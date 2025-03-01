import os
import openai
import requests
import json
from flask import Flask, request, jsonify, session, render_template, redirect, url_for
from flask_session import Session
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default_secret_key")
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
Session(app)

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
# Set your OpenAI API base URL if using DeepSeek API
openai.api_base = os.getenv("OPENAI_API_BASE", "https://api.deepseek.com/v1")
# Groq API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Questions to ask the user
QUESTIONS = [
    "Who is your target audience? (job title, industry, company size, etc.)",
    "What is the key offering, product, or service?",
    "What pain points are you addressing?",
    "What tone or style should the email have? (Formal, Friendly, etc.)",
    "Any special promotions, deadlines, or prior relationships to mention?"
]

# Keys for storing user responses
KEYS = ['audience', 'offering', 'pain_points', 'tone', 'special_notes']

def generate_email_template(user_inputs):
    """Generate a basic email template based on user inputs without using an API."""
    audience = user_inputs.get('audience', 'N/A')
    offering = user_inputs.get('offering', 'N/A')
    pain_points = user_inputs.get('pain_points', 'N/A')
    tone = user_inputs.get('tone', 'Professional')
    special_notes = user_inputs.get('special_notes', 'N/A')
    
    # Create a simple template
    subject = f"Introducing {offering} for {audience}"
    
    intro = f"Dear {audience.split()[0] if ' ' in audience else audience},\n\n"
    intro += f"I hope this email finds you well. I'm reaching out because I understand that {pain_points} can be challenging in your industry.\n\n"
    
    value_prop = f"Our {offering} is specifically designed to address these challenges by providing a solution that helps you overcome {pain_points}.\n\n"
    
    if special_notes != 'N/A':
        value_prop += f"Additionally, {special_notes}\n\n"
    
    cta = "Would you be available for a quick 15-minute call next week to discuss how we can help?\n\n"
    
    sign_off = "Best regards,\n[Your Name]\n[Your Position]\n[Your Company]"
    
    email_body = intro + value_prop + cta + sign_off
    
    return f"Subject: {subject}\n\n{email_body}"

def generate_email_with_groq(user_inputs):
    """Generate an email using Groq API based on user inputs."""
    if not GROQ_API_KEY:
        return None
        
    prompt = f"""
    Create a cold outreach email based on the following information:
    
    Target Audience: {user_inputs.get('audience', 'N/A')}
    Key Offering: {user_inputs.get('offering', 'N/A')}
    Pain Points: {user_inputs.get('pain_points', 'N/A')}
    Tone/Style: {user_inputs.get('tone', 'Professional')}
    Special Notes: {user_inputs.get('special_notes', 'N/A')}
    
    Format the response as follows:
    
    Subject: [Subject Line]
    
    [Email Body with clear Introduction, Value Proposition, Call-to-Action, and Sign-off]
    """
    
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [
                {"role": "system", "content": "You are a professional email copywriter expert in creating effective cold outreach emails."},
                {"role": "user", "content": prompt}
            ],
            "model": "llama3-8b-8192",
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            app.logger.error(f"Groq API Error: {response.text}")
            return None
    except Exception as e:
        app.logger.error(f"Groq API Error: {str(e)}")
        return None

def generate_email(user_inputs):
    """Generate an email using available APIs based on user inputs."""
    # First try DeepSeek
    try:
        response = openai.ChatCompletion.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a professional email copywriter expert in creating effective cold outreach emails."},
                {"role": "user", "content": f"""
                Create a cold outreach email based on the following information:
                
                Target Audience: {user_inputs.get('audience', 'N/A')}
                Key Offering: {user_inputs.get('offering', 'N/A')}
                Pain Points: {user_inputs.get('pain_points', 'N/A')}
                Tone/Style: {user_inputs.get('tone', 'Professional')}
                Special Notes: {user_inputs.get('special_notes', 'N/A')}
                
                Format the response as follows:
                
                Subject: [Subject Line]
                
                [Email Body with clear Introduction, Value Proposition, Call-to-Action, and Sign-off]
                """}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as deepseek_error:
        app.logger.error(f"DeepSeek API Error: {str(deepseek_error)}")
        
        # Try Groq as fallback
        groq_response = generate_email_with_groq(user_inputs)
        if groq_response:
            return groq_response
        
        # If both APIs fail, use the template generator
        error_str = str(deepseek_error).lower()
        if "authentication" in error_str or "api key" in error_str or "auth" in error_str:
            error_message = (
                "⚠️ Authentication Error: API authentication failed.\n\n"
                "Here's a basic email template instead:\n\n"
                f"{generate_email_template(user_inputs)}"
            )
        else:
            error_message = (
                f"⚠️ Error: {str(deepseek_error)}\n\n"
                "Here's a basic email template instead:\n\n"
                f"{generate_email_template(user_inputs)}"
            )
        
        return error_message

def refine_email_with_groq(email, refinement_request):
    """Refine the email using Groq API."""
    if not GROQ_API_KEY:
        return None
        
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [
                {"role": "system", "content": "You are a professional email copywriter expert in refining cold outreach emails."},
                {"role": "user", "content": f"Original email:\n\n{email}\n\nPlease refine this email based on the following request: {refinement_request}"}
            ],
            "model": "llama3-8b-8192",
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            app.logger.error(f"Groq API Error: {response.text}")
            return None
    except Exception as e:
        app.logger.error(f"Groq API Error: {str(e)}")
        return None

def refine_email(email, refinement_request):
    """Refine the generated email based on user feedback."""
    # Check if the email starts with an error message
    if email.startswith("⚠️ Error:") or email.startswith("⚠️ Authentication Error:"):
        # Extract the template part
        template_start = email.find("Here's a basic email template instead:")
        if template_start != -1:
            template_part = email[template_start + len("Here's a basic email template instead:"):]
            email = template_part.strip()
    
    # First try DeepSeek
    try:
        response = openai.ChatCompletion.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a professional email copywriter expert in refining cold outreach emails."},
                {"role": "user", "content": f"Original email:\n\n{email}\n\nPlease refine this email based on the following request: {refinement_request}"}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as deepseek_error:
        app.logger.error(f"DeepSeek API Error in refine_email: {str(deepseek_error)}")
        
        # Try Groq as fallback
        groq_response = refine_email_with_groq(email, refinement_request)
        if groq_response:
            return groq_response
        
        # If both APIs fail, provide a simple response
        if "shorter" in refinement_request.lower():
            return "I've attempted to make the email shorter, but couldn't connect to any available APIs. Please try again later or edit the email manually."
        elif "casual" in refinement_request.lower():
            return "I've attempted to make the email more casual, but couldn't connect to any available APIs. Please try again later or edit the email manually."
        elif "formal" in refinement_request.lower():
            return "I've attempted to make the email more formal, but couldn't connect to any available APIs. Please try again later or edit the email manually."
        else:
            return f"I couldn't refine the email due to API errors. Please try again later or edit the email manually."

@app.route('/')
def index():
    """Render the home page."""
    # Reset session data when starting fresh
    session.clear()
    session['step'] = 0
    session['user_inputs'] = {}
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat interactions."""
    if 'step' not in session:
        session['step'] = 0
    
    if 'user_inputs' not in session:
        session['user_inputs'] = {}
    
    if 'email' not in session:
        session['email'] = None
    
    # Get user message
    data = request.get_json()
    user_message = data.get('message', '').strip()
    
    # Different logic based on the current step
    if session['step'] < len(QUESTIONS):
        # Still collecting initial information
        if session['step'] > 0:  # Store the answer to the previous question
            session['user_inputs'][KEYS[session['step'] - 1]] = user_message
        
        # Get the next question
        question = QUESTIONS[session['step']]
        session['step'] += 1
        
        return jsonify({
            'message': question,
            'is_question': True
        })
    
    elif session['step'] == len(QUESTIONS):
        # Store the answer to the last question
        session['user_inputs'][KEYS[session['step'] - 1]] = user_message
        
        # Generate the email
        email = generate_email(session['user_inputs'])
        session['email'] = email
        session['step'] += 1
        
        return jsonify({
            'message': f"Here's your generated email:\n\n{email}\n\nWould you like to refine it? For example, you can ask for:\n1. A more casual/formal tone\n2. A shorter/longer email\n3. More emphasis on specific benefits\n4. Any other changes",
            'is_question': True,
            'email': email
        })
    
    else:
        # Handle refinement requests
        if user_message.lower() in ['no', 'no thanks', 'it looks good', 'looks good', 'perfect']:
            # User is satisfied with the email
            return jsonify({
                'message': "Great! Feel free to use this email for your outreach. If you want to create a new email, just refresh the page.",
                'is_question': False
            })
        else:
            # User wants refinements
            refined_email = refine_email(session['email'], user_message)
            session['email'] = refined_email
            
            return jsonify({
                'message': f"I've refined your email:\n\n{refined_email}\n\nWould you like to refine it further?",
                'is_question': True,
                'email': refined_email
            })

@app.route('/download', methods=['GET'])
def download():
    """Download the generated email as text."""
    if 'email' in session and session['email']:
        # Remove error messages if present
        email = session['email']
        if email.startswith("⚠️ Error:") or email.startswith("⚠️ Authentication Error:"):
            template_start = email.find("Here's a basic email template instead:")
            if template_start != -1:
                email = email[template_start + len("Here's a basic email template instead:"):].strip()
        
        return jsonify({
            'email': email
        })
    else:
        return jsonify({
            'error': 'No email has been generated yet.'
        }), 400

@app.route('/check-api', methods=['GET'])
def check_api():
    """Check if the APIs are configured correctly."""
    api_status = {
        'deepseek': {'status': 'error', 'message': 'Not configured'},
        'groq': {'status': 'error', 'message': 'Not configured'}
    }
    
    # Check DeepSeek
    if openai.api_key:
        try:
            response = openai.ChatCompletion.create(
                model="deepseek-chat",
                messages=[
                    {"role": "user", "content": "Hello"}
                ],
                max_tokens=5
            )
            api_status['deepseek'] = {'status': 'success', 'message': 'API connection successful'}
        except Exception as e:
            error_str = str(e)
            if "authentication" in error_str.lower() or "api key" in error_str.lower() or "auth" in error_str.lower():
                api_status['deepseek'] = {'status': 'error', 'message': f'Authentication failed: {error_str}'}
            else:
                api_status['deepseek'] = {'status': 'error', 'message': f'API connection failed: {error_str}'}
    
    # Check Groq
    if GROQ_API_KEY:
        try:
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messages": [
                    {"role": "user", "content": "Hello"}
                ],
                "model": "llama3-8b-8192",
                "max_tokens": 5
            }
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload)
            )
            
            if response.status_code == 200:
                api_status['groq'] = {'status': 'success', 'message': 'API connection successful'}
            else:
                api_status['groq'] = {'status': 'error', 'message': f'API connection failed: {response.text}'}
        except Exception as e:
            api_status['groq'] = {'status': 'error', 'message': f'API connection failed: {str(e)}'}
    
    # Determine overall status
    overall_status = 'success' if (api_status['deepseek']['status'] == 'success' or api_status['groq']['status'] == 'success') else 'error'
    
    return jsonify({
        'status': overall_status,
        'message': 'At least one API is working' if overall_status == 'success' else 'All APIs failed',
        'apis': api_status
    })

@app.route('/verify-api', methods=['POST'])
def verify_api():
    """Verify API keys provided by the user."""
    data = request.get_json()
    deepseek_api_key = data.get('deepseek_api_key', '')
    deepseek_api_base = data.get('deepseek_api_base', 'https://api.deepseek.com/v1')
    groq_api_key = data.get('groq_api_key', '')
    
    results = {
        'deepseek': {'status': 'not_tested', 'message': 'API key not provided'},
        'groq': {'status': 'not_tested', 'message': 'API key not provided'},
        'overall': {'status': 'error', 'message': 'No API keys provided'}
    }
    
    # Verify DeepSeek API
    if deepseek_api_key:
        try:
            # Create a temporary OpenAI client to avoid modifying the global one
            import openai as temp_openai
            temp_openai.api_key = deepseek_api_key
            temp_openai.api_base = deepseek_api_base
            
            response = temp_openai.ChatCompletion.create(
                model="deepseek-chat",
                messages=[
                    {"role": "user", "content": "Hello"}
                ],
                max_tokens=5
            )
            results['deepseek'] = {'status': 'success', 'message': 'API connection successful'}
        except Exception as e:
            error_str = str(e)
            if "authentication" in error_str.lower() or "api key" in error_str.lower() or "auth" in error_str.lower():
                results['deepseek'] = {'status': 'error', 'message': f'Authentication failed: {error_str}'}
            else:
                results['deepseek'] = {'status': 'error', 'message': f'API connection failed: {error_str}'}
    
    # Verify Groq API
    if groq_api_key:
        try:
            headers = {
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messages": [
                    {"role": "user", "content": "Hello"}
                ],
                "model": "llama3-8b-8192",
                "max_tokens": 5
            }
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload)
            )
            
            if response.status_code == 200:
                results['groq'] = {'status': 'success', 'message': 'API connection successful'}
            else:
                results['groq'] = {'status': 'error', 'message': f'API connection failed: {response.text}'}
        except Exception as e:
            results['groq'] = {'status': 'error', 'message': f'API connection failed: {str(e)}'}
    
    # Determine overall status
    if results['deepseek']['status'] == 'success' or results['groq']['status'] == 'success':
        results['overall'] = {'status': 'success', 'message': 'At least one API is working'}
    else:
        if deepseek_api_key or groq_api_key:
            results['overall'] = {'status': 'error', 'message': 'All APIs failed to connect'}
    
    return jsonify(results)

@app.route('/update-api-keys', methods=['POST'])
def update_api_keys():
    """Update API keys in the .env file."""
    data = request.get_json()
    deepseek_api_key = data.get('deepseek_api_key', '')
    deepseek_api_base = data.get('deepseek_api_base', 'https://api.deepseek.com/v1')
    groq_api_key = data.get('groq_api_key', '')
    
    # Verify the keys first
    verification_result = verify_api_keys(deepseek_api_key, deepseek_api_base, groq_api_key)
    
    # Only update if at least one key is valid
    if verification_result['overall']['status'] == 'success':
        try:
            # Read current .env file
            env_path = os.path.join(os.path.dirname(__file__), '.env')
            env_exists = os.path.exists(env_path)
            
            if env_exists:
                with open(env_path, 'r') as f:
                    env_lines = f.readlines()
            else:
                env_lines = []
            
            # Process lines to update or add keys
            updated_openai_key = False
            updated_openai_base = False
            updated_groq_key = False
            
            for i, line in enumerate(env_lines):
                if line.startswith('OPENAI_API_KEY=') and deepseek_api_key:
                    env_lines[i] = f'OPENAI_API_KEY={deepseek_api_key}\n'
                    updated_openai_key = True
                elif line.startswith('OPENAI_API_BASE=') and deepseek_api_base:
                    env_lines[i] = f'OPENAI_API_BASE={deepseek_api_base}\n'
                    updated_openai_base = True
                elif line.startswith('GROQ_API_KEY=') and groq_api_key:
                    env_lines[i] = f'GROQ_API_KEY={groq_api_key}\n'
                    updated_groq_key = True
            
            # Add keys that weren't updated
            if not updated_openai_key and deepseek_api_key:
                env_lines.append(f'OPENAI_API_KEY={deepseek_api_key}\n')
            if not updated_openai_base and deepseek_api_base:
                env_lines.append(f'OPENAI_API_BASE={deepseek_api_base}\n')
            if not updated_groq_key and groq_api_key:
                env_lines.append(f'GROQ_API_KEY={groq_api_key}\n')
            
            # Write back to .env file
            with open(env_path, 'w') as f:
                f.writelines(env_lines)
            
            # Update current session
            if deepseek_api_key:
                openai.api_key = deepseek_api_key
            if deepseek_api_base:
                openai.api_base = deepseek_api_base
            if groq_api_key:
                global GROQ_API_KEY
                GROQ_API_KEY = groq_api_key
            
            return jsonify({
                'status': 'success',
                'message': 'API keys updated successfully',
                'verification': verification_result
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Failed to update API keys: {str(e)}',
                'verification': verification_result
            })
    else:
        return jsonify({
            'status': 'error',
            'message': 'No valid API keys provided',
            'verification': verification_result
        })

def verify_api_keys(deepseek_api_key, deepseek_api_base, groq_api_key):
    """Verify API keys without modifying the request object."""
    results = {
        'deepseek': {'status': 'not_tested', 'message': 'API key not provided'},
        'groq': {'status': 'not_tested', 'message': 'API key not provided'},
        'overall': {'status': 'error', 'message': 'No API keys provided'}
    }
    
    # Verify DeepSeek API
    if deepseek_api_key:
        try:
            # Create a temporary OpenAI client to avoid modifying the global one
            import openai as temp_openai
            temp_openai.api_key = deepseek_api_key
            temp_openai.api_base = deepseek_api_base
            
            response = temp_openai.ChatCompletion.create(
                model="deepseek-chat",
                messages=[
                    {"role": "user", "content": "Hello"}
                ],
                max_tokens=5
            )
            results['deepseek'] = {'status': 'success', 'message': 'API connection successful'}
        except Exception as e:
            error_str = str(e)
            if "authentication" in error_str.lower() or "api key" in error_str.lower() or "auth" in error_str.lower():
                results['deepseek'] = {'status': 'error', 'message': f'Authentication failed: {error_str}'}
            else:
                results['deepseek'] = {'status': 'error', 'message': f'API connection failed: {error_str}'}
    
    # Verify Groq API
    if groq_api_key:
        try:
            headers = {
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messages": [
                    {"role": "user", "content": "Hello"}
                ],
                "model": "llama3-8b-8192",
                "max_tokens": 5
            }
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload)
            )
            
            if response.status_code == 200:
                results['groq'] = {'status': 'success', 'message': 'API connection successful'}
            else:
                results['groq'] = {'status': 'error', 'message': f'API connection failed: {response.text}'}
        except Exception as e:
            results['groq'] = {'status': 'error', 'message': f'API connection failed: {str(e)}'}
    
    # Determine overall status
    if results['deepseek']['status'] == 'success' or results['groq']['status'] == 'success':
        results['overall'] = {'status': 'success', 'message': 'At least one API is working'}
    else:
        if deepseek_api_key or groq_api_key:
            results['overall'] = {'status': 'error', 'message': 'All APIs failed to connect'}
    
    return results

if __name__ == '__main__':
    app.run(debug=True)



# AI Cold Email Generator

An AI-powered application that helps you generate personalized cold outreach emails based on your target audience, offering, and other key details.

## Features

- Interactive chat interface to collect information about your email needs
- AI-powered email generation using DeepSeek or Groq LLMs
- Automatic API fallback (tries DeepSeek first, then Groq, then template)
- Fallback template generation when APIs are unavailable
- Ability to refine and customize the generated email
- Copy to clipboard and download functionality
- Secure handling of API keys and sensitive information

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- DeepSeek API key and/or Groq API key

### Installation

1. Clone this repository to your local machine
   ```bash
   git clone <repository-url>
   cd ColdEmailGenerator
   ```

2. Create and activate a virtual environment
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate
   
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the required dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory and add your API keys and a secret key for Flask
   ```
   OPENAI_API_KEY=your_deepseek_api_key_here
   OPENAI_API_BASE=https://api.deepseek.com/v1
   GROQ_API_KEY=your_groq_api_key_here
   SECRET_KEY=your_secret_key_here
   ```
   Note: You can generate a secure random secret key with Python:
   ```python
   import secrets
   print(secrets.token_hex(16))
   ```

### API Configuration

The application uses multiple LLM providers with an automatic fallback mechanism:

1. **DeepSeek API**: Used as the primary API
2. **Groq API**: Used as a fallback if DeepSeek fails
3. **Template Generator**: Used if both APIs fail

You can configure one or both APIs:
- For DeepSeek: Set `OPENAI_API_KEY` and `OPENAI_API_BASE` in your `.env` file
- For Groq: Set `GROQ_API_KEY` in your `.env` file

### Running the Application

1. Make sure your virtual environment is activated
2. Start the Flask application
   ```bash
   python cursor_prompt.py
   ```
3. Open your web browser and go to `http://127.0.0.1:5000`

## Usage

1. The application will ask you a series of questions about your cold email needs:
   - Target audience (job title, industry, company size, etc.)
   - Key offering, product, or service
   - Pain points you're addressing
   - Desired tone or style for the email
   - Any special promotions, deadlines, or prior relationships to mention

2. Based on your responses, the AI will generate a personalized cold outreach email

3. You can request refinements to the generated email by specifying what you'd like to change, such as:
   - "Make it more casual"
   - "Shorten the email"
   - "Add more emphasis on the ROI"
   - "Include a statistic about industry trends"

4. Once you're satisfied with the email, you can copy it to your clipboard or download it as a text file

## Troubleshooting

If you encounter API errors:

1. **Authentication Issues**: Verify your API keys in the `.env` file are correct and have not expired
2. **API Base URL**: Ensure the API base URLs are correct for the services you're using
3. **Model Availability**: Confirm that the models specified in the code are available through your API providers
4. **Fallback Mechanism**: The application will automatically try multiple APIs and fall back to a basic template generator if all APIs fail
5. **API Status**: The application checks API status on startup and displays warnings if there are issues

## Example Interaction

Here's an example of how you might interact with the application:

**User:** *[Starts the application]*

**System:** "Hi there! I'm your AI Cold Email Generator. I'll help you create a personalized cold outreach email. Let me ask you a few questions to get started.

Who is your target audience? (job title, industry, company size, etc.)"

**User:** "Marketing Directors at mid-size SaaS companies with 50-200 employees"

**System:** "What is the key offering, product, or service?"

**User:** "AI-powered content generation platform that creates SEO-optimized blog posts"

**System:** "What pain points are you addressing?"

**User:** "Time-consuming content creation, inconsistent publishing schedule, difficulty ranking on Google"

**System:** "What tone or style should the email have? (Formal, Friendly, etc.)"

**User:** "Professional but conversational"

**System:** "Any special promotions, deadlines, or prior relationships to mention?"

**User:** "14-day free trial with no credit card required, 30% off first 3 months if they sign up this week"

**System:** *[Generates email and displays it]*

**User:** "Make it shorter and add more specifics about the SEO benefits"

**System:** *[Refines the email based on feedback]*


## Acknowledgements

- [DeepSeek](https://deepseek.com/) for providing the LLM API
- [Groq](https://groq.com/) for providing a fast LLM API alternative
- [Flask](https://flask.palletsprojects.com/) for the web framework 


## Created by Sandeep Kumar

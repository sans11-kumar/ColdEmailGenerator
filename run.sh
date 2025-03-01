#!/bin/bash

echo "==================================="
echo "AI Cold Email Generator Setup"
echo "==================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed."
    echo "Please install Python from https://www.python.org/downloads/"
    exit 1
fi

# Check if virtual environment exists, create if it doesn't
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists, prompt creation if it doesn't
if [ ! -f ".env" ]; then
    echo ".env file not found. Creating from template..."
    echo "# OpenAI API Key - Get this from your OpenAI account" > .env
    echo "OPENAI_API_KEY=your_api_key_here" >> .env
    
    echo "# DeepSeek API Base URL" >> .env
    echo "OPENAI_API_BASE=https://api.deepseek.com/v1" >> .env
    
    echo "# Groq API Key - Alternative to DeepSeek" >> .env
    echo "GROQ_API_KEY=your_groq_api_key_here" >> .env
    
    echo "# Flask Secret Key - Used for session encryption" >> .env
    python -c "import secrets; print(f'SECRET_KEY={secrets.token_hex(16)}')" >> .env
    
    echo "Please edit the .env file to add your API keys."
    if command -v nano &> /dev/null; then
        echo "Opening .env file with nano..."
        nano .env
    else
        echo "Please edit the .env file manually to add your API keys."
    fi
fi

echo ""
echo "Note: The application will try to use DeepSeek API first, then Groq API as a fallback."
echo "If both APIs fail, a basic template generator will be used."
echo ""

# Run the application
echo "Starting the application..."
python cursor_prompt.py 
@echo off
echo ===================================
echo AI Cold Email Generator Setup
echo ===================================

REM Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in your PATH.
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b
)

REM Check if virtual environment exists, create if it doesn't
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists, prompt creation if it doesn't
if not exist .env (
    echo .env file not found. Creating from template...
    echo # OpenAI API Key - Get this from your OpenAI account > .env
    echo OPENAI_API_KEY=your_api_key_here >> .env
    
    echo # DeepSeek API Base URL >> .env
    echo OPENAI_API_BASE=https://api.deepseek.com/v1 >> .env
    
    echo # Groq API Key - Alternative to DeepSeek >> .env
    echo GROQ_API_KEY=your_groq_api_key_here >> .env
    
    echo # Flask Secret Key - Used for session encryption >> .env
    python -c "import secrets; print(f'SECRET_KEY={secrets.token_hex(16)}')" >> .env
    
    echo Please edit the .env file to add your API keys.
    echo Opening .env file...
    start notepad .env
    
    echo After saving your API keys, close the text editor and press any key to continue.
    pause
)

echo.
echo Note: The application will try to use DeepSeek API first, then Groq API as a fallback.
echo If both APIs fail, a basic template generator will be used.
echo.

REM Run the application
echo Starting the application...
python cursor_prompt.py
pause 
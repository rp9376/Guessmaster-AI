@echo off
echo Setting up Guessmaster AI...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.11+ and try again
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo pip is not installed
    echo Please install pip and try again
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo Installing Python packages...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install requirements
    pause
    exit /b 1
)

REM Check if .env exists
if not exist .env (
    echo Creating .env file from template...
    copy .env .env.local
    echo Please edit .env file with your Ollama settings
)

REM Run migrations
echo Running database migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    echo Failed to run migrations
    pause
    exit /b 1
)

REM Collect static files
echo Collecting static files...
python manage.py collectstatic --noinput
if %errorlevel% neq 0 (
    echo Failed to collect static files
    pause
    exit /b 1
)

echo.
echo Setup complete!
echo.
echo To start the development server:
echo 1. Make sure Ollama is running with a model (e.g., 'ollama serve' and 'ollama pull llama3')
echo 2. Edit .env file with your Ollama settings
echo 3. Run: python manage.py runserver
echo.
echo The game will be available at: http://localhost:8000
echo.
pause

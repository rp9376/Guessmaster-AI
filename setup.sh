#!/bin/bash

echo "Setting up Guessmaster AI..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed or not in PATH"
    echo "Please install Python 3.11+ and try again"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed"
    echo "Please install pip3 and try again"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing Python packages..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install requirements"
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env .env.local
    echo "Please edit .env file with your Ollama settings"
fi

# Run migrations
echo "Running database migrations..."
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "Failed to run migrations"
    exit 1
fi

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput
if [ $? -ne 0 ]; then
    echo "Failed to collect static files"
    exit 1
fi

echo ""
echo "Setup complete!"
echo ""
echo "To start the development server:"
echo "1. Make sure Ollama is running with a model (e.g., 'ollama serve' and 'ollama pull llama3')"
echo "2. Edit .env file with your Ollama settings"
echo "3. Run: python manage.py runserver"
echo ""
echo "The game will be available at: http://localhost:8000"
echo ""

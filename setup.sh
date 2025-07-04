#!/bin/bash

# GuessMaster 20Q Setup Script
echo "🎯 Setting up GuessMaster 20Q..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    if [ -f ".env.template" ]; then
        echo "📝 Creating .env from template..."
        cp .env.template .env
        echo "⚠️  Please edit .env file and configure your Ollama settings before running the server."
        echo "   Set OLLAMA_URL to point to your Ollama instance."
    else
        echo "❌ Neither .env nor .env.template found. Please create .env with your configuration."
        exit 1
    fi
else
    echo "✅ Environment file found."
fi

echo ""
echo "🚀 Setup complete! To start the server:"
echo "   1. Make sure your Ollama instance is running"
echo "   2. Configure .env with your Ollama URL if not already done"
echo "   3. Run: source venv/bin/activate && python manage.py runserver 9090"
echo "   4. Open: http://localhost:9090"
echo ""
echo "🔗 Your current Ollama configuration:"
echo "   URL: $(grep OLLAMA_URL .env 2>/dev/null || echo 'Not configured')"
echo "   Model: $(grep OLLAMA_MODEL .env 2>/dev/null || echo 'Not configured')"

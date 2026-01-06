#!/bin/bash
# SmartLensOCR Backend Startup Script
# Sets up the environment and starts the backend server

set -e  # Exit on error

echo "🚀 SmartLensOCR Backend Startup"
echo "================================"

# Check Python version
echo "✓ Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "✓ Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "✓ Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠ Warning: .env file not found"
    echo "  Creating .env from .env.example..."
    cp .env.example .env
    echo "  ⚠ Please edit .env and add your GEMINI_API_KEY"
    echo "  Get your key from: https://aistudio.google.com/app/apikey"
fi

# Initialize database
echo "✓ Initializing database..."
python3 -c "from models import init_database; init_database()"

# Start the server
echo ""
echo "🎯 Starting backend server..."
echo "📍 Server running at: http://localhost:8000"
echo "📚 API Docs at:       http://localhost:8000/docs"
echo ""

# Run with auto-reload in development
if [ "$ENVIRONMENT" = "production" ]; then
    uvicorn main:app --host 0.0.0.0 --port 8000
else
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
fi

#!/bin/bash

# Deal Finder - Quick Start Script
# This script starts your Flask deal finder application

echo "════════════════════════════════════════════════════════"
echo "  Starting Deal Finder Application"
echo "════════════════════════════════════════════════════════"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Creating virtual environment..."
    python3 -m venv .venv
    echo "✓ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Check if dependencies are installed
echo "Checking dependencies..."
if ! python -c "import flask" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo "✓ Dependencies installed"
else
    echo "✓ Dependencies already installed"
fi
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "   Please create .env file with your API keys"
    exit 1
fi

# Check if RapidAPI key is configured
if grep -q "RAPIDAPI_KEY=$" .env || grep -q "RAPIDAPI_KEY= $" .env; then
    echo "⚠️  WARNING: RAPIDAPI_KEY not configured in .env"
    echo "   The app will run but won't find real deals"
    echo ""
else
    echo "✓ RapidAPI key configured"
    echo ""
fi

# Start Flask application
echo "════════════════════════════════════════════════════════"
echo "  🚀 Starting Flask Server"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Access the app at: http://localhost:5001/deals"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "════════════════════════════════════════════════════════"
echo ""

cd pra
python app.py

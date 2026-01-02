#!/bin/bash

# Deal Finder Setup Script
# This script sets up the deal finder application

echo "========================================="
echo "  Product Deal Finder Setup"
echo "========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null
then
    echo "❌ pip3 is not installed. Please install pip."
    exit 1
fi

echo "✅ pip3 found"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your API keys before running the app!"
    echo ""
else
    echo "✅ .env file already exists"
    echo ""
fi

# Check if database exists
if [ ! -f "pra/prra.db" ]; then
    echo "🗄️  Database will be created on first run"
else
    echo "✅ Database already exists"
fi
echo ""

echo "========================================="
echo "  Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API keys"
echo "2. Run: source .venv/bin/activate"
echo "3. Run: cd pra && python app.py"
echo "4. Open: http://localhost:5001/deals"
echo ""
echo "API Keys needed:"
echo "  - Google Custom Search API (GOOGLE_API_KEY, GOOGLE_CUSTOM_SEARCH_CX)"
echo "  - Walmart Open API (WALMART_API_KEY)"
echo "  - Best Buy API (BEST_BUY_API_KEY)"
echo "  - Optional: Target API (TARGET_API_KEY)"
echo "  - Optional: Amazon API (AMAZON_API_KEY)"
echo ""
echo "See DEAL_FINDER_README.md for detailed setup instructions."
echo ""

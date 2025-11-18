#!/bin/bash

# ZomatoAI Manager - Startup Script

echo "🍔 Starting ZomatoAI Manager..."
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "   Copy .env.example to .env and add your GEMINI_API_KEY"
    echo ""
fi

# Check if virtual environment exists (optional)
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Run Streamlit
echo "🚀 Starting Streamlit app..."
streamlit run app.py


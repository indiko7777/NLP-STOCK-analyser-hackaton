#!/bin/bash

echo "====================================="
echo "Stock Analyzer Pro"
echo "====================================="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found!"
    echo ""
    echo "Please configure your API keys:"
    echo "1. Edit .env file"
    echo "2. Add your OpenRouter and Alpaca API keys"
    echo ""
    exit 1
fi

# Activate virtual environment
source venv/Scripts/activate

# Start Streamlit
echo "Starting Stock Analyzer..."
echo ""
echo "The app will open in your browser at http://localhost:8501"
echo "Press Ctrl+C to stop the server"
echo ""
streamlit run app.py

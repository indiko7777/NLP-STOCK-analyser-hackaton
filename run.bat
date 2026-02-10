@echo off
echo =====================================
echo Stock Analyzer Pro
echo =====================================
echo.

REM Check if .env exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo.
    echo Please configure your API keys:
    echo 1. Edit .env file
    echo 2. Add your OpenRouter and Alpaca API keys
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start Streamlit
echo Starting Stock Analyzer...
echo.
echo The app will open in your browser at http://localhost:8501
echo Press Ctrl+C to stop the server
echo.
streamlit run app.py

pause

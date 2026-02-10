@echo off
echo =====================================
echo Stock Analyzer Pro
echo =====================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Check if requirements are installed
if not exist "venv\Lib\site-packages\streamlit\" (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
)

REM Check if .env exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please copy .env.example to .env and add your API keys.
    echo.
    pause
    exit /b 1
)

REM Start Streamlit
echo Starting Stock Analyzer...
echo.
streamlit run app.py

pause

@echo off
REM Smart Career Assistant - Quick Start Guide (Windows)
REM This script helps you get started with the redesigned SaaS platform

echo.
echo ================================
echo Launching Smart Career Assistant SaaS
echo ================================
echo.

REM Check Python
echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)
echo OK: Python found
echo.

REM Install dependencies
echo Installing/updating dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo OK: Dependencies installed
echo.

REM Run tests
echo Running integration tests...
python test_integration_saas.py
if errorlevel 1 (
    echo WARNING: Some tests failed - check output above
) else (
    echo OK: All integration tests passed!
)
echo.

REM Start application
echo.
echo ================================
echo Starting application...
echo ================================
echo.
echo The application will be available at: http://localhost:5000
echo.
echo Quick Links:
echo   - Home: http://localhost:5000/
echo   - Resume Upload: http://localhost:5000/resume/upload
echo   - Chatbot (requires login): http://localhost:5000/chatbot/
echo   - API Greeting: http://localhost:5000/api/chat/greeting
echo.
echo Press Ctrl+C to stop the server
echo.
echo.

python app.py

pause

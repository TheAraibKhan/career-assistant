#!/bin/bash
# Smart Career Assistant - Quick Start Guide
# This script helps you get started with the redesigned SaaS platform

echo "================================"
echo "🚀 Smart Career Assistant SaaS"
echo "================================"
echo ""

# Check Python
echo "Checking Python installation..."
python --version
if [ $? -ne 0 ]; then
    echo "❌ Python not found. Please install Python 3.8+"
    exit 1
fi
echo "✅ Python found"
echo ""

# Install dependencies
echo "Installing/updating dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo "✅ Dependencies installed"
echo ""

# Run tests
echo "Running integration tests..."
python test_integration_saas.py
if [ $? -ne 0 ]; then
    echo "⚠️  Some tests failed - check output above"
else
    echo "✅ All integration tests passed!"
fi
echo ""

# Start application
echo ""
echo "================================"
echo "Starting application..."
echo "================================"
echo ""
echo "The application will be available at: http://localhost:5000"
echo ""
echo "Quick Links:"
echo "  • Home: http://localhost:5000/"
echo "  • Resume Upload: http://localhost:5000/resume/upload"
echo "  • Chatbot (requires login): http://localhost:5000/chatbot/"
echo "  • API Greeting: http://localhost:5000/api/chat/greeting"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app.py

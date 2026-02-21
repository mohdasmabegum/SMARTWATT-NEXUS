#!/bin/bash
# SMARTWATT NEXUS - Startup Script for Linux/Mac

echo ""
echo "========================================"
echo "   SMARTWATT NEXUS - Startup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org"
    exit 1
fi

echo "[1/5] Checking Python version..."
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "[2/5] Creating virtual environment..."
    python3 -m venv venv
else
    echo "[2/5] Virtual environment already exists"
fi

# Activate virtual environment
echo "[3/5] Activating virtual environment..."
source venv/bin/activate

# Install requirements (use LIGHT=true to install the lightweight stack)
echo "[4/5] Installing dependencies..."
if [ "$LIGHT" = "true" ] || [ "$LIGHT" = "1" ]; then
    echo "Using lightweight requirements (requirements-light.txt)"
    pip install -q -r requirements-light.txt
else
    pip install -q -r requirements.txt
fi

# Initialize database with sample data
echo "[5/5] Initializing database..."
cd backend
python3 init_data.py

# Run Flask application
echo ""
echo "========================================"
echo "   Starting SMARTWATT NEXUS..."
echo "========================================"
echo ""
echo "Flask app starting at: http://localhost:5000"
echo ""
echo "Test Credentials:"
echo "   Username: demo_user"
echo "   Password: password123"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py

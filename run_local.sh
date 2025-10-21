#!/bin/bash

# Local development server script
# Run this to start the portfolio website locally

echo "Starting local development server..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Initialize database if needed
if [ ! -f "portfolio.db" ]; then
    echo "Initializing database..."
    python3 database.py
fi

# Run Flask development server
echo ""
echo "========================================="
echo "Portfolio website running at:"
echo "http://localhost:5000"
echo "========================================="
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

export FLASK_APP=app.py
export FLASK_ENV=development
python3 -m flask run --host=0.0.0.0 --port=5000

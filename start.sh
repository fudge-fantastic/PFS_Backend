#!/bin/bash

echo "🚀 Starting PixelForge Backend Development Setup..."
echo "=" * 60

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment (Windows)
if [ -f ".venv/Scripts/activate" ]; then
    echo "Activating virtual environment (Windows)..."
    source .venv/Scripts/activate
else
    echo "Activating virtual environment (Unix)..."
    source .venv/bin/activate
fi

# Install dependencies using venv's python explicitly
echo "Installing dependencies..."
PYBIN="python"
if [ -f ".venv/Scripts/python.exe" ]; then
    PYBIN=".venv/Scripts/python.exe"
elif [ -f ".venv/bin/python" ]; then
    PYBIN=".venv/bin/python"
fi

$PYBIN -m pip install -r requirements.txt

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please update .env with your configuration!"
fi

# Initialize database (optional)
read -p "Do you want to initialize the database with sample data? (y/n): " init_db
if [[ $init_db =~ ^[Yy]$ ]]; then
    echo "Initializing database..."
    $PYBIN scripts/init_db.py
fi

# Start the development server
read -p "Do you want to start the development server? (y/n): " start_server
if [[ $start_server =~ ^[Yy]$ ]]; then
    echo "Starting development server..."
    echo "API will be available at: http://localhost:8000"
    echo "Swagger UI: http://localhost:8000/docs"
    echo "ReDoc: http://localhost:8000/redoc"
    $PYBIN run.py
else
    echo "Setup completed! To start the server manually, run: $PYBIN run.py"
fi

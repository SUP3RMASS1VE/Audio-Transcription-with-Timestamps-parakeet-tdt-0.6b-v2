#!/bin/bash

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 could not be found. Please install Python 3."
    exit 1
fi

# Check if virtual environment exists, if not create one
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || source venv/Scripts/activate

# Install PyTorch
echo "Installing PyTorch..."
pip3 install torch torchvision torchaudio

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the app
echo "Starting the application..."
python app.py 
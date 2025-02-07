#!/bin/bash

# Create the virtual environment (if it doesn't exist)
if [ ! -d .venv ]; then
    python3 -m venv .venv
fi

# Activate the virtual environment
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Build the frontend (adjust path)
cd ../frontend
npm install
npm run build

# Go back to backend directory (optional but good practice)
cd ../backend
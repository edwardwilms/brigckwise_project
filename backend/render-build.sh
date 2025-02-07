#!/bin/bash

# Activate the virtual environment
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Build the frontend
cd ../frontend
npm install
npm run build

# Go back to backend directory (optional)
cd backend
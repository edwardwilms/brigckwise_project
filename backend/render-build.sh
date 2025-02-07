#!/bin/bash

# Install system dependencies (locales)
apt-get update
apt-get install -y locales

# Generate the locales you need (e.g., en_US.UTF-8, pt_BR.UTF-8)
locale-gen pt_BR.UTF-8  # Add other locales as needed

# Set the default locale (important)
export LC_ALL="pt_BR.UTF-8" # Or your default locale

# Activate the virtual environment
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Build the frontend
cd ../frontend
npm install
npm run build

# Go back to backend directory (optional but good practice)
cd backend
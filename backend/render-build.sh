#!/bin/bash

# Install system dependencies (locales)
apt-get update
apt-get install -y locales

# Generate the *supported* locale (en_US.UTF-8)
locale-gen en_US.UTF-8

# Set LC_ALL to the *supported* locale (after generation)
export LC_ALL="en_US.UTF-8"

# Create the virtual environment (if it doesn't exist)
if [ ! -d .venv ]; then
    python3 -m venv .venv
fi

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
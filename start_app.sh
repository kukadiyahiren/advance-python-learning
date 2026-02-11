#!/bin/bash
# Check if venv exists
if [ -d "venv" ]; then
    source venv/bin/activate
    python3 app.py
else
    echo "Virtual environment not found! Please run setup first."
    exit 1
fi

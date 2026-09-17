#!/usr/bin/env bash
set -e

echo "=== Initializing EcoAccel-ITAD Environment ==="

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "=== Running EcoAccel-ITAD Diagnostic Pipeline ==="
python main.py

echo "=== Pipeline Execution Completed ==="
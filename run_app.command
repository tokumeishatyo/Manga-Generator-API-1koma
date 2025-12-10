#!/bin/bash

# 1コマ漫画生成アプリ起動スクリプト (macOS/Linux)

cd "$(dirname "$0")"

# Check if venv exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate venv
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r app/requirements.txt --quiet

# Run the app
echo "Starting 1コマ漫画生成アプリ..."
python3 app/main.py

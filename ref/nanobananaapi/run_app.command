#!/bin/bash

# Navigate to the script's directory
cd "$(dirname "$0")"

# Function to find a suitable python
find_python() {
    if command -v /opt/homebrew/bin/python3 &> /dev/null; then
        echo "/opt/homebrew/bin/python3"
    elif command -v /usr/local/bin/python3 &> /dev/null; then
        echo "/usr/local/bin/python3"
    elif command -v python3 &> /dev/null; then
        echo "python3"
    else
        echo ""
    fi
}

PYTHON_CMD=$(find_python)

if [ -z "$PYTHON_CMD" ]; then
    echo "Error: Python 3 not found."
    read -p "Press Enter to close..."
    exit 1
fi

echo "Using Python: $PYTHON_CMD"
$PYTHON_CMD --version

# Delete .venv if it was created by a different Python version/OS
if [ -d ".venv" ]; then
    # Check if .venv is valid
    if [ ! -f ".venv/bin/python" ]; then
        echo "Invalid .venv detected, removing..."
        rm -rf .venv
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment (.venv)..."
    $PYTHON_CMD -m venv .venv
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment."
        read -p "Press Enter to close..."
        exit 1
    fi
fi

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip to suppress warnings and ensure best compatibility
echo "Upgrading pip..."
pip install --upgrade pip -q

# Install dependencies inside the virtual environment
echo "Installing/Updating dependencies..."
pip install -r app/requirements.txt -q

# Run application
echo "Starting 4コマ漫画プロンプト作成ツール (API対応版)..."
echo ""
python app/main.py 2>&1

# Check exit code
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "================================================================"
    echo "アプリがクラッシュしました (終了コード: $EXIT_CODE)"
    echo "================================================================"
    echo ""
    echo "考えられる原因と対処法:"
    echo ""
    echo "1. macOSのシステムPythonを使用している場合:"
    echo "   → Homebrew経由でPythonをインストールしてください"
    echo "      brew install python"
    echo ""
    echo "2. .venvが壊れている場合:"
    echo "   → .venvフォルダを削除して再実行してください"
    echo "      rm -rf .venv"
    echo ""
    echo "3. tkinterがインストールされていない場合:"
    echo "   → Homebrewでpython-tkをインストールしてください"
    echo "      brew install python-tk"
    echo ""
    echo "================================================================"
fi

read -p "Press Enter to close..."

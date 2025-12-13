@echo off
cd /d "%~dp0"

echo Checking for Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in your PATH.
    echo Please install Python 3.11+ from https://www.python.org/
    pause
    exit /b
)

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

echo Activating virtual environment...
call .venv\Scripts\activate

echo Installing dependencies...
pip install --upgrade pip
pip install -r app\requirements.txt

echo Starting 4コマ漫画プロンプト作成ツール (API対応版)...
python app\main.py

pause

@echo off
chcp 65001
cd /d "%~dp0"

REM Check if venv exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate venv
call .venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r app\requirements.txt --quiet

REM Run the app
echo Starting 1コマ漫画生成アプリ...
python app\main.py

pause

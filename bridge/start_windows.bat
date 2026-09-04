@echo off
setlocal
cd /d "%~dp0"
if not exist .venv python -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if "%ROYAL_BRIDGE_TOKEN%"=="" (
  echo Set ROYAL_BRIDGE_TOKEN before starting.
  echo Example: set ROYAL_BRIDGE_TOKEN=change-this-long-random-token
  exit /b 1
)
python main.py

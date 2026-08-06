@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
    echo Virtual environment not found. Run install_windows.bat first.
    pause
    exit /b 1
)

call ".venv\Scripts\activate.bat"

echo Starting ngrok tunnel...
echo Keep run_app.bat running in another window.
python "%~dp0scripts\run_ngrok.py"

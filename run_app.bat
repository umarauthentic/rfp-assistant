@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
    echo Virtual environment not found. Run install_windows.bat first.
    pause
    exit /b 1
)

where ollama >nul 2>nul
if errorlevel 1 (
    echo Ollama was not found. Install Ollama or run install_windows.bat.
    pause
    exit /b 1
)

start "" /min ollama serve
timeout /t 3 /nobreak >nul

call ".venv\Scripts\activate.bat"

echo Starting RFP Assistant...
echo Open http://127.0.0.1:8001 in your browser.
start "" "http://127.0.0.1:8001"
uvicorn app.main:app --host 127.0.0.1 --port 8001

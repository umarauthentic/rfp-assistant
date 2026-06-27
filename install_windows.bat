@echo off
setlocal

cd /d "%~dp0"

echo.
echo === RFP Assistant Windows Installer ===
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found. Trying to install Python 3.12 with winget...
    winget install -e --id Python.Python.3.12 --source winget
    if errorlevel 1 (
        echo Python install failed. Install Python 3.11 or 3.12, then run this installer again.
        pause
        exit /b 1
    )
)

where ollama >nul 2>nul
if errorlevel 1 (
    echo Ollama was not found. Trying to install Ollama with winget...
    winget install -e --id Ollama.Ollama --source winget
    if errorlevel 1 (
        echo Ollama install failed. Install Ollama from https://ollama.com/download, then run this installer again.
        pause
        exit /b 1
    )
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating Python virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo Could not create the Python virtual environment.
        pause
        exit /b 1
    )
)

call ".venv\Scripts\activate.bat"

echo Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo pip upgrade failed.
    pause
    exit /b 1
)

echo Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Dependency installation failed.
    pause
    exit /b 1
)

if not exist ".env" (
    echo Creating .env from .env.example...
    copy ".env.example" ".env" >nul
)

set OLLAMA_MODEL=phi3:mini
for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
    if /i "%%A"=="OLLAMA_MODEL" set OLLAMA_MODEL=%%B
)

echo Starting Ollama if it is not already running...
start "" /min ollama serve
timeout /t 5 /nobreak >nul

echo Pulling Ollama model: %OLLAMA_MODEL%
ollama pull %OLLAMA_MODEL%
if errorlevel 1 (
    echo Could not pull %OLLAMA_MODEL%. Open Ollama and run: ollama pull %OLLAMA_MODEL%
    pause
    exit /b 1
)

echo Building local document index...
python scripts\reingest_documents.py
if errorlevel 1 (
    echo Document indexing failed. You can retry later with reingest_documents.bat.
)

echo.
echo Setup complete.
echo Start the web app with run_app.bat
echo Then open http://127.0.0.1:8001
echo.
pause

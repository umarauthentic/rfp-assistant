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

if exist ".env" (
    for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
        if /i "%%A"=="APP_HOST" if not defined APP_HOST set "APP_HOST=%%B"
        if /i "%%A"=="APP_PORT" if not defined APP_PORT set "APP_PORT=%%B"
    )
)

if not defined APP_HOST set "APP_HOST=0.0.0.0"
if not defined APP_PORT set "APP_PORT=8001"

echo Starting RFP Assistant...
echo Open http://localhost:%APP_PORT% in your browser.
start "" "http://localhost:%APP_PORT%"
uvicorn app.main:app --host %APP_HOST% --port %APP_PORT%

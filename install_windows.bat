@echo off
setlocal

cd /d "%~dp0"

echo.
echo === RFP Assistant Windows Installer ===
echo.

set "TARGET_PYTHON=3.14"

call :find_python

if not "%PYTHON_VERSION%"=="%TARGET_PYTHON%" (
    echo Python %TARGET_PYTHON% was not found. Trying to install Python %TARGET_PYTHON% with winget...
    where winget >nul 2>nul
    if errorlevel 1 (
        echo winget was not found. Install Python %TARGET_PYTHON% manually, then run this installer again.
        pause
        exit /b 1
    )
    winget install -e --id Python.Python.%TARGET_PYTHON% --source winget
    if errorlevel 1 (
        echo Python %TARGET_PYTHON% install failed. Install Python %TARGET_PYTHON% manually, then run this installer again.
        pause
        exit /b 1
    )
    call :find_python
    if not "%PYTHON_VERSION%"=="%TARGET_PYTHON%" (
        echo Python %TARGET_PYTHON% was installed, but it is not available in this command window yet.
        echo Close this window and run install_windows.bat again.
        pause
        exit /b 1
    )
    echo Python %TARGET_PYTHON% installed successfully.
) else (
    for /f "tokens=*" %%V in ('%PYTHON_CMD% --version 2^>^&1') do echo Found %%V
)

where ollama >nul 2>nul
if errorlevel 1 (
    echo Ollama was not found. Trying to install Ollama with winget...
    where winget >nul 2>nul
    if errorlevel 1 (
        echo winget was not found. Install Ollama from https://ollama.com/download, then run this installer again.
        pause
        exit /b 1
    )
    winget install -e --id Ollama.Ollama --source winget
    if errorlevel 1 (
        echo Ollama install failed. Install Ollama from https://ollama.com/download, then run this installer again.
        pause
        exit /b 1
    )
    where ollama >nul 2>nul
    if errorlevel 1 (
        echo Ollama was installed, but it is not available in this command window yet.
        echo Close this window and run install_windows.bat again.
        pause
        exit /b 1
    )
    echo Ollama installed successfully.
) else (
    for /f "tokens=*" %%V in ('ollama --version 2^>^&1') do echo Found %%V
)

set "RECREATE_VENV=0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import sys; raise SystemExit(0 if f'{sys.version_info[0]}.{sys.version_info[1]}' == '%TARGET_PYTHON%' else 1)" >nul 2>nul
    if errorlevel 1 set "RECREATE_VENV=1"
)

if "%RECREATE_VENV%"=="1" (
    echo Existing virtual environment does not use Python %TARGET_PYTHON%. Recreating it...
    rmdir /s /q ".venv"
    if errorlevel 1 (
        echo Could not remove the old Python virtual environment.
        pause
        exit /b 1
    )
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating Python virtual environment...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 (
        echo Could not create the Python virtual environment.
        pause
        exit /b 1
    )
) else (
    echo Python virtual environment already exists.
)

call ".venv\Scripts\activate.bat"

python -m pip --version >nul 2>nul
if errorlevel 1 (
    echo pip was not found in the virtual environment. Installing pip...
    python -m ensurepip --upgrade
    if errorlevel 1 (
        echo pip installation failed.
        pause
        exit /b 1
    )
) else (
    echo pip is already available in the virtual environment.
)

python -m pip show fastapi uvicorn python-dotenv pydantic pydantic-settings sentence-transformers faiss-cpu numpy requests python-docx python-pptx openpyxl pandas python-multipart >nul 2>nul
if errorlevel 1 (
    echo One or more Python dependencies are missing. Installing from requirements.txt...
    python -m pip install --upgrade pip
    if errorlevel 1 (
        echo pip upgrade failed.
        pause
        exit /b 1
    )
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Dependency installation failed.
        pause
        exit /b 1
    )
) else (
    echo Python dependencies are already installed.
)

if not exist ".env" (
    echo Creating .env from .env.example...
    copy ".env.example" ".env" >nul
) else (
    echo .env already exists.
)

set OLLAMA_MODEL=phi3:mini
for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
    if /i "%%A"=="OLLAMA_MODEL" set OLLAMA_MODEL=%%B
)

echo Checking Ollama service...
ollama list >nul 2>nul
if errorlevel 1 (
    echo Starting Ollama...
    start "" /min ollama serve
    timeout /t 5 /nobreak >nul
) else (
    echo Ollama is already running.
)

echo Checking Ollama model: %OLLAMA_MODEL%
ollama list | findstr /i /c:"%OLLAMA_MODEL%" >nul
if errorlevel 1 (
    echo Pulling Ollama model: %OLLAMA_MODEL%
    ollama pull %OLLAMA_MODEL%
    if errorlevel 1 (
        echo Could not pull %OLLAMA_MODEL%. Open Ollama and run: ollama pull %OLLAMA_MODEL%
        pause
        exit /b 1
    )
) else (
    echo Ollama model %OLLAMA_MODEL% is already installed.
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
exit /b 0

:find_python
set "PYTHON_CMD="
set "PYTHON_VERSION="

py -3.14 -c "import venv" >nul 2>nul
if not errorlevel 1 (
    set "PYTHON_CMD=py -3.14"
    set "PYTHON_VERSION=3.14"
    exit /b 0
)

py -3.13 -c "import venv" >nul 2>nul
if not errorlevel 1 (
    set "PYTHON_CMD=py -3.13"
    set "PYTHON_VERSION=3.13"
    exit /b 0
)

py -3.12 -c "import venv" >nul 2>nul
if not errorlevel 1 (
    set "PYTHON_CMD=py -3.12"
    set "PYTHON_VERSION=3.12"
    exit /b 0
)

py -3.11 -c "import venv" >nul 2>nul
if not errorlevel 1 (
    set "PYTHON_CMD=py -3.11"
    set "PYTHON_VERSION=3.11"
    exit /b 0
)

python -c "import sys, venv; raise SystemExit(0 if sys.version_info[:2] in ((3, 11), (3, 12), (3, 13), (3, 14)) else 1)" >nul 2>nul
if not errorlevel 1 (
    set "PYTHON_CMD=python"
    for /f "tokens=*" %%V in ('python -c "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')"') do set "PYTHON_VERSION=%%V"
    exit /b 0
)

exit /b 1

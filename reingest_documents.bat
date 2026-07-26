@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
    echo Virtual environment not found. Run install_windows.bat first.
    pause
    exit /b 1
)

call ".venv\Scripts\activate.bat"
set "PYTHONPATH=%~dp0"
python "%~dp0scripts\reingest_documents.py"
pause

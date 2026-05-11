@echo off
python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
python scripts\add_sample_memory.py
echo Setup complete. Run run_local.bat to start the API.
pause

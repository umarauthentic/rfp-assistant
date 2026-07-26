@echo off
call .venv\Scripts\activate
if not defined APP_HOST set "APP_HOST=0.0.0.0"
if not defined APP_PORT set "APP_PORT=8001"
uvicorn app.main:app --reload --host %APP_HOST% --port %APP_PORT%

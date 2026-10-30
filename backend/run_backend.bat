@echo off
echo Starting AI Multi-Language Transpiler Backend Server...
cd /d "%~dp0"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause

@echo off
title UniversalTranspiler - AI Multi-Language Compiler & Transpiler IDE
echo ======================================================================
echo    Starting UniversalTranspiler (AI Multi-Language Compiler IDE)
echo ======================================================================
echo.

cd /d "%~dp0"

echo [1/2] Launching FastAPI Backend on http://127.0.0.1:8000 ...
start "Transpiler Backend (FastAPI)" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/2] Launching React Vite Frontend on http://localhost:5173 ...
start "Transpiler Frontend (Vite React)" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ======================================================================
echo Both servers have been launched in separate console windows!
echo   - Web IDE:        http://localhost:5173
echo   - Backend Docs:   http://127.0.0.1:8000/docs
echo ======================================================================
pause

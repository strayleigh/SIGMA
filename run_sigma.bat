@echo off
echo ==========================================
echo 🍎 Starting SIGMA Fruit Monitoring System
echo ==========================================

echo 1. Starting Backend Server...
start "SIGMA Backend" cmd /k "cd backend && echo Installing dependencies... && pip install -r requirements.txt && echo Starting Server... && python main.py"

echo 2. Waiting for backend to initialize...
timeout /t 5 >nul

echo 3. Starting Frontend Server...
start "SIGMA Frontend" cmd /k "cd frontend && python -m http.server 3000"

echo 4. Opening Web Browser...
timeout /t 2 >nul
start http://localhost:3000

echo ==========================================
echo ✅ System Started!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo ==========================================
pause

@echo off
echo ================================================
echo  FilmOnDemand - Starting Servers
echo ================================================

echo.
echo [1/3] Installing Python backend dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: pip install failed. Make sure Python and pip are installed.
    pause
    exit /b 1
)

echo.
echo [2/3] Starting FastAPI backend on port 8000...
rem Use cmd /k so the window STAYS OPEN if there is an error
start "FastAPI Backend" cmd /k "uvicorn server.main:app --reload --host 0.0.0.0 --port 8000 & pause"

echo Waiting 3 seconds for backend to start...
timeout /t 3 /nobreak > nul

echo.
echo [3/3] Starting React frontend...
cd FilmOnDemandAPPUI\filmondemand-app

if not exist "node_modules\" (
    echo Installing UI dependencies...
    call npm install
    if %errorlevel% neq 0 (
        echo ERROR: npm install failed. Make sure Node.js is installed.
        pause
        exit /b 1
    )
)

rem Start frontend in this current window
call npm run dev

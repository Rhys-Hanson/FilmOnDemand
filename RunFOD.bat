@echo off
echo ================================================
echo  FilmOnDemand - Starting Servers
echo ================================================

rem Store the project root so backend window always has the right cwd
set PROJECT_ROOT=%~dp0

echo.
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Install Python from https://python.org and check "Add to PATH".
    pause
    exit /b 1
)

echo.
echo [1/3] Installing Python backend dependencies...
pip install -r "%PROJECT_ROOT%requirements.txt"
if %errorlevel% neq 0 (
    echo ERROR: pip install failed.
    pause
    exit /b 1
)

echo.
echo [2/3] Starting FastAPI backend on port 8000...
rem /d sets working directory so uvicorn finds the server package correctly
rem Use "python -m uvicorn" so Windows does not rely on a separate uvicorn.exe being on PATH
start "FastAPI Backend" /d "%PROJECT_ROOT%" cmd /k "python -m uvicorn server.main:app --reload --host 0.0.0.0 --port 8000"

echo Waiting 3 seconds for backend to start...
timeout /t 3 /nobreak > nul

echo.
echo [3/3] Starting React frontend...
cd /d "%PROJECT_ROOT%FilmOnDemandAPPUI\filmondemand-app"

if not exist "node_modules\" (
    echo Installing UI dependencies...
    call npm install
    if %errorlevel% neq 0 (
        echo ERROR: npm install failed. Make sure Node.js is installed from https://nodejs.org
        pause
        exit /b 1
    )
)

rem Start frontend in this current window
call npm run dev

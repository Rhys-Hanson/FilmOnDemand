@echo off
echo Starting FilmOnDemand servers...

echo Starting FastAPI backend on port 8000...
rem Start backend in a completely new, separate command prompt window
start "FastAPI Backend" cmd /c "uvicorn server.main:app --reload --host 0.0.0.0 --port 8000"

echo Starting React frontend...
cd FilmOnDemandAPPUI\filmondemand-app

if not exist "node_modules\" (
    echo Installing UI dependencies...
    call npm install
)

rem Start frontend in this current window
call npm run dev

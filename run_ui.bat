@echo off
cd FilmOnDemandAPPUI\filmondemand-app

if not exist "node_modules\" (
    echo Installing UI dependencies...
    call npm install
)

echo Starting the UI...
call npm run dev

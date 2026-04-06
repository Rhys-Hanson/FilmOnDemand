#!/bin/bash

# Ensure we kill the backend Python server if the user stops this terminal script via Ctrl+C
trap 'echo "Stopping both servers..."; kill $BACKEND_PID 2>/dev/null; exit' INT TERM EXIT

echo "Starting FilmOnDemand servers..."

echo "Starting FastAPI backend on port 8000..."
# Start backend in the background
uvicorn server.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a brief moment to ensure backend starts successfully
sleep 2

echo "Starting React frontend..."
# Navigate to UI
cd FilmOnDemandAPPUI/filmondemand-app

# Install deps if they haven't been installed yet
if [ ! -d "node_modules" ]; then
    echo "Installing UI dependencies..."
    npm install
fi

# Run frontend (this runs continuously in the foreground)
npm run dev

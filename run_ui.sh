#!/bin/bash

# Navigate to the UI directory
cd FilmOnDemandAPPUI/filmondemand-app

# Install dependencies if they haven't been installed yet
if [ ! -d "node_modules" ]; then
    echo "Installing UI dependencies..."
    npm install
fi

# Run the Vite development server
echo "Starting the UI..."
npm run dev

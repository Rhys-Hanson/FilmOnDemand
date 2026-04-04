# FastAPI Web Server Setup Guide

This guide outlines exactly how to build the "Bridge" between your Python APIs and your React frontend using **FastAPI**. 

FastAPI is highly recommended for this project because it is incredibly fast, easy to write, and has built-in support for WebSockets (which we absolutely need for the real-time, Kahoot-style room syncing).

---

## 1. Requirements & Installation

Run this in your terminal to install FastAPI and a local server runner called Uvicorn:
```bash
pip install "fastapi[standard]" uvicorn
```

---

## 2. Recommended Folder Structure

Create a folder called `backend` or just put this in the root of your project:

```text
ACCProject/group-project-group10-1/
├── TasteDiveAPI/
├── TMDbAPI/
├── WatchmodeAPI/
├── FilmOnDemand/        <-- Your main Python wrapper
│   └── main.py
├── filmondemand-app/    <-- React UI
└── server/              <-- NEW FASTAPI FOLDER
    ├── main.py          <-- The main FastAPI app
    └── room_manager.py  <-- Handles the Kahoot-like room logic
```

---

## 3. The Core Server (`server/main.py`)

This file is your server's entry point. It handles the REST API endpoints (like generating the room PIN) and spins up the server.

```python
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import string
from .room_manager import RoomManager

# Initialize your server
app = FastAPI()

# Allow the React frontend to talk to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Change to your React app URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for active rooms
active_rooms = {}
manager = RoomManager()

class RoomSettings(BaseModel):
    genres: list[str]
    streaming_services: list[str]
    year_range: list[int]

# --- REST ENDPOINTS ---

@app.post("/api/rooms/create")
async def create_room():
    """Generates a random 6-character room code."""
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    active_rooms[code] = {
        "players": 0,
        "movies": [],
        "scores": {} # Tracks swipes: {"movie_id_1": 4_likes, "movie_id_2": 1_like}
    }
    # Return the code and the QR Code URL for React to display
    return {
        "room_code": code,
        "qr_url": f"https://yourfrontend.com/join/{code}"
    }

@app.get("/api/rooms/{room_code}")
async def check_room(room_code: str):
    """React calls this when a player types in a code to ensure the room exists."""
    if room_code not in active_rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    return {"status": "valid"}

# --- WEBSOCKETS (REAL-TIME GAMEPLAY) ---

@app.websocket("/ws/rooms/{room_code}/{client_id}")
async def websocket_endpoint(websocket: WebSocket, room_code: str, client_id: str):
    await manager.connect(websocket, room_code)
    try:
        # Notify the host that someone joined
        await manager.broadcast_to_room(room_code, {
            "type": "player_joined", 
            "count": len(manager.rooms[room_code])
        })

        while True:
            # Listen for actions from the players' phones (like Swiping or 'Start Game')
            data = await websocket.receive_json()
            
            if data["action"] == "start_game":
                # TO-DO: Call your FilmOnDemand wrapper here!
                # movies = FilmOnDemand.get_watchmode_movies(...)
                # await manager.broadcast_to_room(room_code, {"type": "game_started", "deck": movies})
                pass
                
            elif data["action"] == "swipe_right":
                movie_id = data["movie_id"]
                active_rooms[room_code]["scores"][movie_id] = active_rooms[room_code]["scores"].get(movie_id, 0) + 1
                
                # Check if everyone matched on this movie
                if active_rooms[room_code]["scores"][movie_id] == len(manager.rooms[room_code]):
                    await manager.broadcast_to_room(room_code, {
                        "type": "match_found",
                        "movie_id": movie_id
                    })

    except WebSocketDisconnect:
        manager.disconnect(websocket, room_code)
        await manager.broadcast_to_room(room_code, {"type": "player_left"})
```

---

## 4. The Room Manager (`server/room_manager.py`)

FastAPI handles WebSockets beautifully, but you need a simple manager class to keep track of which web socket connections belong to which 6-digit room code, so you don't accidentally send movie matches to the wrong group of friends.

```python
from fastapi import WebSocket
from typing import Dict, List

class RoomManager:
    def __init__(self):
        # Maps a room_code to a list of active WebSocket connections
        self.rooms: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_code: str):
        await websocket.accept()
        if room_code not in self.rooms:
            self.rooms[room_code] = []
        self.rooms[room_code].append(websocket)

    def disconnect(self, websocket: WebSocket, room_code: str):
        if room_code in self.rooms:
            self.rooms[room_code].remove(websocket)
            if len(self.rooms[room_code]) == 0:
                del self.rooms[room_code] # Clean up dead rooms

    async def broadcast_to_room(self, room_code: str, message: dict):
        """Send a JSON state update to everyone currently in the specific room."""
        if room_code in self.rooms:
            for connection in self.rooms[room_code]:
                await connection.send_json(message)
```

---

## 5. How to Run Your Server

To spin up your backend and start testing its interaction with React, run:

```bash
cd server
uvicorn main:app --reload
```

Your backend will now be live on `http://127.0.0.1:8000/`. Your React frontend developers can safely begin pointing their API calls out of React and into `http://127.0.0.1:8000/api/rooms/create`.

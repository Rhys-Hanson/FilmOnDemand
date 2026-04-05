from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import string
from .room_manager import RoomManager
from .mock_data import MOCK_MOVIES
from FilmOnDemand.main import FilmOnDemand
import json

USE_MOCK_DATA = True
app = FastAPI()

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
    genres: list[str] = []
    streaming_services: list[str] = []
    year_range: list[int] = []
    actors: list[str] = []
    movies: list[str] = []

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
    return {
        "room_code": code,
        "qr_url": f"https://yourfrontend.com/join/{code}"
    }

@app.get("/api/rooms/{room_code}")
async def check_room(room_code: str):
    """Verify room exists."""
    if room_code not in active_rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    return {"status": "valid"}

# --- WEBSOCKETS (REAL-TIME GAMEPLAY) ---

@app.websocket("/ws/rooms/{room_code}/{client_id}")
async def websocket_endpoint(websocket: WebSocket, room_code: str, client_id: str):
    await manager.connect(websocket, room_code)
    try:
        await manager.broadcast_to_room(room_code, {
            "type": "player_joined", 
            "count": len(manager.rooms[room_code])
        })

        while True:
            data = await websocket.receive_json()
            
            if data["action"] == "start_game":
                if USE_MOCK_DATA:
                    deck = MOCK_MOVIES
                else:
                    engine = FilmOnDemand()
                    deck = engine.run_movie_pull(json.dumps(data))
                    
                await manager.broadcast_to_room(room_code, {"type": "game_started", "deck": deck})
                
            elif data["action"] == "swipe_right":
                movie_id = data["movie_id"]
                active_rooms[room_code]["scores"][movie_id] = active_rooms[room_code]["scores"].get(movie_id, 0) + 1
                
                if active_rooms[room_code]["scores"][movie_id] == len(manager.rooms[room_code]):
                    await manager.broadcast_to_room(room_code, {
                        "type": "match_found",
                        "movie_id": movie_id
                    })

    except WebSocketDisconnect:
        manager.disconnect(websocket, room_code)
        await manager.broadcast_to_room(room_code, {"type": "player_left"})

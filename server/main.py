from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import string
from .room_manager import RoomManager
from .mock_data import MOCK_MOVIES
from .game_state import GameState
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
active_rooms = {
    "000000": {
        "players": 0,
        "movies": [],
        "scores": {} 
    }
}
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

        # Special "Test Mode": Auto-start game for room 000000
        if room_code == "000000":
            if "game_state" not in active_rooms[room_code]:
                active_rooms[room_code]["game_state"] = GameState(room_code, 1) # Support single player test
            await websocket.send_json({"type": "game_started", "deck": MOCK_MOVIES})

        while True:
            data = await websocket.receive_json()
            
            if data["action"] == "start_game":
                if USE_MOCK_DATA:
                    deck = MOCK_MOVIES
                else:
                    from FilmOnDemand.main import FilmOnDemand
                    engine = FilmOnDemand()
                    deck = engine.run_movie_pull(json.dumps(data))
                    
                # Create the game state to formally track progression
                player_count = len(manager.rooms[room_code])
                active_rooms[room_code]["game_state"] = GameState(room_code, player_count)
                    
                await manager.broadcast_to_room(room_code, {"type": "game_started", "deck": deck})
                
            elif data["action"] == "swipe_right":
                movie_id = data["movie_id"]
                game_state = active_rooms[room_code].get("game_state")
                
                if game_state:
                    game_state.register_swipe(movie_id, liked=True)
                    
                    # Unanimous match detection during gameplay
                    if game_state.scores[movie_id] == game_state.total_players:
                        await manager.broadcast_to_room(room_code, {
                            "type": "match_found",
                            "movie_id": movie_id
                        })
                        
            elif data["action"] == "player_finished":
                game_state = active_rooms[room_code].get("game_state")
                
                if game_state:
                    game_state.player_finished_deck()
                    
                    # If this was the last player, game over!
                    if game_state.is_game_over():
                        final_scores = game_state.get_final_results()
                        await manager.broadcast_to_room(room_code, {
                            "type": "game_over",
                            "scores": final_scores
                        })

    except WebSocketDisconnect:
        manager.disconnect(websocket, room_code)
        
        remaining = len(manager.rooms.get(room_code, []))
        
        # Clean up active_rooms entry if the room is now completely empty
        if remaining == 0 and room_code in active_rooms:
            del active_rooms[room_code]
            return  # Nothing left to broadcast to
        
        await manager.broadcast_to_room(room_code, {
            "type": "player_left",
            "count": remaining
        })
        
        # If a game is in progress, reduce expected player count so the game
        # can still reach game_over without waiting for the disconnected player.
        game_state = active_rooms.get(room_code, {}).get("game_state")
        if game_state and game_state.total_players > 1:
            game_state.total_players -= 1
            # If that decrement tips us over the finish line, end the game now
            if game_state.is_game_over():
                final_scores = game_state.get_final_results()
                await manager.broadcast_to_room(room_code, {
                    "type": "game_over",
                    "scores": final_scores
                })

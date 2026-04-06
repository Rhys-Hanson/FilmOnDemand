from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import random
import string
from .room_manager import RoomManager
from .mock_data import MOCK_MOVIES
from .game_state import GameState
from .filter_options import load_watchmode_filter_data, search_actor_names, search_movie_titles
from .movie_service import build_deck

USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "false").lower() == "true"
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
        "scores": {},
        "clients": set(),
        "deck": []
    }
}
manager = RoomManager()

class RoomSettings(BaseModel):
    genres: list[str] = []
    services: list[str] = []
    actors: list[str] = []
    movies: list[str] = []


class StartGameRequest(BaseModel):
    action: str = "start_game"
    filters: RoomSettings


class ActorSearchResponse(BaseModel):
    actors: list[str]


class MovieSearchResponse(BaseModel):
    movies: list[str]

# --- REST ENDPOINTS ---

@app.post("/api/rooms/create")
async def create_room():
    """Generates a random 6-character room code."""
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    active_rooms[code] = {
        "players": 0,
        "movies": [],
        "scores": {}, # Tracks swipes: {"movie_id_1": 4_likes, "movie_id_2": 1_like}
        "clients": set(),
        "deck": []
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


@app.get("/api/options/filter-data")
async def get_filter_data():
    return load_watchmode_filter_data()


@app.get("/api/options/actors", response_model=ActorSearchResponse)
async def get_actor_options(q: str = "", limit: int = 12):
    capped_limit = max(1, min(limit, 20))
    return {"actors": search_actor_names(q, capped_limit)}


@app.get("/api/options/movies", response_model=MovieSearchResponse)
async def get_movie_options(q: str = "", limit: int = 12):
    capped_limit = max(1, min(limit, 20))
    try:
        return {"movies": search_movie_titles(q, capped_limit)}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to fetch movie suggestions: {exc}") from exc


@app.post("/api/rooms/{room_code}/start")
async def start_room_game(room_code: str, request: StartGameRequest):
    """Build a recommendation deck for a room using live FilmOnDemand data."""
    if room_code not in active_rooms:
        raise HTTPException(status_code=404, detail="Room not found")

    try:
        deck = MOCK_MOVIES if USE_MOCK_DATA else build_deck(request.filters.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to build movie deck: {exc}") from exc

    return {"type": "game_started", "deck": deck}

# --- WEBSOCKETS (REAL-TIME GAMEPLAY) ---

@app.websocket("/ws/rooms/{room_code}/{client_id}")
async def websocket_endpoint(websocket: WebSocket, room_code: str, client_id: str):
    await manager.connect(websocket, room_code)
    try:
        is_new_player = client_id not in active_rooms[room_code]["clients"]
        if is_new_player:
            active_rooms[room_code]["clients"].add(client_id)
            game_state = active_rooms.get(room_code, {}).get("game_state")
            if game_state:
                game_state.total_players += 1

        game_state = active_rooms.get(room_code, {}).get("game_state")
        if game_state and active_rooms.get(room_code, {}).get("deck"):
            if game_state.is_game_over():
                final = game_state.get_final_results()
                await websocket.send_json({
                    "type": "game_over",
                    "scores": final["scores"],
                    "super_likes": final["super_likes"],
                    "seen_counts": final["seen_counts"],
                    "unanimous": final["unanimous"],
                })
            else:
                # A game is already in progress. Sync this specific connection directly into it.
                await websocket.send_json({
                    "type": "game_state_sync",
                    "deck": active_rooms[room_code]["deck"]
                })
        else:
            # We are in the lobby. Broadcast new socket count to everyone.
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
                try:
                    deck = MOCK_MOVIES if USE_MOCK_DATA else build_deck(data.get("filters", {}))
                except Exception as exc:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Failed to build movie deck: {exc}"
                    })
                    continue
                    
                active_rooms[room_code]["deck"] = deck

                # Create the game state to formally track progression
                player_count = len(active_rooms[room_code]["clients"])
                active_rooms[room_code]["game_state"] = GameState(room_code, player_count)
                    
                await manager.broadcast_to_room(room_code, {"type": "game_started", "deck": deck})
                
            elif data["action"] == "swipe_right":
                movie_id = data["movie_id"]
                game_state = active_rooms[room_code].get("game_state")
                
                if game_state:
                    game_state.register_swipe(movie_id, liked=True)
                    
                    # Unanimous detection: everyone has now liked this movie
                    if game_state.likes[movie_id] >= game_state.total_players:
                        await manager.broadcast_to_room(room_code, {
                            "type": "match_found",
                            "movie_id": movie_id
                        })

            elif data["action"] == "swipe_left":
                movie_id = data["movie_id"]
                game_state = active_rooms[room_code].get("game_state")
                if game_state:
                    game_state.register_swipe(movie_id, liked=False)

            elif data["action"] == "seen_it":
                movie_id = data["movie_id"]
                game_state = active_rooms[room_code].get("game_state")
                if game_state:
                    game_state.register_seen(movie_id)

            elif data["action"] == "super_like":
                movie_id = data["movie_id"]
                game_state = active_rooms[room_code].get("game_state")
                
                if game_state:
                    game_state.register_super_like(movie_id)
                    
                    # Super-like also counts for unanimous detection
                    if game_state.likes[movie_id] >= game_state.total_players:
                        await manager.broadcast_to_room(room_code, {
                            "type": "match_found",
                            "movie_id": movie_id
                        })
                        
            elif data["action"] == "player_finished":
                game_state = active_rooms[room_code].get("game_state")
                
                if game_state:
                    game_state.player_finished_deck()
                    
                    if game_state.is_game_over():
                        final = game_state.get_final_results()
                        await manager.broadcast_to_room(room_code, {
                            "type": "game_over",
                            "scores": final["scores"],
                            "super_likes": final["super_likes"],
                            "seen_counts": final["seen_counts"],
                            "unanimous": final["unanimous"],
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
                final = game_state.get_final_results()
                await manager.broadcast_to_room(room_code, {
                    "type": "game_over",
                    "scores": final["scores"],
                    "super_likes": final["super_likes"],
                    "seen_counts": final["seen_counts"],
                    "unanimous": final["unanimous"],
                })

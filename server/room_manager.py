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
            if websocket in self.rooms[room_code]:
                self.rooms[room_code].remove(websocket)
            if len(self.rooms[room_code]) == 0:
                del self.rooms[room_code] # Clean up dead rooms

    async def broadcast_to_room(self, room_code: str, message: dict):
        """Send a JSON state update to everyone currently in the specific room."""
        if room_code in self.rooms:
            for connection in list(self.rooms[room_code]):
                try:
                    await connection.send_json(message)
                except Exception:
                    self.disconnect(connection, room_code)

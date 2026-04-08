import asyncio
import websockets
import json

async def test():
    uri = "ws://localhost:8000/ws/rooms/000000/tester123"
    async with websockets.connect(uri) as websocket:
        # Wait for "game_started" if test mode
        msg = await websocket.recv()
        print("Received: ", msg)
        
        # Then send start_game
        data = {
            "action": "start_game",
            "filters": {
                "genres": ["Horror", "Action"],
                "services": ["Netflix"],
                "actors": ["tom cruise"],
                "yearRange": [1990, 2024],
            }
        }
        await websocket.send(json.dumps(data))
        print("Sent start_game")
        
        try:
            msg = await websocket.recv()
            print("Received after start_game: ", msg)
        except Exception as e:
            print("Error recv: ", e)

asyncio.run(test())

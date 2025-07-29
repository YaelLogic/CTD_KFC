import asyncio
import websockets
import json

async def play_game():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        # קבלת מצב לוח ראשוני
        state = await websocket.recv()
        print("Game state:", state)

        # שליחת מהלך לדוגמה
        move = {
            "type": "move",
            "from": [0, 1],
            "to": [2, 1]
        }
        await websocket.send(json.dumps(move))

        # קבלת אישור מהשרת
        response = await websocket.recv()
        print("Server response:", response)

asyncio.run(play_game())

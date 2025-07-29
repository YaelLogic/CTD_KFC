import asyncio
import websockets
import json

def print_board(state):
    board = json.loads(state).get("board", [])
    print("\nCurrent Board State:")
    for piece in board:
        print(f"{piece['type']} ({piece['side']}) at ({piece['row']}, {piece['col']})")

async def play_game():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        # קבלת צבע השחקן והמתנה לשחקן נוסף
        init_data = json.loads(await websocket.recv())
        if init_data["type"] == "wait":
            print(init_data["message"])
            while True:
                init_data = json.loads(await websocket.recv())
                if init_data["type"] == "init":
                    break

        player_color = init_data["color"]
        print(f"You are playing as {'White' if player_color == 'W' else 'Black'}.")
        print_board(json.dumps({"board": init_data["board"]}))

        while True:
            # קבלת מהלך מהמשתמש
            frm = input("Enter the starting position (row,col): ")
            to = input("Enter the target position (row,col): ")

            try:
                frm = [int(x) for x in frm.split(",")]
                to = [int(x) for x in to.split(",")]
            except ValueError:
                print("Invalid input. Please enter positions as row,col.")
                continue

            move = {
                "type": "move",
                "from": frm,
                "to": to
            }
            await websocket.send(json.dumps(move))

            # קבלת אישור מהשרת
            response = json.loads(await websocket.recv())
            if response["type"] == "error":
                print("Error:", response["message"])
                continue

            print("Server response: Move accepted.")

            # קבלת מצב לוח מעודכן
            state = await websocket.recv()
            print_board(state)

asyncio.run(play_game())

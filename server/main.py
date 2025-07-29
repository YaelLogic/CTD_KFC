import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import asyncio, json, websockets, time
from KFC_Py.GameFactory import create_game
from core.board import Board
from core.command import Command
from KFC_Py.img import Img
# ────────────────────────────── הגדרות
PORT    = 8765
TICK_MS = 200          # שידור מצב כל 0.2 שנייה

# ────────────────────────────── אתחול לוח‑משחק
# משתמשים ב‑GameFactory שמובנה לך כדי לקבל Game מוכן
GAME_ASSETS = Path("pieces")                  # עדכני לנתיב האמיתי אצלך
game = create_game(str(GAME_ASSETS), img_factory=Img().read)

clients = {}

# פונקציית עזר – הופכת את הלוח למילון‑JSON פשוט
def board_to_json(b: Board) -> list[dict]:
    out = []
    for p in b.pieces:
        row, col = p.current_cell()
        out.append({
            "id":    p.id,
            "type":  p.__class__.__name__,
            "row":   row,
            "col":   col,
            "side":  'W' if p.id.endswith('W') else 'B'
        })
    return out

# ────────────────────────────── WebSocket handlers
async def handle(ws):
    if len(clients) >= 2:
        await ws.send(json.dumps({"type": "error", "message": "Game is full."}))
        return

    # Assign color to the player
    color = "W" if len(clients) == 0 else "B"
    clients[ws] = color

    try:
        # Wait until both players are connected
        if len(clients) < 2:
            await ws.send(json.dumps({"type": "wait", "message": "Waiting for another player..."}))
            while len(clients) < 2:
                await asyncio.sleep(1)

        # Send initial state and player color
        await ws.send(json.dumps({
            "type": "init",
            "color": color,
            "board": board_to_json(game.board)
        }))

        async for msg in ws:
            data = json.loads(msg)

            if data["type"] == "move":
                frm = tuple(data["from"])
                to = tuple(data["to"])

                # Validate move based on player color
                piece = game.board.get_piece_at(frm)
                if not piece or (piece.id.endswith("W") and color != "W") or (piece.id.endswith("B") and color != "B"):
                    await ws.send(json.dumps({"type": "error", "message": "Invalid move for your color."}))
                    continue

                # Process the move
                cmd = Command(
                    timestamp=int(time.time() * 1000),
                    piece_id=piece.id,
                    type="move",
                    params=[frm, to]
                )
                game._process_input(cmd)
                await ws.send(json.dumps({"type": "ack", "ok": True}))

    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Client disconnected: {e}")

    finally:
        # Remove the client from the list
        if ws in clients:
            del clients[ws]

async def broadcaster():
    while True:
        state = json.dumps({
            "type": "state",
            "board": board_to_json(game.board)
        })
        to_remove = []
        for c in list(clients):
            if c.closed:
                to_remove.append(c)
                continue
            try:
                await c.send(state)
            except websockets.exceptions.ConnectionClosedError:
                to_remove.append(c)

        # Remove closed clients
        for c in to_remove:
            if c in clients:
                del clients[c]

        await asyncio.sleep(TICK_MS / 1000)

async def main():
    async with websockets.serve(handle, "0.0.0.0", PORT):
        print(f"🚀  WS server on ws://localhost:{PORT}")
        await broadcaster()

if __name__ == "__main__":
    asyncio.run(main())

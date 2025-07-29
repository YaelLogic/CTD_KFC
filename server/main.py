import asyncio, json, websockets
from KFC_Py.GameFactory import create_game
from core.board import Board
from core.command import Command
from KFC_Py.img import Img
from pathlib import Path
# ────────────────────────────── הגדרות
PORT    = 8765
TICK_MS = 200          # שידור מצב כל 0.2 שנייה

# ────────────────────────────── אתחול לוח‑משחק
# משתמשים ב‑GameFactory שמובנה לך כדי לקבל Game מוכן
GAME_ASSETS = Path("pieces")                  # עדכני לנתיב האמיתי אצלך
game = create_game(str(GAME_ASSETS), img_factory=Img().read)

clients = set()

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
    clients.add(ws)
    try:
        await ws.send(json.dumps({
            "type": "state",
            "board": board_to_json(game.board)   # מצב‑לוח מלא
        }))

        async for msg in ws:
            data = json.loads(msg)

            if data["type"] == "move":
                frm = tuple(data["from"])   # [row,col]  →  (row,col)
                to  = tuple(data["to"])

                # שולחים פקודה למשחק; Game.on_command מחזיר Bool
                ok = game.on_command(Command(frm, to))   # ⬅️ הפונקציה קיימת אצלך
                await ws.send(json.dumps(
                    {"type": "ack", "ok": ok}
                ))
    finally:
        clients.remove(ws)

async def broadcaster():
    while True:
        state = json.dumps({
            "type": "state",
            "board": board_to_json(game.board)
        })
        await asyncio.gather(*(c.send(state) for c in list(clients) if not c.closed))
        await asyncio.sleep(TICK_MS/1000)

async def main():
    async with websockets.serve(handle, "0.0.0.0", PORT):
        print(f"🚀  WS server on ws://localhost:{PORT}")
        await broadcaster()

if __name__ == "__main__":
    asyncio.run(main())

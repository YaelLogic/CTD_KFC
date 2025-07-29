import pathlib
from core.board import Board
from core.game import Game
from core.piece_factory import PieceFactory
try:
    from GameDisplay import GameDisplay              # קיים בסביבת GUI
except ModuleNotFoundError:
    # אין צורך ב‑GUI בצד השרת, אז יוצרים תחליף ריק
    class GameDisplay:                               # noqa: N801 – שומר על השם
        def __init__(self, *_, **__):                # קולט כל פרמטר ומתעלם
            pass

        def create_canvas(self):
            return None

CELL_PX = 64


def create_game(pieces_root: str | pathlib.Path, img_factory) -> Game:
    """Build a *Game* from the on-disk asset hierarchy rooted at *pieces_root*.

    This reads *board.csv* located inside *pieces_root*, creates a blank board
    (or loads board.png if present), instantiates every piece via PieceFactory
    and returns a ready-to-run *Game* instance.
    """
    pieces_root = pathlib.Path(pieces_root)
    board_csv = pieces_root /  "board.csv"
    if not board_csv.exists():
        raise FileNotFoundError(board_csv)

    # Board image: use board.png beside this file if present, else blank RGBA
    board_png = pieces_root / "board.png"
    if not board_png.exists():
        raise FileNotFoundError(board_png)

    loader = img_factory

    board_img = loader(board_png, (CELL_PX*8, CELL_PX*8), keep_aspect=False)

    board = Board(CELL_PX, CELL_PX, 8, 8, board_img)

    from KFC_Py.GraphicsFactory import GraphicsFactory
    gfx_factory = GraphicsFactory(img_factory)
    pf = PieceFactory(board, pieces_root, graphics_factory=gfx_factory)

    pieces = []
    with board_csv.open() as f:
        for r, line in enumerate(f):
            for c, code in enumerate(line.strip().split(",")):
                if code:
                    pieces.append(pf.create_piece(code, (r, c)))

    game = Game(pieces, board)
    board.pieces = pieces  # הוספת הכלים כמאפיין של הלוח

    display = GameDisplay(           # ⬅️ שולחים את‑game כולו
    game,
    sidebar_w = 230,
    margin    = (20,20,20,20),
    bg_color  = (193,157,122)
)
    
    game.display = display             # אופציונלי – אם תרצי לגשת מה‑Game
    return game
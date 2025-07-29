

import logging
from GameFactory import create_game
from GraphicsFactory import ImgFactory


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    game = create_game("../pieces", ImgFactory())
    def print_scores(_=None):
        print(f"White Score: {game.score_observer_1.get_score()} | Black Score: {game.score_observer_2.get_score()}")
    # הדפסה ראשונית
    print_scores()
    # הדפסה אוטומטית בכל שינוי ניקוד
    game.score_observer_1.add_listener(print_scores)
    game.score_observer_2.add_listener(print_scores)
    def print_moves(_=None):
        print("White Moves:")
        for i, move in enumerate(game.move_history_1.get_history(), 1):
            print(f"{i}. {move['piece']} {move['from']} -> {move['to']} @ {move['time']}")
        print("Black Moves:")
        for i, move in enumerate(game.move_history_2.get_history(), 1):
            print(f"{i}. {move['piece']} {move['from']} -> {move['to']} @ {move['time']}")
        print("-"*40)
    # הדפסה אוטומטית של היסטוריית מהלכים
    game.move_history_1.add_listener(print_moves)
    game.move_history_2.add_listener(print_moves)
    game.run()


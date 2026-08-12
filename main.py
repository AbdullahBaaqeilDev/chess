from engine import ChessEngine
from audio import AudioController
from ui import UIController

def main():
    STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    app = UIController()
    engine = ChessEngine(fen=STARTING_FEN)
    audio = AudioController()

    app.engine = engine
    app.audio = audio

    app.run()

if __name__ == "__main__":
    main()
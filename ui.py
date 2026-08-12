import pygame
import sys
import os
from engine import ChessEngine
from models import MoveFlag
from audio import AudioController

WIDTH, HEIGHT = 640, 640
SQ_SIZE = HEIGHT // 8

class UIController:
    def __init__(self, engine: ChessEngine|None = None, audio: AudioController|None = None):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Modular Chess Engine")
        
        self.engine = engine
        self.audio = audio
        
        self.images = {}
        self.load_images()
        
        self.selected_sq = None
        self.valid_moves = []

        self.legal_moves_surf = pygame.Surface((8 * SQ_SIZE, 8 * SQ_SIZE), flags = pygame.SRCALPHA)
        self.legal_moves_surf.set_alpha(127)
        
    def load_images(self):
        pieces = ["wp", "wr", "wn", "wb", "wq", "wk", "bp", "br", "bn", "bb", "bq", "bk"]
        for p in pieces:
            path = f"assets/images/pieces/{p}.png"
            if os.path.exists(path):
                img = pygame.image.load(path)
                self.images[p[-1].upper() if p[0] == "w" else p[-1]] = pygame.transform.smoothscale(img, (SQ_SIZE, SQ_SIZE))

    def clear_legal_moves_surf(self):
        self.legal_moves_surf.fill((0, 0, 0, 0))

    def run(self):
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(pygame.mouse.get_pos())

            self.draw_game_state()
            clock.tick(30)

    def handle_click(self, pos):
        c, r = pos[0] // SQ_SIZE, pos[1] // SQ_SIZE
        
        # If a square is already selected, check if this click is a valid move
        if self.selected_sq:
            move = next((m for m in self.valid_moves if m.target_sq == (r, c)), None)
            if move:
                if move.flags & MoveFlag.PROMOTION:
                    move.promotion_choice = self.show_promotion_ui(move.piece_moved.isupper())
                
                self.engine.play_move(move)
                self.audio.play_for_move(move)
                
                self.selected_sq = None
                self.valid_moves = []
                self.clear_legal_moves_surf()
                return

        # Select a new square
        piece = self.engine.board.get_piece(r, c)
        if piece and piece.isupper() == self.engine.white_to_move:
            self.clear_legal_moves_surf()
            self.selected_sq = (r, c)
            # Ask the engine for legal moves specifically for this piece
            all_legal = self.engine.get_legal_moves()
            self.valid_moves = [m for m in all_legal if m.start_sq == (r, c)]
        else:
            self.selected_sq = None
            self.valid_moves = []
            self.clear_legal_moves_surf()

    def show_promotion_ui(self, is_white: bool) -> str:
        """Pauses the game, overlays 4 choices, and returns the selected piece."""
        # TODO: Halt and wait for input here.
        choices = ['Q', 'R', 'B', 'N'] if is_white else ['q', 'r', 'b', 'n']
        # Default to Queen.
        return choices[0] 

    def draw_game_state(self):
        # Draw Board
        for r in range(8):
            for c in range(8):
                color = (240, 217, 181) if (r + c) % 2 == 0 else (181, 136, 99)
                pygame.draw.rect(self.screen, color, (c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

        # Draw Pieces
        for r in range(8):
            for c in range(8):
                piece = self.engine.board.get_piece(r, c)
                if piece and piece in self.images:
                    self.screen.blit(self.images[piece], pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

        # Draw Legal Move Hints (Subtle Red)
        if self.selected_sq:
            for move in self.valid_moves:
                tr, tc = move.target_sq
                pygame.draw.circle(
                    self.legal_moves_surf, (255, 255, 255), 
                    (tc * SQ_SIZE + SQ_SIZE//2, tr * SQ_SIZE + SQ_SIZE//2), 
                    SQ_SIZE//6)

        self.screen.blit(self.legal_moves_surf, (0, 0))
        pygame.display.flip()

if __name__ == "__main__":
    app = UIController()
    app.run()
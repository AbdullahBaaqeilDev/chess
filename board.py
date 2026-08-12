class Board:
    def __init__(self):
        self.grid = [["" for _ in range(8)] for _ in range(8)]
        self.piece_locations = {piece: set() for piece in "PNBRQKpnbrqk"}

    def place_piece(self, piece: str, r: int, c: int):
        self.grid[r][c] = piece
        if piece:
            self.piece_locations[piece].add((r, c))

    def remove_piece(self, r: int, c: int) -> str:
        piece = self.grid[r][c]
        if piece:
            self.grid[r][c] = ""
            self.piece_locations[piece].discard((r, c))
        return piece

    def move_piece(self, start_r: int, start_c: int, end_r: int, end_c: int) -> str:
        piece = self.remove_piece(start_r, start_c)
        captured = self.remove_piece(end_r, end_c)
        self.place_piece(piece, end_r, end_c)
        return captured

    def get_piece(self, r: int, c: int) -> str:
        if 0 <= r < 8 and 0 <= c < 8:
            return self.grid[r][c]
        return ""

    def is_empty(self, r: int, c: int) -> bool:
        return self.get_piece(r, c) == ""

    def get_king_pos(self, is_white: bool):
        king = "K" if is_white else "k"
        locations = self.piece_locations[king]
        return next(iter(locations)) if locations else None

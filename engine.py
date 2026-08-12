from models import Move, MoveFlag
from board import Board
from typing import List, Tuple, Optional

class ChessEngine:
    def __init__(self, fen: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
        self.board = Board()
        self.white_to_move = True
        self.castling_rights = {"K": False, "Q": False, "k": False, "q": False}
        self.en_passant_target: Optional[Tuple[int, int]] = None
        self.move_history: List[Move] = []
        
        self.load_fen(fen)

    def load_fen(self, fen: str):
        parts = fen.split(" ")
        ranks = parts[0].split("/")
        
        # 1. Piece Placement
        for r, rank in enumerate(ranks):
            c = 0
            for char in rank:
                if char.isdigit():
                    c += int(char)
                else:
                    self.board.place_piece(char, r, c)
                    c += 1
        
        # 2. Side to move
        self.white_to_move = (parts[1] == 'w')
        
        # 3. Castling
        if parts[2] != "-":
            for char in parts[2]:
                if char in self.castling_rights:
                    self.castling_rights[char] = True
                    
        # 4. En Passant
        if parts[3] != "-":
            col = ord(parts[3][0]) - ord('a')
            row = 8 - int(parts[3][1])
            self.en_passant_target = (row, col)

    def play_move(self, move: Move, update_status: bool = True):
        """Applies a move to the board."""
        r1, c1 = move.start_sq
        r2, c2 = move.target_sq

        # Save current state into move for undo_move
        move.prev_en_passant = self.en_passant_target
        move.prev_castling_rights = self.castling_rights.copy()

        # En Passant Capture
        if move.flags & MoveFlag.EN_PASSANT:
            ep_row = r1
            move.piece_captured = self.board.remove_piece(ep_row, c2)
        else:
            move.piece_captured = self.board.get_piece(r2, c2)

        # Standard Move
        self.board.move_piece(r1, c1, r2, c2)

        # Promotion
        if move.flags & MoveFlag.PROMOTION and move.promotion_choice:
            self.board.remove_piece(r2, c2)
            self.board.place_piece(move.promotion_choice, r2, c2)

        # Castling Rook Movement
        if move.flags & MoveFlag.CASTLE_KINGSIDE:
            self.board.move_piece(r2, 7, r2, c2 - 1)
        elif move.flags & MoveFlag.CASTLE_QUEENSIDE:
            self.board.move_piece(r2, 0, r2, c2 + 1)

        # Update En Passant Target
        if move.flags & MoveFlag.PAWN_DOUBLE:
            self.en_passant_target = ((r1 + r2) // 2, c1)
        else:
            self.en_passant_target = None

        # Update Castling Rights
        self._update_castling_rights(move)

        # Switch Turn
        self.white_to_move = not self.white_to_move
        self.move_history.append(move)

        # Check for Check/Checkmate/Stalemate ONLY when committing real UI moves
        if update_status:
            if self.is_in_check(self.white_to_move):
                move.flags |= MoveFlag.CHECK
                if not self.get_legal_moves():
                    move.flags |= MoveFlag.CHECKMATE
            elif not self.get_legal_moves():
                move.flags |= MoveFlag.STALEMATE

    def undo_move(self):
        """Reverts the last played move."""
        if not self.move_history:
            return

        move = self.move_history.pop()
        r1, c1 = move.start_sq
        r2, c2 = move.target_sq

        # Restore turn and state variables
        self.white_to_move = not self.white_to_move
        self.en_passant_target = move.prev_en_passant
        self.castling_rights = move.prev_castling_rights

        # Undo Castling Rook Move
        if move.flags & MoveFlag.CASTLE_KINGSIDE:
            self.board.move_piece(r2, c2 - 1, r2, 7)
        elif move.flags & MoveFlag.CASTLE_QUEENSIDE:
            self.board.move_piece(r2, c2 + 1, r2, 0)

        # Undo Piece Movement & Promotion
        self.board.remove_piece(r2, c2)
        self.board.place_piece(move.piece_moved, r1, c1)

        # Restore Captured Piece
        if move.flags & MoveFlag.EN_PASSANT:
            ep_row = r1
            self.board.place_piece(move.piece_captured, ep_row, c2)
        elif move.piece_captured:
            self.board.place_piece(move.piece_captured, r2, c2)

    def get_legal_moves(self) -> List[Move]:
        """Generates legal moves by playing and unmaking pseudo-legal moves on self."""
        pseudo_moves = self._get_pseudo_legal_moves(self.white_to_move)
        legal_moves = []

        for move in pseudo_moves:
            # Play move without triggering game status checks to avoid recursion
            self.play_move(move, update_status=False)
            
            # Since turn was toggled in play_move, verify if the player who JUST moved is in check
            if not self.is_in_check(not self.white_to_move):
                legal_moves.append(move)
                
            self.undo_move()

        return legal_moves

    def is_in_check(self, is_white: bool) -> bool:
        king_pos = self.board.get_king_pos(is_white)
        if not king_pos:
            return False
        return self._is_square_attacked(king_pos[0], king_pos[1], not is_white)

    def _update_castling_rights(self, move: Move):
        p = move.piece_moved
        if p == 'K':
            self.castling_rights['K'] = self.castling_rights['Q'] = False
        elif p == 'k':
            self.castling_rights['k'] = self.castling_rights['q'] = False
        elif p == 'R':
            if move.start_sq == (7, 7): self.castling_rights['K'] = False
            elif move.start_sq == (7, 0): self.castling_rights['Q'] = False
        elif p == 'r':
            if move.start_sq == (0, 7): self.castling_rights['k'] = False
            elif move.start_sq == (0, 0): self.castling_rights['q'] = False

    def _get_pseudo_legal_moves(self, is_white: bool) -> List[Move]:
        moves = []
        for r in range(8):
            for c in range(8):
                piece = self.board.get_piece(r, c)
                if piece and piece.isupper() == is_white:
                    moves.extend(self._get_piece_moves(r, c, piece))
        return moves

    def _get_piece_moves(self, r: int, c: int, piece: str) -> List[Move]:
        moves = []
        p_type = piece.lower()
        is_white = piece.isupper()

        # Pawns
        if p_type == 'p':
            direction = -1 if is_white else 1
            start_rank = 6 if is_white else 1
            promo_rank = 0 if is_white else 7

            # Forward Step
            nr = r + direction
            if 0 <= nr < 8 and self.board.is_empty(nr, c):
                if nr == promo_rank:
                    for choice in (['Q', 'R', 'B', 'N'] if is_white else ['q', 'r', 'b', 'n']):
                        moves.append(Move((r, c), (nr, c), piece, flags=MoveFlag.PROMOTION, promotion_choice=choice))
                else:
                    moves.append(Move((r, c), (nr, c), piece, flags=MoveFlag.NORMAL))

                # Double Step
                nnr = r + 2 * direction
                if r == start_rank and self.board.is_empty(nnr, c):
                    moves.append(Move((r, c), (nnr, c), piece, flags=MoveFlag.PAWN_DOUBLE))

            # Captures & En Passant
            for dc in [-1, 1]:
                nc = c + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    target = self.board.get_piece(nr, nc)
                    if target and target.isupper() != is_white:
                        if nr == promo_rank:
                            for choice in (['Q', 'R', 'B', 'N'] if is_white else ['q', 'r', 'b', 'n']):
                                moves.append(Move((r, c), (nr, nc), piece, target, flags=MoveFlag.PROMOTION | MoveFlag.CAPTURE, promotion_choice=choice))
                        else:
                            moves.append(Move((r, c), (nr, nc), piece, target, flags=MoveFlag.CAPTURE))
                    elif (nr, nc) == self.en_passant_target:
                        moves.append(Move((r, c), (nr, nc), piece, flags=MoveFlag.EN_PASSANT | MoveFlag.CAPTURE))

        # Knights, Bishops, Rooks, Queens, Kings
        else:
            offsets = {
                'n': [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)],
                'b': [(-1, -1), (-1, 1), (1, -1), (1, 1)],
                'r': [(-1, 0), (1, 0), (0, -1), (0, 1)],
                'q': [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)],
                'k': [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]
            }
            is_sliding = p_type in ['b', 'r', 'q']

            for dr, dc in offsets[p_type]:
                nr, nc = r + dr, c + dc
                while 0 <= nr < 8 and 0 <= nc < 8:
                    target = self.board.get_piece(nr, nc)
                    if not target:
                        moves.append(Move((r, c), (nr, nc), piece))
                    elif target.isupper() != is_white:
                        moves.append(Move((r, c), (nr, nc), piece, target, flags=MoveFlag.CAPTURE))
                        break
                    else:
                        break  # Blocked by own piece
                    if not is_sliding:
                        break
                    nr += dr
                    nc += dc

        return moves

    def _is_square_attacked(self, r: int, c: int, by_white: bool) -> bool:
        """Determines if a square is under attack by a given side."""
        for row in range(8):
            for col in range(8):
                p = self.board.get_piece(row, col)
                if p and p.isupper() == by_white:
                    # Check if any pseudo-legal move hits (r, c)
                    for move in self._get_piece_moves(row, col, p):
                        if move.target_sq == (r, c):
                            return True
        return False
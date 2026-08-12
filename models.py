from enum import Flag, auto
from dataclasses import dataclass, field
from typing import Optional, Tuple, Dict

class MoveFlag(Flag):
    NORMAL = auto()
    CAPTURE = auto()
    CHECK = auto()
    CHECKMATE = auto()
    STALEMATE = auto()
    CASTLE_KINGSIDE = auto()
    CASTLE_QUEENSIDE = auto()
    EN_PASSANT = auto()
    PROMOTION = auto()
    PAWN_DOUBLE = auto()

@dataclass
class Move:
    start_sq: Tuple[int, int]  # (row, col)
    target_sq: Tuple[int, int]
    piece_moved: str
    piece_captured: str = ""
    flags: MoveFlag = MoveFlag.NORMAL
    promotion_choice: Optional[str] = None  # e.g. 'Q', 'R', 'B', 'N'

    # State tracking for undo operations
    prev_en_passant: Optional[Tuple[int, int]] = None
    prev_castling_rights: Dict[str, bool] = field(default_factory=dict)

    def __eq__(self, other):
        if not isinstance(other, Move):
            return False
        return self.start_sq == other.start_sq and self.target_sq == other.target_sq
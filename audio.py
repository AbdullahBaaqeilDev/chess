import pygame
from models import MoveFlag

class AudioController:
    def __init__(self):
        # pygame.mixer.init()
        # Load real sounds here in practice
        self.sounds = {
            "move": pygame.mixer.Sound("assets/audio/sfx/move.wav"),
            "capture": pygame.mixer.Sound("assets/audio/sfx/capture.wav"),
            "check": pygame.mixer.Sound("assets/audio/sfx/check.wav"),
            "checkmate": pygame.mixer.Sound("assets/audio/sfx/checkmate.wav"),
            "promote": pygame.mixer.Sound("assets/audio/sfx/promote.wav")
        }

    def play_for_move(self, move):
        if move.flags & MoveFlag.CHECKMATE:
            self._play("checkmate")
        elif move.flags & MoveFlag.CHECK:
            self._play("check")
        elif move.flags & MoveFlag.PROMOTION:
            self._play("promote")
        elif move.flags & MoveFlag.CAPTURE or move.flags & MoveFlag.EN_PASSANT:
            self._play("capture")
        else:
            self._play("move")

    def _play(self, sound_key):
        # print(f"[AUDIO] Playing sound: {sound_key}.wav")
        if self.sounds[sound_key]: self.sounds[sound_key].play()
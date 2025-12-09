"""
music.py
מערכת נפרדת שמנגנת מוזיקת רקע בלולאה.
"""

import os
import pygame


BASE_DIR = os.path.dirname(__file__)
SOUND_DIR = os.path.join(BASE_DIR, "sound")


def play_background_music():
    """Play background music (safe path handling)."""
    try:
        pygame.mixer.init()
    except Exception:
        pass

    fname = os.path.join(SOUND_DIR, "age of war eurobeat no copyright.mp3")
    if not os.path.exists(fname):
        return
    try:
        pygame.mixer.music.load(fname)
        pygame.mixer.music.set_volume(0.6)
        pygame.mixer.music.play(-1)
    except Exception:
        pass

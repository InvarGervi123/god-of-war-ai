"""
music.py
מערכת נפרדת שמנגנת מוזיקת רקע בלולאה.
"""

import pygame

def start_music():
    """
    מפעיל מוזיקת רקע בלופ אינסופי.
    """

    pygame.mixer.init()

    # 🔽 תשנה כאן לשם הקובץ שלך 🔽
    pygame.mixer.music.load("sound/age of war eurobeat no copyright.mp3")

    # ניגון בלופ: -1 אומר אינסוף
    pygame.mixer.music.play(-1)

    # ווליום (0 עד 1)
    pygame.mixer.music.set_volume(0.6)

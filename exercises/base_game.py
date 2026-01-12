# exercises/base_game.py

import tkinter as tk
import pygame
import os
from .feedback import FeedbackAnimation


class BaseGame:
    def __init__(self, root, profile, on_finish, save_profile_func, game_key):
        self.root = root
        self.profile = profile
        self.on_finish = on_finish
        self.save_profile = save_profile_func
        self.game_key = game_key  # "math", "memory" и т.д.

        # Инициализация pygame.mixer (если ещё не запущен)
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # Загрузка ОБЩИХ звуков
        self.sound_correct = self.load_sound("assets/sounds/correct.wav")
        self.sound_wrong = self.load_sound("assets/sounds/wrong.wav")
        self.sound_flip = self.load_sound("assets/sounds/flip.wav")

        # Глобальный переключатель звука
        self.sound_enabled = True

        # Общие настройки
        self.MAX_ROUND_TIME = 60
        self.PENALTY_SCORE = 7
        self.PENALTY_TIME = 2
        self.CORRECT_STREAK_FOR_LEVEL_UP = 5
        self.WRONG_STREAK_FOR_LEVEL_DOWN = 4

    def load_sound(self, path):
        """Загружает звук, если файл существует"""
        try:
            return pygame.mixer.Sound(path) if os.path.exists(path) else None
        except:
            return None

    def play_sound(self, sound):
        """Воспроизводит звук, если включён звук"""
        if self.sound_enabled and sound:
            sound.play()

    def toggle_sound(self):
        """Переключает глобальный звук"""
        self.sound_enabled = not self.sound_enabled

    def apply_penalty(self, current_score, current_time):
        """Применяет штраф за ошибку"""
        new_score = max(0, current_score - self.PENALTY_SCORE)
        new_time = max(0, current_time - self.PENALTY_TIME)
        return new_score, new_time

    def update_level_by_streak(self, level, correct_in_row, wrong_in_row):
        """Обновляет уровень по серии правильных/неправильных ответов"""
        new_level = level
        new_correct = correct_in_row
        new_wrong = wrong_in_row

        if correct_in_row >= self.CORRECT_STREAK_FOR_LEVEL_UP:
            new_level = min(10, level + 1)
            new_correct = 0
        elif wrong_in_row >= self.WRONG_STREAK_FOR_LEVEL_DOWN and level > 1:
            new_level = max(1, level - 1)
            new_wrong = 0

        return new_level, new_correct, new_wrong

    def load_background_music(self, music_file):
        """Загружает фоновую музыку для конкретной игры"""
        if os.path.exists(music_file):
            try:
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(0.25)
                pygame.mixer.music.play(-1)  # бесконечно
                return True
            except:
                return False
        return False

    def stop_background_music(self):
        """Останавливает фоновую музыку"""
        pygame.mixer.music.stop()
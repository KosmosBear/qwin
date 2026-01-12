# exercises/memory_game.py
import tkinter as tk
from tkinter import messagebox
import random
import os
from PIL import Image, ImageTk
import pygame

pygame.mixer.init()

CARD_WIDTH, CARD_HEIGHT = 120, 160
CARD_BACK_COLOR = "#5DADE2"
BACKGROUND_COLOR = "#F5F5F5"
ROUND_TIME = 60


class MemoryGame:
    def __init__(self, root, profile, on_finish, save_profile_func):
        self.root = root
        self.profile = profile
        self.on_finish = on_finish
        self.save_profile = save_profile_func
        self.ex_data = profile["exercises"]["memory"]
        self.level = self.ex_data["level"]
        self.score = self.ex_data["score"]
        self.correct_pairs = 0
        self.total_pairs = 0
        self.successful_rounds = self.ex_data.get("successful_rounds", 0)
        self.failed_rounds_in_row = self.ex_data.get("failed_rounds_in_row", 0)
        self.cards = []
        self.flipped = []
        self.matched = set()
        self.card_images = {}
        self.round_time_left = ROUND_TIME
        self.running = True
        self.sound_enabled = True

        # Звуки
        self.sound_flip = self.load_sound("assets/sounds/flip.wav")
        self.sound_match = self.load_sound("assets/sounds/match.wav")
        self.sound_wrong = self.load_sound("assets/sounds/wrong.wav") or self.load_sound("assets/sounds/time_up.wav")

        # Фоновая музыка
        if os.path.exists("assets/sounds/background.mp3"):
            try:
                pygame.mixer.music.load("assets/sounds/background.mp3")
                pygame.mixer.music.set_volume(0.25)
                pygame.mixer.music.play(-1)
            except:
                pass

        self.setup_ui()
        self.update_timer()

    def load_sound(self, path):
        return pygame.mixer.Sound(path) if os.path.exists(path) else None

    def play_sound(self, sound):
        if self.sound_enabled and sound:
            sound.play()

    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        self.sound_btn.config(text="🔇 Выкл" if not self.sound_enabled else "🔊 Вкл")
        if os.path.exists("assets/sounds/background.mp3"):
            if self.sound_enabled:
                pygame.mixer.music.unpause()
            else:
                pygame.mixer.music.pause()

    def setup_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.config(bg=BACKGROUND_COLOR)

        tk.Label(
            self.root,
            text=f"🧠 Память | Уровень: {self.level}",
            font=("Arial", 16, "bold"),
            bg=BACKGROUND_COLOR
        ).pack(pady=5)

        top_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR)
        top_frame.pack()
        self.timer_label = tk.Label(top_frame, text=f"Время: {self.round_time_left}", bg=BACKGROUND_COLOR)
        self.timer_label.pack(side=tk.LEFT, padx=10)
        self.score_label = tk.Label(top_frame, text=f"Очки: {self.score}", bg=BACKGROUND_COLOR, fg="#27AE60")
        self.score_label.pack(side=tk.LEFT)

        self.sound_btn = tk.Button(self.root, text="🔊 Вкл", command=self.toggle_sound, width=8)
        self.sound_btn.pack(pady=5)

        self.cards_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR)
        self.cards_frame.pack(pady=10)

        tk.Button(self.root, text="← Назад", command=self.go_back, bg="#E74C3C", fg="white").pack(pady=10)

        self.prepare_game()

        # Автоматически подстроить размер окна под содержимое
        self.root.update_idletasks()
        width = self.root.winfo_reqwidth()
        height = self.root.winfo_reqheight()
        self.root.geometry(f"{max(width, 420)}x{min(height + 20, 800)}")
    def go_back(self):
        self.running = False
        pygame.mixer.music.stop()
        self.save_progress()
        self.on_finish()

    def prepare_game(self):
        pairs = 3 + self.level
        self.total_pairs = pairs
        symbols = list(range(1, pairs + 1)) * 2
        random.shuffle(symbols)

        self.card_images = {}
        for i in range(1, pairs + 1):
            path = f"assets/cards/card{i}.png"
            try:
                img = Image.open(path)
                img = img.resize((CARD_WIDTH, CARD_HEIGHT), Image.Resampling.LANCZOS)
                self.card_images[i] = ImageTk.PhotoImage(img)
            except:
                self.card_images[i] = None

        for card in self.cards:
            card['canvas'].destroy()
        self.cards.clear()
        self.matched.clear()
        self.flipped.clear()

        cols = min(5, len(symbols) // 2 + 1)
        for idx, symbol in enumerate(symbols):
            canvas = tk.Canvas(self.cards_frame, width=CARD_WIDTH, height=CARD_HEIGHT, bg=CARD_BACK_COLOR,
                               highlightthickness=0, cursor="hand2")
            canvas.grid(row=idx // cols, column=idx % cols, padx=5, pady=5)
            self.cards.append({'canvas': canvas, 'symbol': symbol, 'is_flipped': False})
            canvas.bind("<Button-1>", lambda e, i=idx: self.flip_card(i))

        self.show_all_cards()
        self.root.after(5000, self.hide_all_cards)

    def show_all_cards(self):
        for idx, card in enumerate(self.cards):
            c = card['canvas']
            c.delete("all")
            if self.card_images.get(card['symbol']):
                c.image = self.card_images[card['symbol']]
                c.create_image(0, 0, anchor=tk.NW, image=c.image)
            else:
                c.create_text(CARD_WIDTH // 2, CARD_HEIGHT // 2, text=str(card['symbol']), font=("Arial", 20))
            self.cards[idx]['is_flipped'] = True

    def hide_all_cards(self):
        for idx, card in enumerate(self.cards):
            c = card['canvas']
            c.delete("all")
            c.create_rectangle(0, 0, CARD_WIDTH, CARD_HEIGHT, fill=CARD_BACK_COLOR, outline="black")
            c.create_text(CARD_WIDTH // 2, CARD_HEIGHT // 2, text="?", font=("Arial", 20), fill="white")
            self.cards[idx]['is_flipped'] = False

    def flip_card(self, index):
        if not self.running or index in self.matched or self.cards[index]['is_flipped'] or len(self.flipped) >= 2:
            return

        self.play_sound(self.sound_flip)
        card = self.cards[index]
        c = card['canvas']
        c.delete("all")
        if self.card_images.get(card['symbol']):
            c.image = self.card_images[card['symbol']]
            c.create_image(0, 0, anchor=tk.NW, image=c.image)
        else:
            c.create_text(CARD_WIDTH // 2, CARD_HEIGHT // 2, text=str(card['symbol']), font=("Arial", 20))
        self.cards[index]['is_flipped'] = True
        self.flipped.append(index)

        if len(self.flipped) == 2:
            self.root.after(800, self.check_match)

    def check_match(self):
        if len(self.flipped) != 2:
            return
        i1, i2 = self.flipped
        if self.cards[i1]['symbol'] == self.cards[i2]['symbol']:
            self.play_sound(self.sound_match)
            self.matched.update([i1, i2])
            self.correct_pairs += 1
            self.score += 20
            self.score_label.config(text=f"Очки: {self.score}")
            self.flipped.clear()
            if self.correct_pairs == self.total_pairs:
                self.level_up()
        else:
            self.play_sound(self.sound_wrong)
            self.score = max(0, self.score - 5)
            self.round_time_left = max(0, self.round_time_left - 2)
            self.score_label.config(text=f"Очки: {self.score}")
            self.timer_label.config(text=f"Время: {self.round_time_left}")
            self.root.after(800, self.hide_mismatched)

    def hide_mismatched(self):
        if len(self.flipped) == 2:
            i1, i2 = self.flipped
            self.hide_card(i1)
            self.hide_card(i2)
            self.flipped.clear()
        if self.round_time_left <= 0:
            self.finish_round()

    def hide_card(self, index):
        c = self.cards[index]['canvas']
        c.delete("all")
        c.create_rectangle(0, 0, CARD_WIDTH, CARD_HEIGHT, fill=CARD_BACK_COLOR, outline="black")
        c.create_text(CARD_WIDTH // 2, CARD_HEIGHT // 2, text="?", font=("Arial", 20), fill="white")
        self.cards[index]['is_flipped'] = False

    def level_up(self):
        self.successful_rounds += 1
        self.failed_rounds_in_row = 0
        if self.successful_rounds >= 2:
            self.level = min(10, self.level + 1)
            self.successful_rounds = 0
            messagebox.showinfo("Уровень повышен!", f"Теперь уровень: {self.level}")
        self.prepare_game()

    def update_timer(self):
        if self.running and self.round_time_left > 0:
            self.round_time_left -= 1
            self.timer_label.config(text=f"Время: {self.round_time_left}")
            self.root.after(1000, self.update_timer)
        elif self.running:
            self.finish_round()

    def finish_round(self):
        self.running = False
        pygame.mixer.music.stop()

        self.failed_rounds_in_row += 1
        self.successful_rounds = 0

        if self.failed_rounds_in_row >= 2 and self.level > 1:
            self.level -= 1
            self.failed_rounds_in_row = 0
            messagebox.showinfo("Уровень понижен", f"Сложность снижена. Уровень: {self.level}")

        messagebox.showinfo("Время вышло!", f"Счёт: {self.score}\nУровень: {self.level}")
        self.save_progress()
        self.on_finish()

    def save_progress(self):
        self.profile["exercises"]["memory"].update({
            "level": self.level,
            "score": self.score,
            "successful_rounds": self.successful_rounds,
            "failed_rounds_in_row": self.failed_rounds_in_row
        })
        self.save_profile(self.profile)
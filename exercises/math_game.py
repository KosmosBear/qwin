import tkinter as #учеба кооммис
from tkinter import messagebox
import random
import time
from .base_game import BaseGame
from .feedback import FeedbackAnimation  # ← ЭТА СТРОКА ОБЯЗАТЕЛЬНА!

MIN_TIME_PER_PROBLEM = 6
BASE_TIME_PER_PROBLEM = 10


class MathExercise(BaseGame):
    def __init__(self, root, profile, on_finish, save_profile_func):
        super().__init__(root, profile, on_finish, save_profile_func, "math")

        self.ex_data = profile["exercises"]["math"]
        self.level = self.ex_data["level"]
        self.score = self.ex_data["score"]
        self.correct_in_row = self.ex_data.get("correct_in_row", 0)
        self.wrong_in_row = self.ex_data.get("wrong_in_row", 0)
        self.round_time_left = self.MAX_ROUND_TIME
        self.running = True
        self.answer_buttons = []
        self.locked = False
        self.problem_start_time = None
        self.total_problem_time = self._get_time_for_level()
        self.problem_timer_id = None

        # Фоновая музыка для математики
        self.load_background_music("assets/sounds/background/math.mp3")

        self.setup_ui()

    def _get_time_for_level(self):
        t = BASE_TIME_PER_PROBLEM - (self.level - 1)
        return max(MIN_TIME_PER_PROBLEM, t)

    def setup_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Заголовок с уровнем
        self.label_title = tk.Label(
            self.root,
            text=f"🔢 Математика | Уровень: {self.level}",
            font=("Arial", 16, "bold")
        )
        self.label_title.pack(pady=5)

        # Таймер и счёт
        self.label_round_time = tk.Label(self.root, text=f"Раунд: {self.round_time_left} сек", font=("Arial", 14))
        self.label_round_time.pack(pady=3)
        self.label_score = tk.Label(self.root, text=f"Очки: {self.score}", font=("Arial", 14))
        self.label_score.pack(pady=3)

        # Пример
        self.label_problem = tk.Label(self.root, text="", font=("Arial", 20))
        self.label_problem.pack(pady=10)

        # Полоса времени
        self.time_bar = tk.Canvas(self.root, width=300, height=8, bg="#e0e0e0", highlightthickness=0)
        self.time_bar.pack(pady=5)
        self.time_bar_rect = self.time_bar.create_rectangle(0, 0, 300, 8, fill="#4CAF50")

        # Кнопки ответов
        self.answers_frame = tk.Frame(self.root)
        self.answers_frame.pack(pady=10)

        # Кнопка назад
        tk.Button(self.root, text="← Назад", command=self.go_back).pack(pady=10)

        self.generate_problem()
        self.update_round_timer()

    def go_back(self):
        self.cancel_problem_timer()
        self.stop_background_music()
        self.save_progress()
        self.running = False
        self.on_finish()

    def cancel_problem_timer(self):
        if self.problem_timer_id:
            self.root.after_cancel(self.problem_timer_id)
            self.problem_timer_id = None

    def generate_problem(self):
        if not self.running or self.locked:
            return


        self.cancel_problem_timer()
        self.locked = False
        self.total_problem_time = self._get_time_for_level()
        self.problem_start_time = time.time()

        # Генерация примера (как раньше)
        level = self.level
        if level == 1:
            a, b = random.randint(1, 20), random.randint(1, 20)
            op = random.choice(["+", "-"])
            if op == "-" and a < b: a, b = b, a
            expr, answer = f"{a} {op} {b}", eval(f"{a} {op} {b}")
        elif level == 2:
            nums = [random.randint(1, 15) for _ in range(random.randint(3, 4))]
            ops = [random.choice(["+", "-"]) for _ in range(len(nums) - 1)]
            expr = str(nums[0])
            for i in range(1, len(nums)): expr += f" {ops[i - 1]} {nums[i]}"
            answer = eval(expr)
        elif level == 3:
            a, b = random.randint(2, 12), random.randint(2, 12)
            op = random.choice(["*", "/"])
            if op == "/":
                a = a * b
                expr, answer = f"{a} / {b}", a // b
            else:
                expr, answer = f"{a} * {b}", a * b
        else:
            a = random.randint(10, 50)
            b = random.randint(2, 10)
            c = random.randint(1, 10)
            op1 = random.choice(["+", "-", "*"])
            op2 = random.choice(["+", "-"])
            expr = f"({a} {op1} {b}) {op2} {c}"
            answer = eval(expr)

        self.problem_str, self.correct_answer = expr, answer
        self.label_problem.config(text=expr, fg="black")

        # Очистка кнопок
        for btn in self.answer_buttons:
            btn.destroy()
        self.answer_buttons.clear()

        # Генерация ответов
        wrong = set()
        while len(wrong) < 3:
            w = answer + random.randint(-5, 5)
            if w != answer and w >= 0: wrong.add(w)
        answers = [answer] + list(wrong)
        random.shuffle(answers)

        for ans in answers:
            btn = tk.Button(self.answers_frame, text=str(ans), font=("Arial", 14), width=8,
                            command=lambda a=ans: self.check_answer(a))
            btn.pack(side=tk.LEFT, padx=5)
            self.answer_buttons.append(btn)

        self.update_smooth_timer()

    def update_smooth_timer(self):
        if not self.running or self.locked:
            return
        elapsed = time.time() - self.problem_start_time
        remaining = self.total_problem_time - elapsed
        if remaining > 0:
            width = int((remaining / self.total_problem_time) * 300)
            color = "#FF9800" if remaining < 2 else "#4CAF50"
            self.time_bar.coords(self.time_bar_rect, 0, 0, width, 8)
            self.time_bar.itemconfig(self.time_bar_rect, fill=color)
            self.problem_timer_id = self.root.after(50, self.update_smooth_timer)
        else:
            self.handle_timeout()

    def handle_timeout(self):
        if not self.running:
            return
        self.locked = True
        self.score, self.round_time_left = self.apply_penalty(self.score, self.round_time_left)
        self.label_score.config(text=f"Очки: {self.score}")
        self.label_round_time.config(text=f"Раунд: {self.round_time_left} сек")
        self.label_problem.config(text=f"{self.problem_str} = {self.correct_answer}", fg="red")
        self.root.after(800, self.next_problem)  # ← ОБЯЗАТЕЛЬНО!

    def check_answer(self, user_answer):
        if not self.running or self.locked: return
        self.root.after(600, self.next_problem)

        self.cancel_problem_timer()
        self.locked = True

        is_correct = (user_answer == self.correct_answer)
        if is_correct:
            self.play_sound(self.sound_correct)
            self.score += max(10, 5 * self.level)
            self.correct_in_row += 1
            self.wrong_in_row = 0
        else:
            self.play_sound(self.sound_wrong)
            self.score, self.round_time_left = self.apply_penalty(self.score, self.round_time_left)
            self.wrong_in_row += 1
            self.correct_in_row = 0

        # Обновление уровня
        old_level = self.level
        new_level, self.correct_in_row, self.wrong_in_row = self.update_level_by_streak(
            self.level, self.correct_in_row, self.wrong_in_row
        )

        if new_level != old_level:
            self.level = new_level
            self.label_title.config(text=f"🔢 Математика | Уровень: {self.level}")
            msg = "Уровень повышен!" if new_level > old_level else "Уровень понижен"
            # Показываем сообщение БЕЗ блокировки основного потока
            self.root.after(100, lambda: messagebox.showinfo(msg, f"Теперь уровень: {self.level}"))

    def next_problem(self):
        if self.running:
            self.generate_problem()

    def update_round_timer(self):
        if self.running and self.round_time_left > 0:
            self.round_time_left -= 1
            self.label_round_time.config(text=f"Раунд: {self.round_time_left} сек")
            self.root.after(1000, self.update_round_timer)
        elif self.running:
            self.finish_exercise()

    def finish_exercise(self):
        self.running = False
        self.cancel_problem_timer()
        self.stop_background_music()
        for btn in self.answer_buttons:
            btn.config(state="disabled")
        self.save_progress()
        messagebox.showinfo("Раунд завершён", f"Счёт: {self.score}\nУровень: {self.level}")
        self.on_finish()

    def save_progress(self):
        self.profile["exercises"]["math"].update({
            "level": self.level,
            "score": self.score,
            "correct_in_row": self.correct_in_row,
            "wrong_in_row": self.wrong_in_row
        })
        self.save_profile(self.profile)
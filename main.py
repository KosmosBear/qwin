# main.py дополнение коммента и учусь коммитить
import tkinter as tk
from tkinter import messagebox
import os
from PIL import Image, ImageTk
from profile import load_profile, save_profile, get_avg_level
from exercises.math_game import MathExercise
from exercises.memory_game import MemoryGame

AVATAR_COUNT = 4

class ProfileScreen:
    def __init__(self, root, profile, on_save):
        self.root = root
        self.original_profile = profile.copy()
        self.profile = profile
        self.on_save = on_save
        self.setup_ui()

    def setup_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="✏️ Редактировать профиль", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Ваше имя:", font=("Arial", 12)).pack(pady=(10, 0))
        self.name_entry = tk.Entry(self.root, font=("Arial", 12), width=20)
        self.name_entry.insert(0, self.profile["name"])
        self.name_entry.pack(pady=5)

        tk.Label(self.root, text="Выберите аватар:", font=("Arial", 12)).pack(pady=(15, 5))
        avatar_frame = tk.Frame(self.root)
        avatar_frame.pack(pady=5)

        self.avatar_var = tk.IntVar(value=self.profile["avatar"])
        self.avatar_imgs = []

        for i in range(1, AVATAR_COUNT + 1):
            try:
                img = Image.open(f"assets/avatars/avatar{i}.png")
                img = img.resize((60, 60), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.avatar_imgs.append(photo)
                tk.Radiobutton(avatar_frame, image=photo, variable=self.avatar_var, value=i, indicatoron=False).pack(side=tk.LEFT, padx=5)
            except Exception as e:
                print(f"Ошибка аватара {i}: {e}")
                tk.Radiobutton(avatar_frame, text=f"Аватар {i}", variable=self.avatar_var, value=i).pack(side=tk.LEFT, padx=5)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Сохранить", command=self.save).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Отмена", command=self.cancel).pack(side=tk.LEFT, padx=5)

    def save(self):
        name = self.name_entry.get().strip() or "Новичок"
        self.profile["name"] = name
        self.profile["avatar"] = self.avatar_var.get()
        save_profile(self.profile)
        self.on_save()

    def cancel(self):
        self.profile.update(self.original_profile)
        self.on_save()


class MainScreen:
    def __init__(self, root):
        self.root = root
        self.profile = load_profile()
        self.setup_ui()

    def setup_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Шапка: аватар + имя + уровень
        header_frame = tk.Frame(self.root)
        header_frame.pack(pady=15)

        # Аватар
        try:
            img = Image.open(f"assets/avatars/avatar{self.profile['avatar']}.png")
            img = img.resize((150, 150), Image.Resampling.LANCZOS)
            self.header_avatar_img = ImageTk.PhotoImage(img)
            avatar_label = tk.Label(header_frame, image=self.header_avatar_img)
            avatar_label.pack(side=tk.LEFT, padx=(0, 10))
        except Exception:
            avatar_label = tk.Label(header_frame, text="👤", font=("Arial", 30))
            avatar_label.pack(side=tk.LEFT, padx=(0, 10))

        # Имя и общий уровень
        info_frame = tk.Frame(header_frame)
        info_frame.pack(side=tk.LEFT)
        tk.Label(info_frame, text=self.profile["name"], font=("Arial", 16, "bold")).pack(anchor="w")
        avg_level = get_avg_level(self.profile)
        tk.Label(info_frame, text=f"Уровень: {avg_level}", font=("Arial", 12)).pack(anchor="w")

        # Кнопка профиля
        tk.Button(self.root, text="⚙️ Профиль", command=self.open_profile).pack(pady=5)

        # Упражнения
        exercises = [
            ("🧠 Математика", self.start_math),
            ("🧩 Память", self.start_memory),
            ("👁️ Внимание", self.coming_soon),
            ("🧮 Логика", self.coming_soon),
        ]

        for name, cmd in exercises:
            tk.Button(self.root, text=name, font=("Arial", 12), width=20, command=cmd).pack(pady=8)

    def open_profile(self):
        ProfileScreen(self.root, self.profile, self.return_to_main)

    def return_to_main(self):
        self.profile = load_profile()
        self.setup_ui()

    def start_math(self):
        MathExercise(self.root, self.profile, self.return_to_main, save_profile)

    def start_memory(self):
        MemoryGame(self.root, self.profile, self.return_to_main, save_profile)

    def coming_soon(self):
        messagebox.showinfo("Скоро", "Это упражнение будет доступно позже!")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("NeuroTrainer")
    root.geometry("420x650")
    MainScreen(root)
    root.mainloop()
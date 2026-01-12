# exercises/feedback.py
import tkinter as tk

class FeedbackAnimation:
    @staticmethod
    def show(widget, is_correct):
        original_bg = widget.cget("bg")
        color = "#90ee90" if is_correct else "#ffcccc"
        widget.config(bg=color)
        widget.after(500, lambda: widget.config(bg=original_bg))
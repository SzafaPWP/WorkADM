# theme_light_improved.py
import tkinter as tk
from tkinter import ttk

def apply_theme(root):
    style = ttk.Style(root)
    try:
        style.theme_use('clam')
    except Exception:
        pass

    bg = "#F2F4F7"
    panel = "#FFFFFF"
    fg = "#222222"
    accent = "#1976D2"

    try:
        root.configure(bg=bg)
    except Exception:
        pass

    style.configure('.', background=bg, foreground=fg, font=("Segoe UI", 10))
    style.configure('TFrame', background=panel)
    style.configure('TLabel', background=panel, foreground=fg)
    style.configure('Tile.TFrame', background=panel)
    style.configure('TButton', background="#f0f3f6", foreground=fg, padding=6)
    style.map('TButton', background=[('active','#e6edf6'),('pressed','#dbeafc')])
    style.configure("Treeview", background="#FFFFFF", fieldbackground="#FFFFFF", foreground=fg, rowheight=22)
    style.configure("Treeview.Heading", background="#f0f3f6", foreground=accent, font=("Segoe UI", 10, "bold"))
    style.configure("TNotebook.Tab", background="#f7f9fb", foreground=fg, padding=[10,8], font=("Segoe UI", 10))

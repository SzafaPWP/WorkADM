# theme_dark_exact.py
# Refined dark ttk theme tuned to match the invoice app screenshot
import tkinter as tk
from tkinter import ttk

def apply_theme(root):
    """Apply a refined dark theme to ttk widgets."""
    style = ttk.Style(root)
    try:
        style.theme_use('clam')
    except Exception:
        pass

    # Palette tuned to screenshot
    bg = "#141414"
    panel = "#1c1c1c"
    panel2 = "#222426"
    header = "#2b2f33"
    fg = "#E6E6E6"
    accent = "#2b7bd6"
    tile_bg = "#191919"
    border = "#2a2a2a"
    selection = accent

    try:
        root.configure(bg=bg)
    except Exception:
        pass

    default_font = ("Segoe UI", 10)
    style.configure(".", background=bg, foreground=fg, font=default_font)
    style.configure("TFrame", background=panel)
    style.configure("Card.TFrame", background=tile_bg, relief="flat", borderwidth=1)
    style.configure("TLabel", background=panel, foreground=fg)
    style.configure("Header.TLabel", font=("Segoe UI", 10, "bold"), background=panel, foreground=fg)
    style.configure("Small.TLabel", font=("Segoe UI", 9), background=panel, foreground=fg)

    style.configure("TButton", background=panel2, foreground=fg, borderwidth=0, padding=6, relief="flat")
    style.map("TButton", background=[("active", "#2a2d30"), ("pressed", "#232526")])

    style.configure("Primary.TButton", background=accent, foreground="#ffffff", font=("Segoe UI", 10, "bold"))
    style.map("Primary.TButton", background=[("active", "#1f63a8"), ("pressed", "#154a7a")])

    style.configure("TEntry", fieldbackground=panel, foreground=fg, background=panel)
    style.configure("TCombobox", fieldbackground=panel, foreground=fg, background=panel)

    style.configure("Treeview", background=panel, fieldbackground=panel, foreground=fg, rowheight=24)
    style.configure("Treeview.Heading", background=header, foreground=fg, font=("Segoe UI", 10, "bold"), relief="flat")
    style.map("Treeview", background=[("selected", selection)], foreground=[("selected", "#ffffff")])

    style.configure("TNotebook", background=bg, borderwidth=0)
    style.configure("TNotebook.Tab", background=panel2, foreground=fg, padding=[12,8], font=("Segoe UI", 10))
    style.map("TNotebook.Tab", background=[("selected", header)], foreground=[("selected", "#ffffff")])

    style.configure("Dialog.TFrame", background=tile_bg)
    style.configure("Dialog.TLabel", background=tile_bg, foreground=fg)

    style.configure("Vertical.TScrollbar", background=panel, troughcolor=panel, bordercolor=border)

    try:
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
    except Exception:
        pass

# theme_light.py
# Clean light theme for ttk (Tkinter)
import tkinter as tk
from tkinter import ttk

def apply_theme(root):
    """Apply a light theme to ttk widgets. Call early after creating Tk() or when toggling themes."""
    style = ttk.Style(root)
    try:
        style.theme_use('clam')
    except Exception:
        pass

    # Colors
    bg = "#F6F7F9"
    panel = "#FFFFFF"
    fg = "#222222"
    accent = "#1976D2"  # blue
    light = "#2b6fa8"
    tile_bg = "#FFFFFF"
    border = "#e6e9ee"
    selected = "#cfe8ff"

    try:
        root.configure(bg=bg)
    except Exception:
        pass

    style.configure(".", background=bg, foreground=fg, font=("Segoe UI", 10))
    style.configure("TFrame", background=panel)
    style.configure("TLabel", background=panel, foreground=fg)
    style.configure("Header.TLabel", font=("Segoe UI", 11, "bold"), foreground=light, background=panel)
    style.configure("Tile.TFrame", background=tile_bg, relief="flat", borderwidth=1)
    style.configure("TileTitle.TLabel", background=tile_bg, foreground=accent, font=("Segoe UI", 9, "bold"))
    style.configure("TileValue.TLabel", background=tile_bg, foreground=fg, font=("Segoe UI", 16, "bold"))

    # Buttons
    style.configure("TButton", background="#f0f3f6", foreground=fg, borderwidth=0, padding=6)
    style.map("TButton",
              background=[("active", "#e6edf6"), ("pressed", "#dbeafc")],
              foreground=[("disabled", "#a0a0a0")])

    style.configure("Primary.TButton", background=accent, foreground="white", font=("Segoe UI", 10, "bold"))
    style.map("Primary.TButton", background=[("active", "#145ca8"), ("pressed", "#0d3f6d")])

    # Entries and Combobox
    style.configure("TEntry", fieldbackground="#FFFFFF", foreground=fg, background="#FFFFFF")
    style.configure("TCombobox", fieldbackground="#FFFFFF", foreground=fg)

    # Treeview / Table
    style.configure("Treeview", background="#FFFFFF", fieldbackground="#FFFFFF", foreground=fg, rowheight=22)
    style.configure("Treeview.Heading", background="#f0f3f6", foreground=light, font=("Segoe UI", 9, "bold"))
    style.map("Treeview", background=[("selected", selected)])

    # Notebook (tabs)
    style.configure("TNotebook", background=bg, borderwidth=0)
    style.configure("TNotebook.Tab", background="#f7f9fb", foreground=light, padding=[8,6], font=("Segoe UI", 10))
    style.map("TNotebook.Tab", background=[("selected", "#eef6ff")], foreground=[("selected", "#000000")])

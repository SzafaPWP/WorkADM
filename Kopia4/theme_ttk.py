
# theme_ttk.py
# Modern dark theme for ttk (Tkinter)
import tkinter as tk
from tkinter import ttk

def apply_theme(root):
    """Apply a dark theme to ttk widgets. Call early after creating Tk() but before building complex widgets."""
    style = ttk.Style(root)
    try:
        style.theme_use('clam')
    except Exception:
        pass

    # Colors
    bg = "#111217"
    panel = "#0f1316"
    fg = "#E6EEF3"
    accent = "#0ea5ff"  # cyan-blue
    light = "#9fbff3"
    tile_bg = "#15171a"
    border = "#1e2428"
    selected = "#0ea5ff20"  # semi transparent
    # General
    root.configure(bg=bg)
    style.configure(".", background=bg, foreground=fg, font=("Segoe UI", 10))
    style.configure("TFrame", background=panel)
    style.configure("TLabel", background=panel, foreground=fg)
    style.configure("Header.TLabel", font=("Segoe UI", 11, "bold"), foreground=light, background=panel)
    style.configure("Tile.TFrame", background=tile_bg, relief="flat", borderwidth=1)
    style.configure("TileTitle.TLabel", background=tile_bg, foreground=light, font=("Segoe UI", 9, "bold"))
    style.configure("TileValue.TLabel", background=tile_bg, foreground=fg, font=("Segoe UI", 16, "bold"))

    # Buttons
    style.configure("TButton", background="#1b1f23", foreground=fg, borderwidth=0, padding=6)
    style.map("TButton",
              background=[("active", "#222528"), ("pressed", "#2a2d30")],
              foreground=[("disabled", "#808080")])

    style.configure("Primary.TButton", background=accent, foreground="white", font=("Segoe UI", 10, "bold"))
    style.map("Primary.TButton", background=[("active", "#0891cf"), ("pressed", "#046b9a")])

    # Entries and Combobox
    style.configure("TEntry", fieldbackground="#0f1316", foreground=fg, background="#0f1316")
    style.configure("TCombobox", fieldbackground="#0f1316", foreground=fg)

    # Treeview / Table
    style.configure("Treeview", background=bg, fieldbackground=bg, foreground=fg, rowheight=22)
    style.configure("Treeview.Heading", background=panel, foreground=light, font=("Segoe UI", 9, "bold"))
    style.map("Treeview", background=[("selected", selected)])

    # Notebook (tabs)
    style.configure("TNotebook", background=bg, borderwidth=0)
    style.configure("TNotebook.Tab", background="#121316", foreground=light, padding=[8,6], font=("Segoe UI", 10))
    style.map("TNotebook.Tab", background=[("selected", "#1a2330")], foreground=[("selected", "#ffffff")])

    # Scrollbars tweaks not supported cross-platform here; leave defaults

    # Custom tag colors for tree items can be set during insertion
    # Example usage in code: tree.tag_configure('ok', background='#163a14', foreground='#b7f3c2')

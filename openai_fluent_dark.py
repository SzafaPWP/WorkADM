
import tkinter as tk
from tkinter import ttk

# ===== OpenAI Fluent Dark — compact, Windows-like =====
BG        = "#1b1d22"   # app background
SURFACE   = "#22252b"   # panels/cards
SURFACE2  = "#2a2e35"   # inputs
BORDER    = "#2f343c"   # subtle border
FG        = "#e5e7eb"   # text
MUTED     = "#a7b0bc"   # secondary
ACCENT    = "#10a37f"
ACCENT_H  = "#13b08d"
ACCENT_A  = "#0c8b6f"
SEL_BG    = "#0f5e4d"   # selection in lists
SEL_FG    = "#ffffff"
ALT_ROW   = "#252932"   # zebra row alt

def _map(style: ttk.Style, name: str, **kw):
    for opt, states in kw.items():
        style.map(name, **{opt: states})

def _base(style: ttk.Style, root):
    try:
        style.theme_use("clam")
    except Exception:
        pass

    # Global defaults
    style.configure(".", background=BG, foreground=FG, font=("Segoe UI", 10))

    # Top-level background
    if hasattr(root, "configure"):
        try:
            root.configure(bg=BG)
        except Exception:
            pass

    # Containers
    style.configure("TFrame", background=BG)
    style.configure("Card.TFrame", background=SURFACE, bordercolor=BORDER, relief="flat")
    style.configure("TLabelframe", background=BG, foreground=FG, bordercolor=BORDER)
    style.configure("TLabelframe.Label", background=BG, foreground=MUTED)

    # Labels / separators
    style.configure("TLabel", background=BG, foreground=FG)
    style.configure("Subtitle.TLabel", foreground=MUTED)
    style.configure("TSeparator", background=BORDER)

def _buttons(style: ttk.Style):
    # Neutral button (flat, subtle border)
    style.configure("TButton",
                    background=SURFACE,
                    foreground=FG,
                    padding=(14, 8),
                    borderwidth=1,
                    relief="flat")
    _map(style, "TButton",
         background=[("active", SURFACE2), ("pressed", SURFACE2)],
         bordercolor=[("!disabled", BORDER)])

    # Accent button (OpenAI green)
    style.configure("Accent.TButton",
                    background=ACCENT,
                    foreground="#ffffff",
                    padding=(16, 10),
                    borderwidth=0)
    _map(style, "Accent.TButton",
         background=[("active", ACCENT_H), ("pressed", ACCENT_A)])

def _inputs(style: ttk.Style):
    # Entries & comboboxes — compact, Fluent-like
    common = dict(fieldbackground=SURFACE2,
                  foreground=FG,
                  bordercolor=BORDER,
                  lightcolor=ACCENT,
                  darkcolor=BORDER,
                  padding=7)
    style.configure("TEntry", **common)
    style.configure("TCombobox", arrowsize=14, **common)
    style.map("TCombobox",
              fieldbackground=[("readonly", SURFACE2)],
              foreground=[("readonly", FG)],
              bordercolor=[("focus", ACCENT)])

    # Checks / radios
    style.configure("TCheckbutton", background=BG, foreground=FG, padding=4)
    style.configure("TRadiobutton", background=BG, foreground=FG, padding=4)

def _tree(style: ttk.Style):
    style.configure("Treeview",
                    background=SURFACE,
                    fieldbackground=SURFACE,
                    foreground=FG,
                    bordercolor=BORDER,
                    rowheight=24)
    style.configure("Treeview.Heading",
                    background=SURFACE2,
                    foreground=FG,
                    relief="flat",
                    bordercolor=BORDER,
                    padding=6)
    # selection
    style.map("Treeview",
              background=[("selected", SEL_BG)],
              foreground=[("selected", SEL_FG)])

def _notebook(style: ttk.Style):
    style.configure("FluentDark.TNotebook", background=BG, bordercolor=BORDER)
    style.layout("FluentDark.TNotebook.Tab", [
        ("Notebook.tab", {"sticky": "nswe",
          "children": [("Notebook.padding", {"side": "top", "sticky":"nswe",
            "children":[("Notebook.label", {"side":"left", "sticky":""})]})]})])
    style.configure("FluentDark.TNotebook.Tab",
                    background=SURFACE,
                    foreground=MUTED,
                    padding=(14, 8),
                    borderwidth=1)
    _map(style, "FluentDark.TNotebook.Tab",
         background=[("selected", SURFACE2)],
         foreground=[("selected", FG)])

def apply_openai_theme(root: tk.Misc) -> None:
    """Dark Fluent theme using the same API name for drop-in use."""
    style = ttk.Style(root)
    _base(style, root)
    _buttons(style)
    _inputs(style)
    _tree(style)
    _notebook(style)
    # minimal scrollbars
    style.configure("Horizontal.TScrollbar", background=BG)
    style.configure("Vertical.TScrollbar", background=BG)

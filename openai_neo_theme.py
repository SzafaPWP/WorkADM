
import tkinter as tk
from tkinter import ttk

# ======= OpenAI Neo UI 2025 palette =======
BG        = "#111827"  # slate-900 (deeper)
SURFACE   = "#0f172a"  # slate-950-ish, window bg
PANEL     = "#1f2937"  # slate-800 (cards/inputs base)
PANEL2    = "#374151"  # slate-700 (hover/active)
BORDER    = "#2b3442"  # subtle border
FG        = "#e5e7eb"  # zinc-100
MUTED     = "#cbd5e1"  # slate-300
ACCENT    = "#10a37f"  # OpenAI green
ACCENT_H  = "#15b690"
ACCENT_A  = "#0b7b61"
SEL_BG    = "#0b7b61"
SEL_FG    = "#ffffff"
WARN      = "#f59e0b"
ERR       = "#ef4444"

def _map(style: ttk.Style, name: str, **kw):
    for opt, states in kw.items():
        style.map(name, **{opt: states})

def _base(style: ttk.Style, root):
    # base theme
    try:
        style.theme_use("clam")
    except Exception:
        pass
    # global
    style.configure(".", background=BG, foreground=FG, font=("Segoe UI", 10))
    # top-level window bg
    if hasattr(root, "configure"):
        try:
            root.configure(bg=SURFACE)
        except Exception:
            pass

    # Frames / Panels
    style.configure("TFrame", background=BG)
    style.configure("Card.TFrame", background=PANEL, relief="flat")
    style.configure("Soft.TLabelframe", background=PANEL, foreground=FG, bordercolor=BORDER)
    style.configure("TLabelframe", background=BG, foreground=FG, bordercolor=BORDER)
    style.configure("TLabelframe.Label", background=BG, foreground=FG)

    # Labels
    style.configure("TLabel", background=BG, foreground=FG)
    style.configure("Subtitle.TLabel", foreground=MUTED)

    # Separator
    style.configure("TSeparator", background=BORDER)

def _buttons(style: ttk.Style):
    # Neutral button
    style.configure("TButton",
                    background=PANEL,
                    foreground=FG,
                    padding=(14, 8),
                    borderwidth=0)
    _map(style, "TButton",
         background=[("active", PANEL2), ("pressed", PANEL2)],
         relief=[("pressed", "sunken")])

    # Accent button
    style.configure("Accent.TButton",
                    background=ACCENT,
                    foreground="#ffffff",
                    padding=(16, 10),
                    borderwidth=0)
    _map(style, "Accent.TButton",
         background=[("active", ACCENT_H), ("pressed", ACCENT_A)],
         foreground=[("disabled", "#e5e7eb")])

def _inputs(style: ttk.Style):
    # Entries
    style.configure("TEntry",
                    fieldbackground=PANEL,
                    foreground=FG,
                    bordercolor=BORDER,
                    lightcolor=ACCENT,
                    darkcolor=BORDER,
                    padding=8)
    # Combobox
    style.configure("TCombobox",
                    fieldbackground=PANEL,
                    foreground=FG,
                    bordercolor=BORDER,
                    arrowsize=14,
                    padding=8)
    style.map("TCombobox",
              fieldbackground=[("readonly", PANEL)],
              foreground=[("readonly", FG)],
              bordercolor=[("focus", ACCENT)])

    # Spinbox/Check/Radio
    style.configure("TCheckbutton", background=BG, foreground=FG, padding=6)
    style.configure("TRadiobutton", background=BG, foreground=FG, padding=6)

def _tree(style: ttk.Style):
    style.configure("Treeview",
                    background=PANEL,
                    fieldbackground=PANEL,
                    foreground=FG,
                    bordercolor=BORDER,
                    rowheight=26)
    style.configure("Treeview.Heading",
                    background=PANEL2,
                    foreground=FG,
                    relief="flat",
                    bordercolor=BORDER,
                    padding=6)
    style.map("Treeview",
              background=[("selected", SEL_BG)],
              foreground=[("selected", SEL_FG)])

def _notebook(style: ttk.Style):
    # container
    style.configure("OpenAI.Neo.TNotebook", background=BG, bordercolor=BORDER)
    # tab layout
    style.layout("OpenAI.Neo.TNotebook.Tab", [
        ("Notebook.tab", {"sticky": "nswe",
            "children": [("Notebook.padding", {"side": "top", "sticky": "nswe",
                "children": [("Notebook.label", {"side": "left", "sticky": ""})]})]})])
    # tab look
    style.configure("OpenAI.Neo.TNotebook.Tab",
                    background=PANEL,
                    foreground=MUTED,
                    padding=(18, 10),
                    borderwidth=0)
    _map(style, "OpenAI.Neo.TNotebook.Tab",
         background=[("selected", PANEL2)],
         foreground=[("selected", "#ffffff")])

def apply_openai_neo_theme(root: tk.Misc) -> None:
    style = ttk.Style(root)
    _base(style, root)
    _buttons(style)
    _inputs(style)
    _tree(style)
    _notebook(style)
    # Scrollbars minimal
    style.configure("Horizontal.TScrollbar", background=BG)
    style.configure("Vertical.TScrollbar", background=BG)

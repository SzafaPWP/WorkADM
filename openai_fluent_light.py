
import tkinter as tk
from tkinter import ttk

# ===== OpenAI Fluent Light 2025 =====
BG        = "#f7f7fb"   # app background (very light)
SURFACE   = "#ffffff"   # cards/panels
SURFACE2  = "#f0f2f5"   # inputs background
BORDER    = "#d9dde3"   # subtle border
FG        = "#1f2937"   # text
MUTED     = "#6b7280"   # secondary text
ACCENT    = "#10a37f"   # OpenAI green
ACCENT_H  = "#0e9272"
ACCENT_A  = "#0b7b61"
SEL_BG    = "#d7f3eb"   # selection bg (light green tint)
SEL_FG    = "#0b3d2f"

def _map(style: ttk.Style, name: str, **kw):
    for opt, states in kw.items():
        style.map(name, **{opt: states})

def _base(style: ttk.Style, root):
    try:
        style.theme_use("clam")
    except Exception:
        pass
    style.configure(".", background=BG, foreground=FG, font=("Segoe UI", 10))

    if hasattr(root, "configure"):
        try:
            root.configure(bg=BG)
        except Exception:
            pass

    # Containers
    style.configure("TFrame", background=BG)
    style.configure("Card.TFrame", background=SURFACE, relief="flat")
    style.configure("TLabelframe", background=BG, foreground=FG, bordercolor=BORDER)
    style.configure("TLabelframe.Label", background=BG, foreground=MUTED)

    style.configure("TLabel", background=BG, foreground=FG)
    style.configure("Subtitle.TLabel", foreground=MUTED)
    style.configure("TSeparator", background=BORDER)

def _buttons(style: ttk.Style):
    style.configure("TButton",
                    background=SURFACE,
                    foreground=FG,
                    padding=(14, 9),
                    borderwidth=1,
                    relief="flat",
                    focusthickness=2,
                    focuscolor=ACCENT)
    _map(style, "TButton",
         background=[("active", SURFACE2), ("pressed", SURFACE2)],
         bordercolor=[("!disabled", BORDER)])

    style.configure("Accent.TButton",
                    background=ACCENT,
                    foreground="#ffffff",
                    padding=(16, 10),
                    borderwidth=0)
    _map(style, "Accent.TButton",
         background=[("active", ACCENT_H), ("pressed", ACCENT_A)])

def _inputs(style: ttk.Style):
    entry_opts = dict(fieldbackground=SURFACE2, foreground=FG, bordercolor=BORDER,
                      lightcolor=ACCENT, darkcolor=BORDER, padding=8)
    style.configure("TEntry", **entry_opts)
    style.configure("TCombobox", arrowsize=14, **entry_opts)
    style.map("TCombobox",
              fieldbackground=[("readonly", SURFACE2)],
              foreground=[("readonly", FG)],
              bordercolor=[("focus", ACCENT)])

    style.configure("TCheckbutton", background=BG, foreground=FG, padding=6)
    style.configure("TRadiobutton", background=BG, foreground=FG, padding=6)

def _tree(style: ttk.Style):
    style.configure("Treeview",
                    background=SURFACE,
                    fieldbackground=SURFACE,
                    foreground=FG,
                    bordercolor=BORDER,
                    rowheight=26)
    style.configure("Treeview.Heading",
                    background=SURFACE2,
                    foreground=FG,
                    relief="flat",
                    bordercolor=BORDER,
                    padding=6)
    style.map("Treeview",
              background=[("selected", SEL_BG)],
              foreground=[("selected", SEL_FG)])

def _notebook(style: ttk.Style):
    style.configure("Fluent.TNotebook", background=BG, bordercolor=BORDER)
    style.layout("Fluent.TNotebook.Tab", [
        ("Notebook.tab", {"sticky": "nswe",
          "children": [("Notebook.padding", {"side":"top", "sticky":"nswe",
            "children":[("Notebook.label", {"side":"left", "sticky":""})]})]})])
    style.configure("Fluent.TNotebook.Tab",
                    background=SURFACE,
                    foreground=MUTED,
                    padding=(16, 9),
                    borderwidth=1)
    _map(style, "Fluent.TNotebook.Tab",
         background=[("selected", SURFACE2)],
         foreground=[("selected", FG)])

def apply_openai_theme(root: tk.Misc) -> None:
    """Light theme version with the same function name to be drop-in."""
    style = ttk.Style(root)
    _base(style, root)
    _buttons(style)
    _inputs(style)
    _tree(style)
    _notebook(style)
    style.configure("Horizontal.TScrollbar", background=BG)
    style.configure("Vertical.TScrollbar", background=BG)

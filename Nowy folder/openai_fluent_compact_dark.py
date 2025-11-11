# openai_fluent_compact_dark.py
import tkinter as tk
from tkinter import ttk

# ---- Paleta (Fluent, kompakt, dark) ----
BG       = "#17191d"   # tło okna
SURF     = "#1f2329"   # panele / karty
SURF2    = "#262b33"   # input/hover
BORDER   = "#2b313a"
FG       = "#e6e8eb"
MUTED    = "#a9b0ba"
ACCENT   = "#10a37f"
ACCENT_H = "#12b089"
ACCENT_P = "#0c8b6f"
SEL_BG   = "#0e5c4d"
SEL_FG   = "#ffffff"

# REKURSYWNE przyciemnienie zwykłych tk.* kontenerów (żeby nie było białych placków)
def _force_dark_bg(root):
    try:
        root.configure(bg=BG)
    except Exception:
        pass
    stack = [root]
    while stack:
        w = stack.pop()
        for c in w.winfo_children():
            try:
                if isinstance(c, (tk.Tk, tk.Toplevel, tk.Frame, tk.LabelFrame, tk.Canvas)):
                    c.configure(bg=BG)
            except Exception:
                pass
            stack.append(c)

def _map(style: ttk.Style, name: str, **kw):
    for opt, states in kw.items():
        style.map(name, **{opt: states})

def _base(style: ttk.Style, root):
    try:
        style.theme_use("clam")
    except Exception:
        pass
    # global: CZCIONKA MNIEJSZA + tło wszędzie
    style.configure(".", background=BG, foreground=FG, font=("Segoe UI", 9))
    _force_dark_bg(root)

    style.configure("TFrame", background=BG)
    style.configure("TLabelframe", background=BG, foreground=FG, bordercolor=BORDER)
    style.configure("TLabelframe.Label", background=BG, foreground=MUTED)
    style.configure("TLabel", background=BG, foreground=FG)
    style.configure("Subtitle.TLabel", foreground=MUTED)
    style.configure("TSeparator", background=BORDER)

def _buttons(style: ttk.Style):
    # kompaktowe, płaskie, bez przesady
    style.configure("TButton",
        background=SURF, foreground=FG, padding=(10,6),
        borderwidth=1, relief="flat")
    _map(style, "TButton",
        background=[("active", SURF2), ("pressed", SURF2)],
        bordercolor=[("!disabled", BORDER)])

    style.configure("Accent.TButton",
        background=ACCENT, foreground="#ffffff", padding=(12,7),
        borderwidth=0)
    _map(style, "Accent.TButton",
        background=[("active", ACCENT_H), ("pressed", ACCENT_P)])

def _inputs(style: ttk.Style):
    common = dict(fieldbackground=SURF2, foreground=FG,
                  bordercolor=BORDER, lightcolor=ACCENT, darkcolor=BORDER,
                  padding=6)
    style.configure("TEntry", **common)
    style.configure("TCombobox", arrowsize=12, **common)
    style.map("TCombobox",
        fieldbackground=[("readonly", SURF2)],
        foreground=[("readonly", FG)],
        bordercolor=[("focus", ACCENT)])
    style.configure("TCheckbutton", background=BG, foreground=FG, padding=3)
    style.configure("TRadiobutton", background=BG, foreground=FG, padding=3)

def _tree(style: ttk.Style):
    style.configure("Treeview",
        background=SURF, fieldbackground=SURF, foreground=FG,
        bordercolor=BORDER, rowheight=22)
    style.configure("Treeview.Heading",
        background=SURF2, foreground=FG, relief="flat",
        bordercolor=BORDER, padding=5)
    style.map("Treeview",
        background=[("selected", SEL_BG)],
        foreground=[("selected", SEL_FG)])

def _notebook(style: ttk.Style):
    style.configure("FluentCompactDark.TNotebook", background=BG, bordercolor=BORDER)
    style.layout("FluentCompactDark.TNotebook.Tab", [
        ("Notebook.tab", {"sticky":"nswe",
            "children":[("Notebook.padding", {"side":"top","sticky":"nswe",
                "children":[("Notebook.label", {"side":"left","sticky":""})]})]})])
    style.configure("FluentCompactDark.TNotebook.Tab",
        background=SURF, foreground=MUTED, padding=(10,6), borderwidth=1)
    _map(style, "FluentCompactDark.TNotebook.Tab",
        background=[("selected", SURF2)],
        foreground=[("selected", FG)])

def apply_openai_theme(root: tk.Misc) -> None:
    style = ttk.Style(root)
    _base(style, root)
    _buttons(style)
    _inputs(style)
    _tree(style)
    _notebook(style)
    style.configure("Horizontal.TScrollbar", background=BG)
    style.configure("Vertical.TScrollbar", background=BG)

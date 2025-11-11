
import tkinter as tk
from tkinter import ttk

OPENAI_BG = "#0f172a"      # slate-900
OPENAI_FG = "#e2e8f0"      # slate-200
OPENAI_MID = "#1e293b"     # slate-800
OPENAI_SOFT = "#334155"    # slate-700
OPENAI_ACCENT = "#10a37f"  # OpenAI green
OPENAI_ACCENT_HOVER = "#0d8e6f"
OPENAI_ACCENT_ACTIVE = "#0b7b61"
OPENAI_BORDER = "#475569"  # slate-600
OPENAI_SEL_BG = "#0b7b61"
OPENAI_SEL_FG = "#ffffff"

def _map_style(style: ttk.Style, style_name: str, **maps):
    for opt, states in maps.items():
        # states must be a list of (state, value) tuples
        style.map(style_name, **{opt: states})

def _configure_treeview(style: ttk.Style):
    style.configure("Treeview",
                    background=OPENAI_MID,
                    fieldbackground=OPENAI_MID,
                    foreground=OPENAI_FG,
                    bordercolor=OPENAI_BORDER,
                    rowheight=26)
    style.configure("Treeview.Heading",
                    background=OPENAI_SOFT,
                    foreground=OPENAI_FG,
                    relief="flat",
                    bordercolor=OPENAI_BORDER)
    style.map("Treeview",
              background=[("selected", OPENAI_SEL_BG)],
              foreground=[("selected", OPENAI_SEL_FG)])

def _configure_buttons(style: ttk.Style):
    style.configure("TButton",
                    background=OPENAI_SOFT,
                    foreground=OPENAI_FG,
                    padding=(14, 8),
                    borderwidth=0,
                    focusthickness=3,
                    focuscolor=OPENAI_ACCENT)
    _map_style(style, "TButton",
               background=[("disabled", OPENAI_SOFT),
                           ("active", OPENAI_SOFT)],
               relief=[("pressed", "sunken")])
    style.configure("Accent.TButton",
                    background=OPENAI_ACCENT,
                    foreground="#ffffff",
                    padding=(16, 9),
                    borderwidth=0)
    _map_style(style, "Accent.TButton",
               background=[("active", OPENAI_ACCENT_HOVER),
                           ("pressed", OPENAI_ACCENT_ACTIVE)],
               foreground=[("disabled", "#cbd5e1")])

def _configure_inputs(style: ttk.Style):
    style.configure("TEntry",
                    fieldbackground=OPENAI_MID,
                    foreground=OPENAI_FG,
                    padding=8,
                    bordercolor=OPENAI_BORDER)
    style.configure("TCombobox",
                    fieldbackground=OPENAI_MID,
                    foreground=OPENAI_FG,
                    padding=6,
                    arrowsize=14)
    style.map("TCombobox",
              fieldbackground=[("readonly", OPENAI_MID)],
              foreground=[("readonly", OPENAI_FG)])
    style.configure("TCheckbutton",
                    background=OPENAI_BG,
                    foreground=OPENAI_FG,
                    padding=6)
    style.configure("TRadiobutton",
                    background=OPENAI_BG,
                    foreground=OPENAI_FG,
                    padding=6)

def _configure_misc(style: ttk.Style):
    style.configure(".", background=OPENAI_BG, foreground=OPENAI_FG, font=("Segoe UI", 10))
    style.configure("TFrame", background=OPENAI_BG)
    style.configure("TLabel", background=OPENAI_BG, foreground=OPENAI_FG)
    style.configure("TLabelFrame", background=OPENAI_BG, foreground=OPENAI_FG, bordercolor=OPENAI_BORDER)
    style.configure("TSeparator", background=OPENAI_BORDER)
    style.configure("Status.TLabel", background=OPENAI_MID, padding=(10, 6))

def _configure_notebook(style: ttk.Style):
    style.layout("OpenAI.TNotebook.Tab", [
        ("Notebook.tab", {
            "sticky": "nswe",
            "children": [
                ("Notebook.padding", {
                    "side": "top",
                    "sticky": "nswe",
                    "children": [
                        ("Notebook.label", {"side": "left", "sticky": ""})
                    ]
                })
            ]
        })
    ])
    style.configure("OpenAI.TNotebook",
                    background=OPENAI_BG,
                    bordercolor=OPENAI_BORDER)
    style.configure("OpenAI.TNotebook.Tab",
                    background=OPENAI_SOFT,
                    foreground=OPENAI_FG,
                    padding=(18, 10),
                    borderwidth=0)
    _map_style(style, "OpenAI.TNotebook.Tab",
               background=[("selected", OPENAI_MID)],
               foreground=[("selected", "#ffffff")])

def apply_openai_theme(root: tk.Misc) -> None:
    # Apply base colors to the toplevel/root
    if hasattr(root, "configure"):
        try:
            root.configure(bg=OPENAI_BG)
        except Exception:
            pass

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    _configure_misc(style)
    _configure_buttons(style)
    _configure_inputs(style)
    _configure_treeview(style)
    _configure_notebook(style)

    # Global padding policy (subtle, modern)
    style.configure("TMenubutton", padding=(10, 6))
    style.configure("Horizontal.TScrollbar", background=OPENAI_BG)
    style.configure("Vertical.TScrollbar", background=OPENAI_BG)

    # convenience alias: use Notebook with this style name if available
    # Developers can set: notebook.configure(style="OpenAI.TNotebook")
    # and tab style will be "OpenAI.TNotebook.Tab" automatically.

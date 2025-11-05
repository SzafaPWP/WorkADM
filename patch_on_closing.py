# patch_on_closing.py — wstrzykuje metodę on_closing do klasy MainWindow
from pathlib import Path
import re

p = Path("main_window.py")
src = p.read_text(encoding="utf-8")

if "class MainWindow" not in src:
    raise SystemExit("Nie znaleziono klasy MainWindow w main_window.py")

if "def on_closing(self):" in src:
    print("on_closing już istnieje — nic nie zmieniam.")
else:
    # wstaw metodę po definicji __init__ (bezpieczne wstrzyknięcie)
    m = re.search(r"(?s)(class\s+MainWindow\s*\([^)]*\)\s*:\s*.*?def\s+__init__\s*\(\s*self[^\)]*\)\s*:\s*\n.*?)(\n\s*def\s|\Z)", src)
    if not m:
        # plan B: wstaw zaraz po 'class MainWindow'
        m = re.search(r"(class\s+MainWindow\s*\([^)]*\)\s*:\s*\n)", src)
        insert_at = m.end()
        payload = """
    def on_closing(self):
        try:
            from tkinter import messagebox
            if messagebox.askokcancel("Zamknij", "Czy na pewno chcesz zamknąć aplikację?"):
                self.destroy()
        except Exception:
            self.destroy()

"""
        src = src[:insert_at] + payload + src[insert_at:]
    else:
        insert_at = m.end(1)
        payload = """
    def on_closing(self):
        try:
            from tkinter import messagebox
            if messagebox.askokcancel("Zamknij", "Czy na pewno chcesz zamknąć aplikację?"):
                self.destroy()
        except Exception:
            self.destroy()

"""
        src = src[:insert_at] + payload + src[insert_at:]

p.write_text(src, encoding="utf-8")
print("OK: wstawiono metodę on_closing do klasy MainWindow.")

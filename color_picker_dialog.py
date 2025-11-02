import tkinter as tk
from tkinter.colorchooser import askcolor

class ColorPickerDialog(tk.Toplevel):
    def __init__(self, master, initial_color, title="Wybierz Kolor", callback=None):
        super().__init__(master)
        self.title(title)
        self.result_color = initial_color
        self.callback = callback
        self.transient(master)
        self.grab_set()
        
        # Centrowanie
        self.update_idletasks()
        width = 250
        height = 100
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        self.resizable(False, False)

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Wybrany kolor:").grid(row=0, column=0, padx=10, pady=10)
        
        self.color_preview = tk.Label(self, bg=self.result_color, width=10, relief=tk.SUNKEN)
        self.color_preview.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Button(self, text="Wybierz z Palety", command=self.pick_color).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(self, text="Zapisz i Zamknij", command=self.on_close).grid(row=1, column=1, padx=5, pady=5)

    def pick_color(self):
        # askcolor zwraca (RGB_tuple, HEX_string)
        color_code = askcolor(color=self.result_color, title="Paleta Kolorów")
        if color_code and color_code[1]:
            self.result_color = color_code[1]
            self.color_preview.config(bg=self.result_color)
            if self.callback:
                self.callback(self.result_color) # Natychmiastowa aktualizacja w oknie ustawień

    def on_close(self):
        self.destroy()
        # Właściwa aktualizacja wartości nastąpi w oknie nadrzędnym (settings_window) po kliknięciu "Zapisz"
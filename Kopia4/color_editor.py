# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
from employee_management import EmployeeManagement

class ColorEditor(tk.Toplevel):
    def __init__(self, master, emp_manager: EmployeeManagement):
        super().__init__(master)
        self.master = master
        self.emp_manager = emp_manager
        self.title("Edytor kolorów statusów")
        self.resizable(True, True)
        self.minsize(500, 360)

        # Wycentrowanie względem okna głównego
        try:
            self.update_idletasks()
            mw = master.winfo_width() if master else 1000
            mh = master.winfo_height() if master else 700
            w = max(500, int(mw * 0.45))
            h = max(360, int(mh * 0.5))
            x = (master.winfo_rootx() + (mw - w) // 2) if master else 120
            y = (master.winfo_rooty() + (mh - h) // 2) if master else 120
            self.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            self.geometry("600x420+120+120")

        self.transient(master)
        self.grab_set()

        ttk.Label(self, text="Kolory statusów", font=("Segoe UI", 12, "bold")).pack(anchor='w', padx=12, pady=(10, 6))

        # Obszar przewijany (gdy statusów jest dużo)
        container = ttk.Frame(self)
        container.pack(fill='both', expand=True, padx=10, pady=6)

        self.canvas = tk.Canvas(container, highlightthickness=0)
        self.scroll_y = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.form = ttk.Frame(self.canvas)
        self.form.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.form, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll_y.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scroll_y.pack(side="right", fill="y")

        # Nagłówki kolumn
        hdr = ttk.Frame(self.form)
        hdr.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 6))
        ttk.Label(hdr, text="Status", width=28).grid(row=0, column=0, sticky='w', padx=(0, 6))
        ttk.Label(hdr, text="Kolor (#RRGGBB)", width=18).grid(row=0, column=1, sticky='w', padx=(0, 6))
        ttk.Label(hdr, text="Podgląd", width=10).grid(row=0, column=2, sticky='w', padx=(0, 6))

        ttk.Separator(self.form, orient='horizontal').grid(row=1, column=0, columnspan=4, sticky="ew")

        self.controls = {}  # name -> {'entry':..., 'preview':...}
        self._build_rows()

        # Przyciski akcji
        btns = ttk.Frame(self)
        btns.pack(fill='x', padx=10, pady=(6, 10))
        center = ttk.Frame(btns)
        center.pack(anchor='center')
        ttk.Button(center, text="Zapisz", command=self.save, style='Accent.TButton').pack(side='left', padx=6)
        ttk.Button(center, text="Anuluj", command=self.destroy).pack(side='left', padx=6)

    def _build_rows(self):
        # Usuń stare wiersze (poniżej separatora)
        for w in self.form.grid_slaves():
            if int(w.grid_info().get('row', 99)) >= 2:
                w.destroy()

        try:
            statuses = self.emp_manager.get_statuses_config() or []
        except Exception:
            statuses = []

        if not statuses:
            ttk.Label(self.form, text="Brak zdefiniowanych statusów. Dodaj je w Ustawienia → Statusy.",
                      foreground='gray').grid(row=2, column=0, columnspan=4, sticky='w', pady=10)
            return

        self.controls.clear()
        row = 2
        for name, color in statuses:
            color = color or "#3CB371"
            ttk.Label(self.form, text=name, width=28).grid(row=row, column=0, sticky='w', padx=(0, 6), pady=4)

            entry = ttk.Entry(self.form, width=18)
            entry.insert(0, color)
            entry.grid(row=row, column=1, sticky='w', padx=(0, 6), pady=4)

            preview = tk.Label(self.form, text="      ", bg=color, relief='solid', bd=1)
            preview.grid(row=row, column=2, sticky='w', padx=(0, 6), pady=4)

            ttk.Button(self.form, text="Wybierz…",
                       command=lambda n=name: self.choose_color(n)).grid(row=row, column=3, sticky='w', padx=(0, 6), pady=4)

            self.controls[name] = {'entry': entry, 'preview': preview}
            row += 1

        # Rozciąganie kolumn
        self.form.grid_columnconfigure(0, weight=1)
        for c in (1, 2, 3):
            self.form.grid_columnconfigure(c, weight=0)

    def choose_color(self, status_name):
        ctl = self.controls.get(status_name)
        if not ctl:
            return
        current = ctl['entry'].get().strip() or "#3CB371"
        try:
            color = colorchooser.askcolor(initialcolor=current, title=f"Wybierz kolor: {status_name}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wybrać koloru: {e}")
            return
        if color and color[1]:
            ctl['entry'].delete(0, tk.END)
            ctl['entry'].insert(0, color[1])
            ctl['preview'].config(bg=color[1])

    def save(self):
        # Pobierz aktualne kolory z bazy
        try:
            current = dict(self.emp_manager.get_statuses_config() or [])
        except Exception:
            current = {}

        to_update = []
        for name, ctl in self.controls.items():
            val = (ctl['entry'].get() or "").strip()
            # prosta walidacja HEX #RRGGBB lub #RGB
            if not (val.startswith("#") and len(val) in (4, 7)):
                messagebox.showerror("Błąd", f"Nieprawidłowy kolor dla statusu '{name}': {val}")
                return
            if current.get(name) != val:
                to_update.append((name, val))

        if not to_update:
            self.destroy()
            return

        errs = 0
        for name, col in to_update:
            done = False
            # 1) Jeśli jest metoda update_status_color – użyj
            if hasattr(self.emp_manager, 'update_status_color'):
                try:
                    done = bool(self.emp_manager.update_status_color(name, col))
                except Exception:
                    done = False
            # 2) Fallback: delete + add
            if not done:
                try:
                    self.emp_manager.delete_setting('statuses', name)
                    self.emp_manager.add_setting('statuses', {'name': name, 'color': col})
                    done = True
                except Exception:
                    errs += 1

        if errs:
            messagebox.showerror("Błąd", "Nie wszystkie kolory udało się zapisać.")
        else:
            messagebox.showinfo("Sukces", "Kolory statusów zapisane.")

        # Odśwież listę pracowników (żeby kolory od razu się zmieniły)
        try:
            if hasattr(self.master, 'refresh_employee_list'):
                self.master.refresh_employee_list(self.master.filtered_data or None)
        except Exception:
            pass

        self.destroy()
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import font as tkfont
from datetime import datetime
import pandas as pd
from collections import defaultdict
from employee_management import EmployeeManagement
from db_manager import DBManager
from login_window import LoginWindow
from employee_dialog import EmployeeDialog
from settings_window import SettingsWindow
from history_window import HistoryWindow
from summary_window import SummaryWindow
from machine_dialog import MachineDialog
from vacation_dialog import VacationDialog
from l4_dialog import L4Dialog
from color_editor import ColorEditor
import json
from pathlib import Path
from tkinter import filedialog
import subprocess, sys, threading, os


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("System Zarządzania Pracownikami (Python/Tkinter)")
        self.geometry("1400x800")

        # Motywy
        self.current_theme = 'light'
        self.themes = {
            'light': self.setup_light_theme,
            'dark': self.setup_dark_theme,
            'blue': self.setup_blue_theme,
            'modern': self.setup_modern_theme
        }

        self.db_manager = DBManager()
        self.current_user = None
        self.emp_manager = EmployeeManagement(self.db_manager, self.current_user)
        self.all_employees_data = []
        self.filtered_data = []
        self.current_filters = {}
                # załaduj konfigurację aplikacji
        self._app_config = self.load_app_config()


        # Kontrola inicjalizacji i login window
        self._app_initialized = False
        self.login_win = None

        # Debounce autosize, panel historii i meta historii
        self._autosize_job = None
        self._history_pane_visible = True
        self._history_meta = None

        # NOWOŚĆ: Stos undo (lista akcji do cofnięcia)
        self.undo_stack = []
        self.undo_max_size = 10  # Maks. liczba akcji do cofnięcia

        self.setup_light_theme()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.create_login_screen()
    def open_magtank(self):
        mag_path = self._app_config.get("magtank_path", "")
        if not mag_path:
            self.show_magazyn_settings_dialog()
            return

        if not Path(mag_path).exists():
            messagebox.showerror("Błąd", f"Plik nie istnieje:\n{mag_path}")
            return

        try:
            subprocess.Popen(
                ["cmd", "/c", "start", "", mag_path],
                cwd=Path(mag_path).parent
            )
        except Exception as e:
            messagebox.showerror("Błąd uruchamiania Magazynu", str(e))


    # ---------------- MOTYWY ----------------
    def setup_light_theme(self):
        self.current_theme = 'light'
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.bg_color = '#ffffff'
        self.fg_color = '#000000'
        self.accent_color = '#007acc'

        self.configure(bg=self.bg_color)
        self.style.configure('.', background=self.bg_color, foreground=self.fg_color)

        # ✅ Ustawienia czcionek
        default_font = ('Segoe UI', 10)
        heading_font = ('Segoe UI', 10, 'bold')
        small_font = ('Segoe UI', 8)

        self.option_add("*TLabel.Font", default_font)
        self.option_add("*TButton.Font", default_font)
        self.option_add("*Treeview.Font", default_font)
        self.option_add("*Treeview.Heading.Font", heading_font)
        self.option_add("*Entry.Font", default_font)
        self.option_add("*TCombobox.Font", default_font)
        self.option_add("*Label.Font", default_font)
        self.option_add("*Button.Font", default_font)

        # ✅ Styl elementów
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color, foreground=self.fg_color)
        self.style.configure('TLabelFrame', background=self.bg_color)
        self.style.configure('TButton', background='#f0f0f0', foreground=self.fg_color)
        self.style.configure('Accent.TButton', background=self.accent_color, foreground='white')
        self.style.configure('Small.TButton', font=small_font)
        self.style.configure('Treeview', background='white', foreground='black', fieldbackground='white')
        self.style.configure('Treeview.Heading', background='#e0e0e0', foreground='black')
        # ---- Ścieżka do pliku konfiguracyjnego obok main_window.py ----
    def _config_path(self):
        try:
            base = Path(__file__).resolve().parent
        except Exception:
            base = Path(".").resolve()
        return base / "app_config.json"

    def load_app_config(self):
        p = self._config_path()
        if not p.exists():
            cfg = {"magtank_path": ""}
            try:
                p.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
            except Exception:
                pass
            return cfg
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {"magtank_path": ""}

    def save_app_config(self, cfg):
        p = self._config_path()
        try:
            p.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
            return True
        except Exception as e:
            messagebox.showerror("Błąd zapisu konfiguracji", str(e))
            return False

    # ---- Otwieranie programu magazynowego (w osobnym procesie) ----
    def open_magtank(self):
        mag_path = (self._app_config.get("magtank_path", "") if hasattr(self, "_app_config") else "")
        if not mag_path:
            # jeśli nie ustawiony — otwórz ustawienia, by użytkownik podał ścieżkę
            self.show_magazyn_settings_dialog()
            return

        if not Path(mag_path).exists():
            messagebox.showerror("Nie znaleziono pliku", f"Nie znaleziono pliku:\n{mag_path}")
            return

        def _run():
            try:
                if str(mag_path).lower().endswith(".py"):
                    subprocess.Popen([sys.executable, mag_path])
                else:
                    # .exe lub inny binarny plik
                    subprocess.Popen([mag_path])
            except Exception as e:
                # Wywołanie w wątku — komunikat w głównym wątku
                self.after(0, lambda: messagebox.showerror("Błąd uruchomienia Magazynu", str(e)))

        threading.Thread(target=_run, daemon=True).start()

    # ---- Dialog ustawień magazynu ----
    def show_magazyn_settings_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Ustawienia — Magazyn")
        dialog.transient(self)
        dialog.grab_set()
        dialog.geometry("660x160")
        dialog.resizable(False, False)

        frame = ttk.Frame(dialog, padding=12)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Ścieżka do programu magazynowego (.exe lub .py):", font=('Arial', 10)).grid(row=0, column=0, sticky='w', pady=(4,8))
        path_var = tk.StringVar(value=self._app_config.get("magtank_path", ""))

        entry = ttk.Entry(frame, textvariable=path_var, width=72)
        entry.grid(row=1, column=0, columnspan=2, sticky='w', padx=(0,4))

        def browse():
            p = filedialog.askopenfilename(
                title="Wybierz program magazynowy",
                filetypes=[("Executables / Python", "*.exe *.py"), ("Wszystkie pliki","*.*")]
            )
            if p:
                path_var.set(p)

        ttk.Button(frame, text="Wybierz plik...", command=browse).grid(row=1, column=2, padx=(6,0))

        status_label = ttk.Label(frame, text="", font=('Arial', 9), foreground='gray')
        status_label.grid(row=2, column=0, columnspan=3, sticky='w', pady=(8,0))

        def save_and_close():
            newp = path_var.get().strip()
            cfg = (self._app_config or {})
            cfg["magtank_path"] = newp
            ok = self.save_app_config(cfg)
            if ok:
                self._app_config = cfg
                status_label.config(text="Zapisano konfigurację.")
                # odśwież stan przycisku Magazyn w UI
                try:
                    self.update_mag_button_state()
                except Exception:
                    pass
                dialog.after(600, dialog.destroy)

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=3, sticky='e', pady=(12,0))
        ttk.Button(btn_frame, text="Zapisz", command=save_and_close).pack(side='right', padx=(6,0))
        ttk.Button(btn_frame, text="Anuluj", command=dialog.destroy).pack(side='right')

        dialog.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")




    def setup_dark_theme(self):
        self.current_theme = 'dark'
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.bg_color = '#2b2b2b'
        self.fg_color = '#ffffff'
        self.accent_color = '#4CAF50'
        self.tree_bg = '#3c3f41'
        self.tree_fg = '#ffffff'

        self.configure(bg=self.bg_color)
        self.style.configure('.', background=self.bg_color, foreground=self.fg_color)
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color, foreground=self.fg_color)
        self.style.configure('TLabelFrame', background=self.bg_color, foreground=self.fg_color)
        self.style.configure('TButton', background='#404040', foreground=self.fg_color)
        self.style.configure('Accent.TButton', background=self.accent_color, foreground='white')
        self.style.configure('Small.TButton', font=('Arial', 8))
        self.style.configure('Treeview', background=self.tree_bg, foreground=self.tree_fg, fieldbackground=self.tree_bg)
        self.style.configure('Treeview.Heading', background='#404040', foreground=self.fg_color)

    def setup_blue_theme(self):
        self.current_theme = 'blue'
        self.style = ttk.Style()
        self.style.theme_use('vista')

        self.bg_color = '#f0f8ff'
        self.fg_color = '#1e3a5f'
        self.accent_color = '#1e88e5'

        self.configure(bg=self.bg_color)
        self.style.configure('.', background=self.bg_color, foreground=self.fg_color)
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color, foreground=self.fg_color)
        self.style.configure('TLabelFrame', background=self.bg_color, bordercolor=self.accent_color)
        self.style.configure('TButton', background=self.accent_color, foreground='white')
        self.style.configure('Accent.TButton', background='#1565c0', foreground='white')
        self.style.configure('Small.TButton', font=('Arial', 8))
        self.style.configure('Treeview', background='white', foreground='black')
        self.style.configure('Treeview.Heading', background=self.accent_color, foreground='white')

    def setup_modern_theme(self):
        self.current_theme = 'modern'
        self.style = ttk.Style()
        self.style.theme_use('alt')

        self.bg_color = '#f8fafc'
        self.fg_color = '#2d3748'
        self.accent_color = '#667eea'

        self.configure(bg=self.bg_color)
        self.style.configure('.', background=self.bg_color, foreground=self.fg_color)
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color, foreground=self.fg_color)
        self.style.configure('TLabelFrame', background=self.bg_color, bordercolor=self.accent_color)
        self.style.configure('TButton', background=self.accent_color, foreground='white')
        self.style.configure('Accent.TButton', background='#5a67d8', foreground='white')
        self.style.configure('Small.TButton', font=('Arial', 8))
        self.style.configure('Treeview', background='white', foreground=self.fg_color)
        self.style.configure('Treeview.Heading', background=self.accent_color, foreground='white')

    def change_theme(self, theme_name):
        if theme_name in self.themes:
            self.themes[theme_name]()
            if hasattr(self, 'main_frame'):
                self.refresh_interface()

    def refresh_interface(self):
        self.refresh_employee_list()
        self.update_status_bar()

    def refresh_summary_if_open(self):
        try:
            if hasattr(self, 'summary_window') and self.summary_window and self.summary_window.winfo_exists():
                self.summary_window.apply_filters()
        except Exception:
            pass

    # ---------------- LOGOWANIE ----------------
    def create_login_screen(self):
        # schowaj główne okno
        self.withdraw()
        # zamknij poprzednie okno logowania (jeśli było)
        try:
            if self.login_win and self.login_win.winfo_exists():
                self.login_win.destroy()
        except Exception:
            pass
        # utwórz okno logowania
        self.login_win = LoginWindow(self, self.db_manager, self.on_login_success)

    def on_login_success(self, user):
        # jeśli UI już jest, tylko zamknij okno logowania
        if self._app_initialized:
            try:
                if self.login_win and self.login_win.winfo_exists():
                    self.login_win.destroy()
            except Exception:
                pass
            return

        self._app_initialized = True
        self.current_user = user
        self.emp_manager.set_current_user(user)
        self.title(f"System Zarządzania Pracownikami - Zalogowano jako: {user['username']} ({user['role']})")

        # zamknij okno logowania
        try:
            if self.login_win and self.login_win.winfo_exists():
                self.login_win.destroy()
        except Exception:
            pass

        # pokaż główne okno
        self.deiconify()
        try:
            self.state('zoomed')
        except Exception:
            pass

        # sprzątnij ewentualny stary UI
        try:
            if hasattr(self, 'notebook') and self.notebook.winfo_exists():
                self.notebook.destroy()
        except Exception:
            pass

        self.create_main_app_interface()
        self.after(5000, self.check_alerts_periodically)

    # ---------------- UI GŁÓWNE ----------------
    def create_main_app_interface(self):
        # sprzątanie (gdyby coś zostało)
        try:
            if hasattr(self, 'notebook') and self.notebook.winfo_exists():
                self.notebook.destroy()
        except Exception:
            pass
                # po zbudowaniu toolbar/okienka
        try:
            self.update_mag_button_state()
        except Exception:
            pass


        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.main_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.main_frame, text="👥 Pracownicy")

        # Zakładka Duplikaty
        self.duplicates_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.duplicates_frame, text="🔁 Duplikaty")

        self.create_employee_tab()
        self.refresh_employee_list()
        self.update_dashboard()

        # Utwórz zakładkę duplikatów
        self.create_duplicates_tab()

        self.main_frame.grid_rowconfigure(2, weight=1)  # lista (bez kafelka)
        self.main_frame.grid_rowconfigure(3, weight=1)  # lista (z kafelkiem)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.bind('<Configure>', self._on_window_configure)

    # Metoda do tworzenia zakładki Duplikaty
    def create_duplicates_tab(self):
        # Toolbar
        toolbar = ttk.Frame(self.duplicates_frame)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        ttk.Button(toolbar, text="🔄 Odśwież", command=self.refresh_duplicates_tab, width=12).pack(side='left', padx=2)
        ttk.Button(toolbar, text="✏️ Edytuj zaznaczonych", command=self.edit_selected_duplicates, width=24).pack(side='left', padx=2)
        ttk.Button(toolbar, text="🗑️ Usuń zaznaczonych", command=self.delete_selected_duplicates, width=18).pack(side='left', padx=2)
        
        # Przycisk "Usuń wszystkie duplikaty"
        ttk.Button(toolbar, text="🗑️ Usuń wszystkie duplikaty", command=self.delete_all_duplicates_dialog, width=28).pack(side='left', padx=2)

        # Label z liczbą duplikatów
        self.duplicates_count_label = ttk.Label(toolbar, text="Znaleziono 0 grup duplikatów", font=('Arial', 9))
        self.duplicates_count_label.pack(side='right', padx=10)

        # Treeview dla duplikatów (hierarchiczne)
        dup_list_frame = ttk.Frame(self.duplicates_frame)
        dup_list_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 0))

        # Kolumny: dla grup (uproszczone), dla rekordów (pełne) – szersze
        columns = ("ID", "Imię", "Nazwisko", "Stanowisko", "Wydział", "Zmiana", "Status", "Maszyna/Urządzenie")
        self.duplicates_tree = ttk.Treeview(dup_list_frame, columns=columns, show="tree headings", selectmode='extended')

        # Nagłówki i szerokości (zwiększone, stretch dla rozciągania)
        self.duplicates_tree.heading("#0", text="Grupa", anchor='w')
        self.duplicates_tree.column("#0", width=150, minwidth=120, anchor='w', stretch=False)  # Węższa grupa

        self.duplicates_tree.heading("Imię", text="Imię", anchor='center')
        self.duplicates_tree.column("Imię", width=100, minwidth=80, anchor='center', stretch=True)

        self.duplicates_tree.heading("Nazwisko", text="Nazwisko", anchor='center')
        self.duplicates_tree.column("Nazwisko", width=120, minwidth=100, anchor='center', stretch=True)

        self.duplicates_tree.heading("ID", text="ID", anchor='center')
        self.duplicates_tree.column("ID", width=60, minwidth=50, anchor='center', stretch=False)

        self.duplicates_tree.heading("Stanowisko", text="Stanowisko", anchor='center')
        self.duplicates_tree.column("Stanowisko", width=150, minwidth=120, anchor='center', stretch=True)

        self.duplicates_tree.heading("Wydział", text="Wydział", anchor='center')
        self.duplicates_tree.column("Wydział", width=120, minwidth=100, anchor='center', stretch=True)

        self.duplicates_tree.heading("Zmiana", text="Zmiana", anchor='center')
        self.duplicates_tree.column("Zmiana", width=100, minwidth=80, anchor='center', stretch=True)

        self.duplicates_tree.heading("Status", text="Status", anchor='center')
        self.duplicates_tree.column("Status", width=100, minwidth=80, anchor='center', stretch=True)

        self.duplicates_tree.heading("Maszyna/Urządzenie", text="Maszyna/Urządzenie", anchor='center')
        self.duplicates_tree.column("Maszyna/Urządzenie", width=200, minwidth=160, anchor='center', stretch=True)  # Szersza ostatnia kolumna

        v_scroll = ttk.Scrollbar(dup_list_frame, orient="vertical", command=self.duplicates_tree.yview)
        h_scroll = ttk.Scrollbar(dup_list_frame, orient="horizontal", command=self.duplicates_tree.xview)
        self.duplicates_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.duplicates_tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        dup_list_frame.grid_rowconfigure(0, weight=1)
        dup_list_frame.grid_columnconfigure(0, weight=1)

        self.duplicates_tree.bind('<Double-1>', self.on_double_click_duplicate)
        self.duplicates_tree.bind('<<TreeviewSelect>>', self.on_duplicates_selection_change)

        self.duplicates_frame.grid_rowconfigure(1, weight=1)
        self.duplicates_frame.grid_columnconfigure(0, weight=1)

        # Odśwież na starcie
        self.refresh_duplicates_tab()

    # Odświeżanie zakładki Duplikaty (z licznikiem)
    def refresh_duplicates_tab(self):
        for item in self.duplicates_tree.get_children():
            self.duplicates_tree.delete(item)

        all_emps = self.emp_manager.get_all_employees() or []
        groups = defaultdict(list)
        for emp in all_emps:
            key = (str(emp[1]).lower().strip(), str(emp[2]).lower().strip())  # Imię + Nazwisko (case-insensitive)
            groups[key].append(emp)

        dupe_groups = {k: v for k, v in groups.items() if len(v) > 1}
        
        # Aktualizuj licznik
        num_groups = len(dupe_groups)
        total_duplicates = sum(len(emps) - 1 for emps in dupe_groups.values())  # Liczba duplikatów do usunięcia
        self.duplicates_count_label.config(text=f"Znaleziono {num_groups} grup duplikatów ({total_duplicates} duplikatów)")

        if not dupe_groups:
            self.duplicates_tree.insert('', 'end', text="Brak duplikatów", values=('', '', '', '', '', '', '', ''))
            return

        for (imie_key, nazwisko_key), emps in dupe_groups.items():
            # Parent: grupa
            parent = self.duplicates_tree.insert('', 'end', text=f"Duplikat ({len(emps)} rekordów)", 
                                                 values=(imie_key.title(), nazwisko_key.title(), len(emps), '', '', '', '', ''), 
                                                 tags=('group',))
            
            # Children: rekordy
            for emp in emps:
                emp_id, imie, nazwisko, stanowisko, wydzial, zmiana, status, maszyna = emp[:8]
                self.duplicates_tree.insert(parent, 'end', values=(emp_id, imie, nazwisko, stanowisko, wydzial, zmiana, status, maszyna), tags=('record',))

        # Tagi dla stylizacji
        self.duplicates_tree.tag_configure('group', background='#FFE6E6')  # Lekko czerwony dla grup

    # Dialog wyboru dla "Usuń wszystkie duplikaty"
    def delete_all_duplicates_dialog(self):
        if not self.duplicates_count_label.cget('text').startswith('Znaleziono 0'):
            dialog = tk.Toplevel(self)
            dialog.title("Usuń wszystkie duplikaty")
            dialog.geometry("300x150")
            dialog.transient(self)
            dialog.grab_set()

            tk.Label(dialog, text="Wybierz, które wpisy usunąć:", font=('Arial', 10, 'bold')).pack(pady=10)

            keep_var = tk.StringVar(value="older")
            ttk.Radiobutton(dialog, text="Usuń nowsze wpisy (zostaw starsze)", variable=keep_var, value="older").pack(pady=2)
            ttk.Radiobutton(dialog, text="Usuń starsze wpisy (zostaw nowsze)", variable=keep_var, value="newer").pack(pady=2)

            def confirm_delete():
                keep_older = (keep_var.get() == "older")
                dialog.destroy()
                self.delete_all_duplicates(keep_older)

            ttk.Button(dialog, text="Potwierdź i usuń", command=confirm_delete).pack(pady=10)
        else:
            messagebox.showinfo("Brak duplikatów", "Nie znaleziono duplikatów do usunięcia.")

    # Usuń wszystkie duplikaty (z opcją starsze/nowsze)
    def delete_all_duplicates(self, keep_older=True):
        all_emps = self.emp_manager.get_all_employees() or []
        groups = defaultdict(list)
        for emp in all_emps:
            key = (str(emp[1]).lower().strip(), str(emp[2]).lower().strip())
            groups[key].append(emp)

        dupe_groups = {k: v for k, v in groups.items() if len(v) > 1}
        if not dupe_groups:
            messagebox.showinfo("Brak duplikatów", "Nie znaleziono duplikatów do usunięcia.")
            return

        deleted_count = 0
        groups_count = len(dupe_groups)
        for key, emps in dupe_groups.items():
            # Sortuj po ID (niższe = starsze)
            emps_sorted = sorted(emps, key=lambda e: e[0])  # Sort po ID
            if keep_older:
                to_keep = emps_sorted[0]  # Najstarszy (najniższe ID)
                to_delete = emps_sorted[1:]
            else:
                to_keep = emps_sorted[-1]  # Najnowszy (najwyższe ID)
                to_delete = emps_sorted[:-1]

            for emp in to_delete:
                emp_id = emp[0]
                emp_data = self.db_manager.fetch_one("SELECT * FROM employees WHERE id=?", (emp_id,))
                if self.emp_manager.delete_employee(emp_id):
                    self._log_history_emp("Usunięcie duplikatu (wszystkie)", f"Usunięto duplikat ID {emp_id} (zostawiono ID {to_keep[0]})", emp_id)
                    # Push undo dla delete
                    if emp_data:
                        self.push_undo_action('delete', f"Usunięcie duplikatu ID {emp_id}", data=emp_data)
                    deleted_count += 1

        messagebox.showinfo("Sukces", f"Usunięto {deleted_count} duplikatów z {groups_count} grup.\n(Zostawiono {'starsze' if keep_older else 'nowsze'} wpisy).")
        self.refresh_employee_list()
        self.refresh_duplicates_tab()
        self.refresh_summary_if_open()  # NOWOŚĆ: Odśwież podsumowanie po zmianach

    # Edytuj zaznaczonych duplikatów
    def edit_selected_duplicates(self):
        selected = self.duplicates_tree.selection()
        if not selected:
            messagebox.showwarning("Brak zaznaczenia", "Zaznacz rekordy do edycji.")
            return

        edited_count = 0
        for item in selected:
            tags = self.duplicates_tree.item(item, 'tags')
            if 'record' not in tags:  # Tylko rekordy (nie grupy)
                continue
            values = self.duplicates_tree.item(item, 'values')
            try:
                emp_id = int(values[0])  # ID z pierwszej kolumny
            except (ValueError, IndexError):
                continue  # Pomijamy, jeśli nie da się sparsować ID
            
            # Użyj bezpośredniego zapytania do DB
            data = self.db_manager.fetch_one("SELECT * FROM employees WHERE id=?", (emp_id,))
            if data:
                old_data = list(data)  # Kopia przed edycją
                dialog = EmployeeDialog(self, self.emp_manager, employee_data=data)
                self.wait_window(dialog)
                # Sprawdź zmiany i push undo
                new_data = self.db_manager.fetch_one("SELECT * FROM employees WHERE id=?", (emp_id,))
                if new_data and tuple(new_data) != tuple(old_data):
                    self.push_undo_action('edit', f"Edycja duplikatu ID {emp_id}", data=new_data, old_data=old_data)
                edited_count += 1
            else:
                print(f"Nie znaleziono danych dla ID {emp_id}")  # Debug

        if edited_count > 0:
            messagebox.showinfo("Sukces", f"Otwarto edycję dla {edited_count} rekordów.")
            self.refresh_employee_list()  # Odśwież główną listę i duplikaty
            self.refresh_duplicates_tab()
            self.refresh_summary_if_open()  # NOWOŚĆ: Odśwież podsumowanie po zmianach
        else:
            messagebox.showwarning("Brak edycji", "Nie udało się otworzyć edycji dla zaznaczonych rekordów.")

    # Usuń zaznaczonych duplikatów
    def delete_selected_duplicates(self):
        selected = self.duplicates_tree.selection()
        if not selected:
            messagebox.showwarning("Brak zaznaczenia", "Zaznacz rekordy do usunięcia.")
            return

        emp_ids = []
        for item in selected:
            tags = self.duplicates_tree.item(item, 'tags')
            if 'record' not in tags:
                continue
            values = self.duplicates_tree.item(item, 'values')
            try:
                emp_ids.append(int(values[0]))
            except (ValueError, IndexError):
                continue

        if not emp_ids:
            messagebox.showwarning("Brak rekordów", "Zaznacz tylko rekordy (nie grupy).")
            return

        if not messagebox.askyesno("Potwierdzenie", f"Usunąć {len(emp_ids)} zaznaczonych duplikatów?"):
            return

        deleted_count = 0
        for emp_id in emp_ids:
            emp_data = self.db_manager.fetch_one("SELECT * FROM employees WHERE id=?", (emp_id,))
            if self.emp_manager.delete_employee(emp_id):
                self._log_history_emp("Usunięcie duplikatu", f"Usunięto duplikat ID {emp_id}", emp_id)
                # Push undo dla delete
                if emp_data:
                    self.push_undo_action('delete', f"Usunięcie duplikatu ID {emp_id}", data=emp_data)
                deleted_count += 1

        messagebox.showinfo("Sukces", f"Usunięto {deleted_count} duplikatów.")
        self.refresh_employee_list()
        self.refresh_duplicates_tab()
        self.refresh_summary_if_open()  # NOWOŚĆ: Odśwież podsumowanie po zmianach

    # Double-click na duplikacie (edytuj)
    def on_double_click_duplicate(self, event):
        item = self.duplicates_tree.identify_row(event.y)
        if not item:
            return
        tags = self.duplicates_tree.item(item, 'tags')
        if 'record' not in tags:
            return  # Tylko rekordy, nie grupy
        values = self.duplicates_tree.item(item, 'values')
        try:
            emp_id = int(values[0])  # ID z pierwszej kolumny
        except (ValueError, IndexError):
            return
        
        # Użyj bezpośredniego zapytania do DB
        data = self.db_manager.fetch_one("SELECT * FROM employees WHERE id=?", (emp_id,))
        if data:
            self.open_edit_dialog(data)
        else:
            messagebox.showerror("Błąd", f"Nie znaleziono danych pracownika o ID {emp_id}.")

    # Zmiana zaznaczenia w duplikatach
    def on_duplicates_selection_change(self, event):
        pass  # Możesz dodać logikę, np. podgląd historii

    def create_employee_tab(self):
        self.create_toolbar(self.main_frame)
        self.create_filter_section(self.main_frame)
        self.create_employee_list_section(self.main_frame)

    def create_toolbar(self, parent):
        toolbar = ttk.Frame(parent, relief='raised', borderwidth=1)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        actions_frame = ttk.Frame(toolbar)
        actions_frame.pack(side='left', fill='x', padx=5, pady=5)

        ttk.Button(actions_frame, text="➕ Dodaj Pracownika",
                   command=self.open_add_employee_dialog, width=18).pack(side='left', padx=2)

        # NOWOŚĆ: Przycisk Cofnij (aktywny, jeśli są akcje)
        self.undo_button = ttk.Button(actions_frame, text="↶ Cofnij",
                                      command=self.undo_last_action, width=12, state='disabled')
        self.undo_button.pack(side='left', padx=2)

        group_menu = tk.Menubutton(actions_frame, text="👥 Operacje Grupowe",
                                   relief='raised', width=18)
        group_menu.pack(side='left', padx=2)
        group_menu.menu = tk.Menu(group_menu, tearoff=0)
        group_menu['menu'] = group_menu.menu
        group_menu.menu.add_command(label="📊 Status", command=self.bulk_change_status)
        group_menu.menu.add_command(label="➡️ Przeniesienie", command=self.bulk_move_employees)
        group_menu.menu.add_command(label="⚙️ Maszyna", command=self.bulk_change_machine)
        group_menu.menu.add_separator()
        group_menu.menu.add_command(label="🔍 Bez Stanowiska", command=self.find_without_position)
        group_menu.menu.add_command(label="🔍 Bez Wydziału", command=self.find_without_department)
        group_menu.menu.add_command(label="🔍 Bez Maszyny", command=self.find_without_machine)
        group_menu.menu.add_command(label="🔍 Wszystkie Braki", command=self.find_all_missing_data)
        group_menu.menu.add_separator()
        group_menu.menu.add_command(label="🗑️ Usuń Zaznaczonych", command=self.bulk_delete_employees)

        ttk.Button(actions_frame, text="📊 Podsumowanie",
                   command=self.show_summary, width=18).pack(side='left', padx=2)
        ttk.Button(actions_frame, text="📋 Historia",
                   command=self.show_history, width=12).pack(side='left', padx=2)

        # Przełącznik bocznego podglądu historii
        ttk.Button(actions_frame, text="🕘 Podgląd historii",
                   command=self.toggle_side_history, width=18).pack(side='left', padx=2)

        ttk.Button(actions_frame, text="🎨 Kolory",
                   command=self.show_color_editor, width=12).pack(side='left', padx=2)
                # Magazyn — przycisk, który uruchamia program jeśli ustawiony, inaczej otwiera ustawienia
        self.mag_button = ttk.Button(actions_frame, text="📦 Magazyn", command=self.open_magtank, width=12)
        self.mag_button.pack(side='left', padx=2)


        user_frame = ttk.Frame(toolbar)
        user_frame.pack(side='right', fill='x', padx=5, pady=5)

        ttk.Label(user_frame, text=f"👤 {self.current_user['username']} | 🎭 {self.current_user['role']}",
                  font=('Arial', 9)).pack(side='left', padx=5)

        ttk.Label(user_frame, text="Motyw:").pack(side='left', padx=(10, 2))
        self.theme_var = tk.StringVar(value=self.current_theme)
        theme_combo = ttk.Combobox(user_frame, textvariable=self.theme_var,
                                   values=list(self.themes.keys()),
                                   state='readonly', width=10)
        theme_combo.pack(side='left', padx=2)
        theme_combo.bind('<<ComboboxSelected>>', lambda e: self.change_theme(self.theme_var.get()))

        ttk.Button(user_frame, text="⚙️", width=3,
                   command=self.show_settings).pack(side='left', padx=2)
        ttk.Button(user_frame, text="🚪", width=3,
                   command=self.logout).pack(side='left', padx=2)
    def update_mag_button_state(self):
        """Ustaw stan i tooltip/przyciski zależnie od tego czy ścieżka do magazynu jest ustawiona."""
        mag_path = (self._app_config.get("magtank_path", "") if hasattr(self, "_app_config") else "")
        if mag_path and Path(mag_path).exists():
            try:
                self.mag_button.state(["!disabled"])
            except Exception:
                self.mag_button.config(state="normal")
        else:
            try:
                self.mag_button.state(["disabled"])
            except Exception:
                self.mag_button.config(state="disabled")


    def create_filter_section(self, parent):
        filter_frame = ttk.LabelFrame(parent, text="🔍 Filtrowanie", padding="8")
        filter_frame.grid(row=1, column=0, sticky="ew", pady=(0, 0))

        self.filters = {}
        self.dynamic_filter_vars = {}
        filter_cols = ["Wydział", "Zmiana", "Status", "Stanowisko", "Maszyna"]

        for i, col in enumerate(filter_cols):
            ttk.Label(filter_frame, text=f"{col}:").grid(row=0, column=i*2, padx=4, pady=2, sticky='w')
            self.dynamic_filter_vars[col] = tk.StringVar()
            combo = ttk.Combobox(filter_frame, textvariable=self.dynamic_filter_vars[col],
                                 state='readonly', width=15)
            combo.grid(row=0, column=i*2+1, padx=4, pady=2, sticky='ew')
            combo.bind('<<ComboboxSelected>>', self.apply_filters)
            self.filters[col] = combo

        ttk.Label(filter_frame, text="Nazwisko:").grid(row=0, column=len(filter_cols)*2, padx=4, pady=2, sticky='w')
        self.nazwisko_entry = ttk.Entry(filter_frame, width=15)
        self.nazwisko_entry.grid(row=0, column=len(filter_cols)*2+1, padx=4, pady=2, sticky='ew')
        self.nazwisko_entry.bind('<KeyRelease>', self.apply_filters)

        ttk.Button(filter_frame, text="🗑️ Wyczyść Filtry",
                   command=self.reset_filters).grid(row=0, column=len(filter_cols)*2+2, padx=4, pady=2)

        for i in range(len(filter_cols)*2 + 3):
            filter_frame.columnconfigure(i, weight=1)

        self.update_dynamic_filters()

    def create_employee_list_section(self, parent):
        """Lista tuż pod filtrami; po prawej boczny podgląd historii w PanedWindow."""
        # Kafelek (na starcie niewidoczny)
        self.summary_tile_frame = ttk.LabelFrame(parent, text="🎯 Podsumowanie Filtrowania", padding="5")
        self.summary_content_frame = ttk.Frame(self.summary_tile_frame)

        # Holder (przesuwany między row=2 a row=3)
        self.list_holder = ttk.Frame(parent)
        self.list_holder.grid(row=2, column=0, sticky="nsew", pady=(0, 0))

        # PanedWindow poziomy
        self.paned = ttk.Panedwindow(self.list_holder, orient='horizontal')
        self.paned.pack(fill='both', expand=True)

        # Lewy panel: lista pracowników
        self.list_frame = ttk.Frame(self.paned)
        self.paned.add(self.list_frame, weight=3)

        columns = ("ID", "Imię", "Nazwisko", "Stanowisko", "Wydział", "Zmiana",
                   "Status", "Maszyna/Urządzenie", "Urlop od-do", "L4 od-do")
        self.employee_tree = ttk.Treeview(self.list_frame, columns=columns, show="headings", selectmode='extended')

        for col in columns:
            self.employee_tree.heading(col, text=col, anchor='center',
                                       command=lambda c=col: self.sort_column(self.employee_tree, c, False))
            self.employee_tree.column(col, width=80, anchor='center', stretch=False)

        self.employee_tree.column("Urlop od-do", width=140, minwidth=110, anchor='center', stretch=False)
        self.employee_tree.column("L4 od-do",    width=200, minwidth=180, anchor='center', stretch=False)

        v_scroll = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.employee_tree.yview)
        h_scroll = ttk.Scrollbar(self.list_frame, orient="horizontal", command=self.employee_tree.xview)
        self.employee_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.employee_tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        self.list_frame.grid_rowconfigure(0, weight=1)
        self.list_frame.grid_columnconfigure(0, weight=1)

        self.employee_tree.bind('<Double-1>', self.on_double_click_employee)
        self.employee_tree.bind('<Button-3>', self.show_context_menu)
        self.employee_tree.bind('<<TreeviewSelect>>', self.on_selection_change)
        self.employee_tree.bind('<Configure>', self._on_tree_configure)

        # Prawy panel: podgląd historii
        self.history_side_frame = self.create_history_side_panel()
        self.paned.add(self.history_side_frame, weight=1)

        # Grid weights
        parent.grid_rowconfigure(2, weight=1)
        parent.grid_rowconfigure(3, weight=1)
        parent.grid_columnconfigure(0, weight=1)

    # PRAWY PANEL HISTORII
    def create_history_side_panel(self):
        side = ttk.Frame(self.paned)

        header = ttk.Frame(side)
        header.pack(fill='x', padx=6, pady=(6, 4))
        ttk.Label(header, text="📋 Historia (podgląd)", font=('Arial', 10, 'bold')).pack(side='left')

        cols = ('Czas', 'Operator', 'Akcja', 'Szczegóły')
        self.history_tree = ttk.Treeview(side, columns=cols, show='headings', height=12)
        for c in cols:
            self.history_tree.heading(c, text=c, anchor='center')
            self.history_tree.column(c, anchor='center', stretch=True, width=120)
        self.history_tree.column('Szczegóły', anchor='w', width=260)

        yscroll = ttk.Scrollbar(side, orient='vertical', command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=yscroll.set)

        self.history_tree.pack(side='left', fill='both', expand=True, padx=(6,0), pady=(0,6))
        yscroll.pack(side='left', fill='y', padx=(0,6), pady=(0,6))
        return side

    # WSPARCIE HISTORII (detekcja i logowanie)
    def _detect_history_table_and_columns(self):
        candidates = ['history', 'historia', 'employee_history', 'log_history', 'logs']
        for t in candidates:
            try:
                info = self.emp_manager.db.fetch_all(f"PRAGMA table_info({t})")
            except Exception:
                info = []
            cols = [row[1] for row in info] if info else []
            if not cols:
                continue
            lower = [c.lower() for c in cols]
            def find(names):
                for n in names:
                    if n in lower:
                        return cols[lower.index(n)]
                return None
            ts = find(['timestamp', 'czas', 'date', 'created_at', 'created', 'ts', 'data', 'datetime'])
            action = find(['action', 'akcja', 'type', 'event', 'operation'])
            details = find(['details', 'szczegoly', 'message', 'opis', 'info', 'detail', 'msg'])
            emp = find(['employee_id', 'pracownik_id', 'emp_id', 'id_pracownika'])
            if not ts:
                ts = 'rowid'
            return {'table': t, 'ts': ts, 'action': action, 'details': details, 'emp': emp}
        return None

    def _get_emp_row(self, emp_id):
        try:
            return self.emp_manager.db.fetch_one(
                "SELECT id, imie, nazwisko, stanowisko, wydzial, zmiana, status, maszyna FROM employees WHERE id=?",
                (emp_id,)
            )
        except Exception:
            return None

    def _log_history_emp(self, action, details, emp_id):
        try:
            return self.emp_manager.log_history(action, details, employee_id=emp_id)
        except TypeError:
            try:
                return self.emp_manager.log_history(action, details, emp_id)
            except Exception:
                try:
                    return self.emp_manager.log_history(action, f"[EMP:{emp_id}] {details}")
                except Exception:
                    pass

    def _log_field_change(self, emp_id, label, old, new):
        if old == new:
            return
        action = f"Zmiana {label.lower()}"
        details = f"Zmieniono {label.lower()}: {old or '-'} -> {new or '-'}"
        self._log_history_emp(action, details, emp_id)

    def populate_side_history(self):
        if not hasattr(self, 'history_tree'):
            return
        for i in self.history_tree.get_children():
            self.history_tree.delete(i)

        sel = self.employee_tree.selection()
        if not sel:
            self.history_tree.insert('', 'end', values=('', '', 'Wybierz pracownika', ''))
            return

        try:
            emp_id = int(self.employee_tree.item(sel[0], 'values')[0])
        except Exception:
            self.history_tree.insert('', 'end', values=('', '', 'Wybierz pracownika', ''))
            return

        rows = []
        try:
            rows = self.emp_manager.get_employee_history(emp_id)
        except Exception:
            pass
        if not rows:
            try:
                rows = self.emp_manager.get_history(employee_id=emp_id, limit=50)
            except Exception:
                rows = []
        if not rows:
            if not self._history_meta:
                self._history_meta = self._detect_history_table_and_columns()
            meta = self._history_meta
            if meta:
                try:
                    if meta['emp']:
                        sql = f"SELECT {meta['ts']}, {meta['action'] or 'NULL'}, {meta['details'] or 'NULL'} " \
                              f"FROM {meta['table']} WHERE {meta['emp']}=? " \
                              f"ORDER BY {meta['ts']} DESC LIMIT 50"
                        rows = self.emp_manager.db.fetch_all(sql, (emp_id,))
                    elif meta['details']:
                        sql = f"SELECT {meta['ts']}, {meta['action'] or 'NULL'}, {meta['details']} " \
                              f"FROM {meta['table']} WHERE {meta['details']} LIKE ? " \
                              f"ORDER BY {meta['ts']} DESC LIMIT 50"
                        rows = self.emp_manager.db.fetch_all(sql, (f"%{emp_id}%",))
                    else:
                        sql = f"SELECT {meta['ts']}, {meta['action'] or 'NULL'}, {meta['details'] or 'NULL'} " \
                              f"FROM {meta['table']} ORDER BY {meta['ts']} DESC LIMIT 20"
                        rows = self.emp_manager.db.fetch_all(sql)
                except Exception:
                    rows = []
        if not rows:
            try:
                rows = self.emp_manager.get_history(limit=20)
            except Exception:
                rows = []

        if not rows:
            self.history_tree.insert('', 'end', values=('', '', 'Brak wpisów historii', ''))
            return

        for r in rows:
            if isinstance(r, dict):
                ts = r.get('timestamp') or r.get('time') or r.get('date') or ''
                action = r.get('action') or r.get('type') or ''
                details = r.get('details') or r.get('message') or ''
            else:
                if len(r) >= 3:
                    ts, action, details = r[0], r[1], r[2]
                elif len(r) == 2:
                    ts, action, details = r[0], r[1], ''
                else:
                    ts, action, details = '', str(r), ''
            self.history_tree.insert('', 'end', values=(ts, op if 'op' in locals() else '', action, details))

    def toggle_side_history(self):
        if not hasattr(self, 'history_side_frame'):
            return
        if self._history_pane_visible:
            try:
                self.paned.forget(self.history_side_frame)
            except Exception:
                pass
            self._history_pane_visible = False
        else:
            try:
                self.paned.add(self.history_side_frame)
            except Exception:
                pass
            self._history_pane_visible = True
        self.schedule_autosize()

    # ---------------- FILTRY / DANE ----------------
    def update_dynamic_filters(self):
        wydzialy_list = self.emp_manager.get_setting('wydzialy') or []
        shifts_config = self.emp_manager.get_shifts_config() or []
        statuses_config = self.emp_manager.get_statuses_config() or []
        stanowiska_list = self.emp_manager.get_setting('stanowiska') or []
        maszyny_list = self.emp_manager.get_setting('maszyny') or []

        self.filters["Wydział"]['values'] = [''] + list(wydzialy_list)
        self.filters["Zmiana"]['values'] = [''] + [s[0] for s in shifts_config]
        self.filters["Status"]['values'] = [''] + [s[0] for s in statuses_config]
        self.filters["Stanowisko"]['values'] = [''] + list(stanowiska_list)
        self.filters["Maszyna"]['values'] = [''] + list(maszyny_list)

    def refresh_employee_list(self, filter_data=None):
        if filter_data is None:
            self.all_employees_data = self.emp_manager.get_all_employees()
            data_to_display = self.all_employees_data
        else:
            data_to_display = filter_data

        for item in self.employee_tree.get_children():
            self.employee_tree.delete(item)

        status_colors = {name: color for name, color in (self.emp_manager.get_statuses_config() or [])}

        vacations = self.emp_manager.get_vacations() or []
        l4_records = self.emp_manager.get_l4_records() or []
        vacation_map = {v[1]: f"{v[2]} - {v[3]}" for v in vacations}
        l4_map = {l[1]: f"{l[2]} - {l[3]}" for l in l4_records}

        overflow_data = {}
        for emp in data_to_display:
            wydzial, zmiana, status = emp[4], emp[5], emp[6]
            if status == "W Pracy" and (zmiana and "Wolne" not in zmiana):
                key = (wydzial, zmiana)
                if key not in overflow_data:
                    required = self.emp_manager.get_required_staff_by_wydzial_shift(wydzial, zmiana)
                    current_count = len([e for e in data_to_display
                                         if e[4] == wydzial and e[5] == zmiana and e[6] == "W Pracy"])
                    overflow_data[key] = {
                        'required': required,
                        'current': current_count,
                        'overflow': (current_count > required) if (required and required > 0) else False
                    }

        for emp in data_to_display:
            emp_id, imie, nazwisko, stanowisko, wydzial, zmiana, status, maszyna = emp
            vacation_info = vacation_map.get(emp_id, "")
            l4_info = l4_map.get(emp_id, "")

            # oblicz dynamiczny opis zmiany wg tabeli shifts
            try:
                zm_key = self.emp_manager.normalize_shift_key(zmiana) if zmiana else ''
                zmiana_display = self.emp_manager.get_shift_full_name(zm_key) if zm_key else (zmiana or '')
            except Exception:
                zmiana_display = zmiana or ''
            values = (emp_id, imie, nazwisko, stanowisko, wydzial, zmiana_display, status, maszyna, vacation_info, l4_info)

            color_tag = (status or '').replace(' ', '_') or 'STATUS_NONE'
            self.employee_tree.tag_configure(color_tag, background=status_colors.get(status, 'white'))

            tags = [color_tag]
            if status == "W Pracy" and (zmiana and "Wolne" not in zmiana):
                key = (wydzial, zmiana)
                if key in overflow_data and overflow_data[key]['overflow']:
                    self.employee_tree.tag_configure('OVERFLOW', background='#FFF0E0')
                    tags.append('OVERFLOW')

            self.employee_tree.insert("", tk.END, values=values, tags=tuple(tags))

        # jeśli panel historii włączony i nic nie zaznaczono – zaznacz pierwszy
        if self._history_pane_visible and not self.employee_tree.selection():
            children = self.employee_tree.get_children('')
            if children:
                self.employee_tree.selection_set(children[0])

        self.update_status_bar()
        self.on_selection_change(None)
        self.update_dashboard()
        # Odśwież zakładkę duplikatów po zmianach
        if hasattr(self, 'duplicates_tree'):
            self.refresh_duplicates_tab()
        # UWAGA: bez nawiasów – przekazujemy referencję
        self.after_idle(self.schedule_autosize)
        self.refresh_summary_if_open()  # NOWOŚĆ: Odśwież podsumowanie po zmianach w liście

    # Autosize kolumn – wyśrodkowanie + limity (L4/Urlop węższe)
    def auto_size_employee_tree(self, max_col_widths=None, sample_limit=600):
        tv = getattr(self, 'employee_tree', None)
        if not tv:
            return
        rows = tv.get_children("")
        if not rows:
            return

        default_max = {
            "ID": 54, "Imię": 120, "Nazwisko": 150, "Stanowisko": 190,
            "Wydział": 170, "Zmiana": 160, "Status": 120, "Maszyna/Urządzenie": 180,
            "Urlop od-do": 140, "L4 od-do": 200  # Zwiększony limit
        }
        if max_col_widths:
            default_max.update(max_col_widths)

        min_widths = {
            "ID": 44, "Imię": 80, "Nazwisko": 100, "Stanowisko": 120,
            "Wydział": 120, "Zmiana": 120, "Status": 100, "Maszyna/Urządzenie": 120,
            "Urlop od-do": 110, "L4 od-do": 180  # Zwiększony min
        }

        try:
            font_data = tkfont.nametofont("TkDefaultFont")
            font_head = tkfont.nametofont("TkHeadingFont")
        except Exception:
            font_data = tkfont.Font()
            font_head = font_data

        sample = rows[:sample_limit]

        for col in tv["columns"]:
            header_text = tv.heading(col).get("text", col)
            w_header = font_head.measure(str(header_text)) + 24

            w_data = 0
            for iid in sample:
                val = tv.set(iid, col)
                w_data = max(w_data, font_data.measure(str(val)) + 18)

            width = max(min_widths.get(col, 60),
                        min(max(w_header, w_data), default_max.get(col, 300)))  # Zwiększony globalny limit

            tv.heading(col, anchor='center')
            tv.column(col, width=int(width), stretch=False, anchor='center')

    def schedule_autosize(self):
        if self._autosize_job:
            try:
                self.after_cancel(self._autosize_job)
            except Exception:
                pass
        self._autosize_job = self.after(80, self.auto_size_employee_tree)

    def _on_tree_configure(self, event):
        self.schedule_autosize()

    def _on_window_configure(self, event):
        self.schedule_autosize()

    def apply_filters(self, event=None):
        filtered_data = []

        filter_wydzial = self.dynamic_filter_vars["Wydział"].get()
        filter_zmiana = self.dynamic_filter_vars["Zmiana"].get()
        filter_status = self.dynamic_filter_vars["Status"].get()
        filter_stanowisko = self.dynamic_filter_vars["Stanowisko"].get()
        filter_maszyna = self.dynamic_filter_vars["Maszyna"].get()
        filter_nazwisko = self.nazwisko_entry.get().strip().lower()

        for emp in self.all_employees_data:
            match_wydzial = not filter_wydzial or emp[4] == filter_wydzial
            match_zmiana = not filter_zmiana or emp[5] == filter_zmiana
            match_status = not filter_status or emp[6] == filter_status
            match_stanowisko = not filter_stanowisko or emp[3] == filter_stanowisko
            match_maszyna = not filter_maszyna or emp[7] == filter_maszyna
            match_nazwisko = not filter_nazwisko or (emp[2] and filter_nazwisko in str(emp[2]).lower())

            if match_wydzial and match_zmiana and match_status and match_stanowisko and match_maszyna and match_nazwisko:
                filtered_data.append(emp)

        self.filtered_data = filtered_data
        self.refresh_employee_list(filtered_data)

        if filter_wydzial or filter_zmiana or filter_status or filter_stanowisko or filter_maszyna or filter_nazwisko:
            self.show_summary_tile(filtered_data, filter_wydzial, filter_zmiana, filter_status)
        else:
            self.hide_summary_tile()

        # jeśli dokładnie 1 pracownik – zaznacz i pokaż historię
        if len(self.filtered_data) == 1:
            target_id = self.filtered_data[0][0]
            for iid in self.employee_tree.get_children(''):
                try:
                    row_id = int(self.employee_tree.set(iid, "ID"))
                except Exception:
                    continue
                if row_id == target_id:
                    self.employee_tree.selection_set(iid)
                    self.employee_tree.see(iid)
                    break
            self.populate_side_history()
        self.refresh_summary_if_open()  # NOWOŚĆ: Odśwież podsumowanie po filtrach

    def show_summary_tile(self, filtered_data, filter_wydzial, filter_zmiana, filter_status):
        if not self.summary_tile_frame.winfo_ismapped():
            self.summary_tile_frame.grid(row=2, column=0, sticky="ew", pady=(0, 6))
            self.list_holder.grid_configure(row=3)

        for w in self.summary_content_frame.winfo_children():
            w.destroy()
        self.summary_content_frame.pack_forget()
        self.summary_content_frame = ttk.Frame(self.summary_tile_frame)
        self.summary_content_frame.pack(fill='both', expand=True)

        header_frame = ttk.Frame(self.summary_content_frame)
        header_frame.pack(fill='x', pady=3)

        filters_applied = []
        if filter_wydzial:
            filters_applied.append(f"🏭 {filter_wydzial}")
        if filter_zmiana:
            filters_applied.append(f"🕐 {filter_zmiana}")
        if filter_status:
            filters_applied.append(f"📊 {filter_status}")
        filter_text = " • ".join(filters_applied) if filters_applied else "👥 Wszyscy pracownicy"

        main_info_frame = ttk.Frame(header_frame)
        main_info_frame.pack(fill='x')

        tk.Label(main_info_frame, text=f"📋 {len(filtered_data)}",
                 font=('Arial', 14, 'bold'), fg='#1E6FBA', bg=self.bg_color).pack(side='left', padx=(0, 10))
        tk.Label(main_info_frame, text=filter_text,
                 font=('Arial', 9), fg='#666666', bg=self.bg_color).pack(side='left')

        ttk.Button(main_info_frame, text="✕", width=2,
                   command=self.hide_summary_tile, style='Small.TButton').pack(side='right')

        status_counts = self.calculate_status_counts(filtered_data)
        if any(c > 0 for c in status_counts.values()):
            stats_frame = ttk.Frame(self.summary_content_frame)
            stats_frame.pack(fill='x', pady=2)
            emoji = {"W Pracy": "🟢", "Urlop": "🟠", "L4": "🔴", "Wolne": "🟢"}
            parts = [f"{emoji.get(k,'▪')} {k}: {v}" for k, v in status_counts.items() if v > 0]
            if parts:
                tk.Label(stats_frame, text="  ".join(parts),
                         font=('Arial', 8), fg='#444444', bg=self.bg_color).pack()

    def hide_summary_tile(self):
        if self.summary_tile_frame.winfo_ismapped():
            self.summary_tile_frame.grid_remove()
        self.list_holder.grid_configure(row=2)
        self.schedule_autosize()

    def calculate_status_counts(self, employees):
        cnt = {"W Pracy": 0, "Urlop": 0, "L4": 0, "Wolne": 0}
        for emp in employees:
            s = emp[6]
            if s in cnt:
                cnt[s] += 1
        return cnt

    def reset_filters(self):
        self.dynamic_filter_vars["Wydział"].set('')
        self.dynamic_filter_vars["Zmiana"].set('')
        self.dynamic_filter_vars["Status"].set('')
        self.dynamic_filter_vars["Stanowisko"].set('')
        self.dynamic_filter_vars["Maszyna"].set('')
        self.nazwisko_entry.delete(0, tk.END)
        self.refresh_employee_list()
        self.hide_summary_tile()
        self.refresh_summary_if_open()  # NOWOŚĆ: Odśwież podsumowanie po reset

    # ---------------- TREEVIEW HELPERS ----------------
    def sort_column(self, tree, col, reverse):
        l = [(tree.set(k, col), k) for k in tree.get_children('')]
        if col == "ID":
            def key_fn(t):
                try:
                    return int(t[0])
                except Exception:
                    return t[0]
            l.sort(key=key_fn, reverse=reverse)
        else:
            l.sort(key=lambda t: str(t[0]).lower(), reverse=reverse)

        for index, (val, k) in enumerate(l):
            tree.move(k, '', index)
        tree.heading(col, command=lambda: self.sort_column(tree, col, not reverse))

    def get_selected_employee_ids(self):
        selected_items = self.employee_tree.selection()
        selected_ids = []
        for item in selected_items:
            values = self.employee_tree.item(item, 'values')
            try:
                selected_ids.append(int(values[0]))
            except Exception:
                continue
        return selected_ids

    def get_selected_employee_data(self):
        selected_item = self.employee_tree.selection()
        if selected_item:
            values = self.employee_tree.item(selected_item[0], 'values')
            emp_id = values[0]
            full_data = self.emp_manager.db.fetch_one("SELECT * FROM employees WHERE id=?", (emp_id,))
            return full_data
        return None

    def on_double_click_employee(self, event):
        data = self.get_selected_employee_data()
        if data:
            self.open_edit_dialog(data)

    def on_selection_change(self, event):
        self.populate_side_history()

    # ---------------- MENU KONTEKSTOWE ----------------
    def show_context_menu(self, event):
        item_id = self.employee_tree.identify_row(event.y)
        if not item_id:
            return
        self.employee_tree.selection_set(item_id)
        data = self.get_selected_employee_data()
        if not data:
            return

        emp_id = data[0]
        emp_name = f"{data[1]} {data[2]}"
        cur_machine = data[7]

        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="✏️ Edytuj Pracownika", command=lambda d=data: self.open_edit_dialog(d))
        menu.add_separator()

        menu.add_command(label="🏖️ Planuj urlop",
                         command=lambda: VacationDialog(self, self.emp_manager, emp_id, emp_name))
        menu.add_command(label="🏥 Zarejestruj L4",
                         command=lambda: L4Dialog(self, self.emp_manager, emp_id, emp_name))

        move_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="➡️ Przenieś", menu=move_menu)

        wydzial_menu = tk.Menu(move_menu, tearoff=0)
        move_menu.add_cascade(label="Zmień Wydział na...", menu=wydzial_menu)
        for wydzial in (self.emp_manager.get_setting('wydzialy') or []):
            wydzial_menu.add_command(label=wydzial,
                                     command=lambda w=wydzial: self.safe_move_employee(emp_id, new_wydzial=w))

        zmiana_menu = tk.Menu(move_menu, tearoff=0)
        move_menu.add_cascade(label="Zmień Zmianę na...", menu=zmiana_menu)
        for zmiana in [s[0] for s in (self.emp_manager.get_shifts_config() or [])]:
            zmiana_menu.add_command(label=zmiana,
                                    command=lambda z=zmiana: self.safe_move_employee(emp_id, new_zmiana=z))

        stanowisko_menu = tk.Menu(move_menu, tearoff=0)
        move_menu.add_cascade(label="Zmień Stanowisko na...", menu=stanowisko_menu)
        for stanowisko in (self.emp_manager.get_setting('stanowiska') or []):
            stanowisko_menu.add_command(label=stanowisko,
                                        command=lambda s=stanowisko: self.safe_move_employee(emp_id, new_stanowisko=s))

        menu.add_separator()

        status_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="🔄 Zmień Status na...", menu=status_menu)
        for status in [s[0] for s in (self.emp_manager.get_statuses_config() or [])]:
            status_menu.add_command(label=status,
                                    command=lambda s=status: self.change_status_action(emp_id, s))

        menu.add_command(label="⚙️ Zmień Maszynę/Urządzenie",
                         command=lambda: MachineDialog(self, self.emp_manager, emp_id, emp_name, cur_machine))

        menu.add_separator()
        menu.add_command(label="🗑️ Usuń Pracownika", command=lambda: self.delete_employee_action(emp_id))

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            try:
                menu.grab_release()
            except Exception:
                pass

    def open_edit_dialog(self, employee_data):
        # Zapisz stare dane przed edycją
        old_data = list(employee_data)  # Kopia
        dialog = EmployeeDialog(self, self.emp_manager, employee_data=employee_data)
        self.wait_window(dialog)
        
        # Po edycji: sprawdź, czy dane się zmieniły, i dodaj do undo
        emp_id = old_data[0]
        try:
            new_data = self.db_manager.fetch_one("SELECT * FROM employees WHERE id=?", (emp_id,))
            if new_data and tuple(new_data) != tuple(old_data):  # POPRAWKA: tuple() dla porównania
                self.push_undo_action('edit', f"Edycja pracownika {old_data[1]} {old_data[2]} (ID: {emp_id})", 
                                      data=new_data, old_data=old_data)
                print(f"DEBUG: Dodano push edit dla ID {emp_id}")
        except Exception as e:
            print(f"DEBUG Błąd push edit: {e}")
        
        self.refresh_employee_list()
        self.apply_filters()
        self.refresh_summary_if_open()  # NOWOŚĆ: Odśwież podsumowanie po edycji

    # ---------------- OPERACJE GRUPOWE + DOKŁADNE LOGI ----------------
    def bulk_change_status(self):
        selected_ids = self.get_selected_employee_ids()
        if not selected_ids:
            messagebox.showwarning("Brak zaznaczenia", "Zaznacz przynajmniej jednego pracownika.")
            return

        status_dialog = tk.Toplevel(self)
        status_dialog.title("Grupowa zmiana statusu")
        status_dialog.geometry("300x150")
        status_dialog.transient(self)
        status_dialog.grab_set()

        tk.Label(status_dialog, text=f"Zmiana statusu dla {len(selected_ids)} pracowników",
                 font=('Arial', 10, 'bold')).pack(pady=10)

        status_var = tk.StringVar()
        status_combo = ttk.Combobox(status_dialog, textvariable=status_var,
                                    values=[s[0] for s in (self.emp_manager.get_statuses_config() or [])],
                                    state='readonly')
        status_combo.pack(pady=5)

        def apply_bulk_status():
            new_status = status_var.get()
            if not new_status:
                messagebox.showwarning("Błąd", "Wybierz status.")
                return
            success_count = 0
            for emp_id in selected_ids:
                old_row = self._get_emp_row(emp_id)
                old_status = old_row[6] if old_row else None
                old_data = self.db_manager.fetch_one("SELECT * FROM employees WHERE id=?", (emp_id,))
                if self.emp_manager.update_employee_status(emp_id, new_status):
                    success_count += 1
                    self._log_field_change(emp_id, "Status", old_status, new_status)
                    # Push undo dla edit
                    new_data = self.db_manager.fetch_one("SELECT * FROM employees WHERE id=?", (emp_id,))
                    if new_data and old_data:
                        self.push_undo_action('edit', f"Grupowa zmiana statusu ID {emp_id}", data=new_data, old_data=old_data)
            status_dialog.destroy()
            messagebox.showinfo("Sukces", f"Zmieniono status dla {success_count}/{len(selected_ids)} pracowników.")
            self.refresh_employee_list()
            self.apply_filters()
            self.refresh_summary_if_open()  # NOWOŚĆ: Odśwież podsumowanie po zmianach grupowych

        ttk.Button(status_dialog, text="Zastosuj", command=apply_bulk_status).pack(pady=10)
        status_dialog.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (status_dialog.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (status_dialog.winfo_height() // 2)
        status_dialog.geometry(f'+{x}+{y}')

    def bulk_move_employees(self):
        selected_ids = self.get_selected_employee_ids()
        if not selected_ids:
            messagebox.showwarning("Brak zaznaczenia", "Zaznacz przynajmniej jednego pracownika.")
            return

        move_dialog = tk.Toplevel(self)
        move_dialog.title("Grupowe przeniesienie")
        move_dialog.geometry("350x220")
        move_dialog.transient(self)
        move_dialog.grab_set()

        tk.Label(move_dialog, text=f"Przeniesienie {len(selected_ids)} pracowników",
                 font=('Arial', 10, 'bold')).pack(pady=10)

        wydzial_frame = ttk.Frame(move_dialog); wydzial_frame.pack(fill='x', padx=20, pady=5)
        tk.Label(wydzial_frame, text="Nowy wydział:").pack(side='left')
        wydzial_var = tk.StringVar()
        ttk.Combobox(wydzial_frame, textvariable=wydzial_var,
                     values=(self.emp_manager.get_setting('wydzialy') or []),
                     state='readonly').pack(side='left', padx=10)

        zmiana_frame = ttk.Frame(move_dialog); zmiana_frame.pack(fill='x', padx=20, pady=5)
        tk.Label(zmiana_frame, text="Nowa zmiana:").pack(side='left')
        zmiana_var = tk.StringVar()
        ttk.Combobox(zmiana_frame, textvariable=zmiana_var,
                     values=[s[0] for s in (self.emp_manager.get_shifts_config() or [])],
                     state='readonly').pack(side='left', padx=10)

        stanowisko_frame = ttk.Frame(move_dialog); stanowisko_frame.pack(fill='x', padx=20, pady=5)
        tk.Label(stanowisko_frame, text="Nowe stanowisko:").pack(side='left')
        stanowisko_var = tk.StringVar()
        ttk.Combobox(stanowisko_frame, textvariable=stanowisko_var,
                     values=(self.emp_manager.get_setting('stanowiska') or []),
                     state='readonly').pack(side='left', padx=10)

        def apply_bulk_move():
            new_wydzial = wydzial_var.get() or None
            new_zmiana = zmiana_var.get() or None
            new_stanowisko = stanowisko_var.get() or None
            if not any([new_wydzial, new_zmiana, new_stanowisko]):
                messagebox.showwarning("Błąd", "Wybierz przynajmniej jeden parametr do zmiany.")
                return
            success_count = 0
            for emp_id in selected_ids:
                old_data = self.db_manager.fetch_one("SELECT * FROM employees WHERE id=?", (emp_id,))
                if self.safe_move_employee(emp_id, new_wydzial, new_zmiana, new_stanowisko):
                    success_count += 1
                    # Push undo dla edit (po zmianie)
                    new_data = self.db_manager.fetch_one("SELECT * FROM employees WHERE id=?", (emp_id,))
                    if new_data and old_data:
                        self.push_undo_action('edit', f"Grupowe przeniesienie ID {emp_id}", data=new_data, old_data=old_data)
            move_dialog.destroy()
            messagebox.showinfo("Sukces", f"Przeniesiono {success_count}/{len(selected_ids)} pracowników.")
            self.refresh_employee_list()
            self.apply_filters()
            self.refresh_summary_if_open()  # NOWOŚĆ: Odśwież podsumowanie po zmianach grupowych

        ttk.Button(move_dialog, text="Zastosuj", command=apply_bulk_move).pack(pady=10)
        move_dialog.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (move_dialog.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (move_dialog.winfo_height() // 2)
        move_dialog.geometry(f'+{x}+{y}')

    def bulk_change_machine(self):
        selected_ids = self.get_selected_employee_ids()
        if not selected_ids:
            messagebox.showwarning("Brak zaznaczenia", "Zaznacz przynajmniej jednego pracownika.")
            return

        machine_dialog = tk.Toplevel(self)
        machine_dialog.title("Grupowa zmiana maszyny")
        machine_dialog.geometry("300x150")
        machine_dialog.transient(self)
        machine_dialog.grab_set()

        tk.Label(machine_dialog, text=f"Zmiana maszyny dla {len(selected_ids)} pracowników",
                 font=('Arial', 10, 'bold')).pack(pady=10)

        machine_var = tk.StringVar()
        ttk.Combobox(machine_dialog, textvariable=machine_var,
                     values=(self.emp_manager.get_setting('maszyny') or []),
                     state='readonly').pack(pady=5)

        def apply_bulk_machine():
            new_machine = machine_var.get()
            if not new_machine:
                messagebox.showwarning("Błąd", "Wybierz maszynę.")
                return
            success_count = 0
            for emp_id in selected_ids:
                old_row = self._get_emp_row(emp_id)
                old_machine = old_row[7] if old_row else None
                old_data = self.db_manager.fetch_one("SELECT * FROM employees WHERE id=?", (emp_id,))
                if self.emp_manager.update_employee_machine(emp_id, new_machine):
                    success_count += 1
                    self._log_field_change(emp_id, "Maszyna", old_machine, new_machine)
                    # Push undo dla edit
                    new_data = self.db_manager.fetch_one("SELECT * FROM employees WHERE id=?", (emp_id,))
                    if new_data and old_data:
                        self.push_undo_action('edit', f"Grupowa zmiana maszyny ID {emp_id}", data=new_data, old_data=old_data)
            machine_dialog.destroy()
            messagebox.showinfo("Sukces", f"Zmieniono maszynę dla {success_count}/{len(selected_ids)} pracowników.")
            self.refresh_employee_list()
            self.apply_filters()
            self.refresh_summary_if_open()  # NOWOŚĆ: Odśwież podsumowanie po zmianach grupowych

        ttk.Button(machine_dialog, text="Zastosuj", command=apply_bulk_machine).pack(pady=10)
        machine_dialog.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (machine_dialog.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (machine_dialog.winfo_height() // 2)
        machine_dialog.geometry(f'+{x}+{y}')

    def bulk_delete_employees(self):
        selected_ids = self.get_selected_employee_ids()
        if not selected_ids:
            messagebox.showwarning("Brak zaznaczenia", "Zaznacz przynajmniej jednego pracownika.")
            return
        if messagebox.askyesno("Potwierdzenie",
                               f"Czy na pewno chcesz usunąć {len(selected_ids)} zaznaczonych pracowników?"):
            success_count = 0
            for emp_id in selected_ids:
                emp_data = self.db_manager.fetch_one("SELECT * FROM employees WHERE id=?", (emp_id,))
                if self.emp_manager.delete_employee(emp_id):
                    success_count += 1
                    self._log_history_emp("Usunięcie pracownika", "Usunięto pracownika z bazy", emp_id)
                    # Push undo dla delete
                    if emp_data:
                        self.push_undo_action('delete', f"Usunięcie pracownika ID {emp_id}", data=emp_data)
            messagebox.showinfo("Sukces", f"Usunięto {success_count}/{len(selected_ids)} pracowników.")
            self.refresh_employee_list()
            self.apply_filters()
            self.refresh_summary_if_open()  # NOWOŚĆ: Odśwież podsumowanie po zmianach grupowych

    # ---------------- SZYBKIE WYSZUKIWANIA ----------------
    def find_without_position(self):
        filtered = []
        for emp in self.all_employees_data:
            stanowisko = str(emp[3]).strip() if emp[3] else ""
            if not stanowisko or stanowisko.lower() in ['', 'nieustawione', 'brak', 'none', 'null']:
                filtered.append(emp)
        if filtered:
            self.refresh_employee_list(filtered)
            messagebox.showinfo("Znaleziono", f"Znaleziono {len(filtered)} pracowników bez stanowiska.")
        else:
            messagebox.showinfo("Brak wyników", "Wszyscy pracownicy mają ustawione stanowisko.")
        self.refresh_summary_if_open()  # NOWOŚĆ: Odśwież podsumowanie po filtrze

    def find_without_department(self):
        filtered = []
        for emp in self.all_employees_data:
            wydzial = str(emp[4]).strip() if emp[4] else ""
            if not wydzial or wydzial.lower() in ['', 'nieustawiony', 'brak', 'none', 'null']:
                filtered.append(emp)
        if filtered:
            self.refresh_employee_list(filtered)
            messagebox.showinfo("Znaleziono", f"Znaleziono {len(filtered)} pracowników bez wydziału.")
        else:
            messagebox.showinfo("Brak wyników", "Wszyscy pracownicy mają ustawiony wydział.")
        self.refresh_summary_if_open()  # NOWOŚĆ: Odśwież podsumowanie po filtrze

    def find_without_machine(self):
        filtered = []
        for emp in self.all_employees_data:
            maszyna = str(emp[7]).strip() if emp[7] else ""
            if not maszyna or maszyna.lower() in ['', 'brak', 'none', 'null', 'nieustawione']:
                filtered.append(emp)
        if filtered:
            self.refresh_employee_list(filtered)
            messagebox.showinfo("Znaleziono", f"Znaleziono {len(filtered)} pracowników bez maszyny.")
        else:
            messagebox.showinfo("Brak wyników", "Wszyscy pracownicy mają ustawioną maszynę.")
        self.refresh_summary_if_open()  # NOWOŚĆ: Odśwież podsumowanie po filtrze

    def find_all_missing_data(self):
        filtered = []
        for emp in self.all_employees_data:
            stanowisko = str(emp[3]).strip() if emp[3] else ""
            wydzial = str(emp[4]).strip() if emp[4] else ""
            maszyna = str(emp[7]).strip() if emp[7] else ""
            if (not stanowisko or stanowisko.lower() in ['', 'nieustawione', 'brak', 'none', 'null'] or
                not wydzial or wydzial.lower() in ['', 'nieustawiony', 'brak', 'none', 'null'] or
                not maszyna or maszyna.lower() in ['', 'brak', 'none', 'null', 'nieustawione']):
                filtered.append(emp)
        if filtered:
            self.refresh_employee_list(filtered)
            messagebox.showinfo("Znaleziono", f"Znaleziono {len(filtered)} pracowników z brakującymi danymi.")
            missing_details = self.analyze_missing_data(filtered)
            messagebox.showinfo("Szczegóły brakujących danych", f"Szczegóły brakujących danych:\n{missing_details}")
        else:
            messagebox.showinfo("Brak wyników", "Wszyscy pracownicy mają kompletne dane.")
        self.refresh_summary_if_open()  # NOWOŚĆ: Odśwież podsumowanie po filtrze

    def analyze_missing_data(self, employees):
        mp = md = mm = 0
        for emp in employees:
            stanowisko = str(emp[3]).strip() if emp[3] else ""
            wydzial = str(emp[4]).strip() if emp[4] else ""
            maszyna = str(emp[7]).strip() if emp[7] else ""
            if not stanowisko or stanowisko.lower() in ['', 'nieustawione', 'brak', 'none', 'null']:
                mp += 1
            if not wydzial or wydzial.lower() in ['', 'nieustawiony', 'brak', 'none', 'null']:
                md += 1
            if not maszyna or maszyna.lower() in ['', 'brak', 'none', 'null', 'nieustawione']:
                mm += 1
        return (f"• Bez stanowiska: {mp}\n"
                f"• Bez wydziału: {md}\n"
                f"• Bez maszyny: {mm}")

    # ---------------- OBSADA + LOGI SZCZEGÓŁOWE ----------------
    def safe_move_employee(self, emp_id, new_wydzial=None, new_zmiana=None, new_stanowisko=None):
        old_row = self._get_emp_row(emp_id)
        old_w, old_z, old_s = (old_row[4] if old_row else None,
                               old_row[5] if old_row else None,
                               old_row[3] if old_row else None)
        old_data = self.db_manager.fetch_one("SELECT * FROM employees WHERE id=?", (emp_id,))

        if not new_zmiana or (new_zmiana and "Wolne" in new_zmiana):
            result = self.emp_manager.move_employee(emp_id, new_wydzial, new_zmiana, new_stanowisko)
        else:
            target_wydzial = new_wydzial if new_wydzial else \
                self.emp_manager.db.fetch_one("SELECT wydzial FROM employees WHERE id=?", (emp_id,))[0]

            current_count = len(self.emp_manager.db.fetch_all(
                "SELECT id FROM employees WHERE wydzial=? AND zmiana=? AND status='W Pracy'",
                (target_wydzial, new_zmiana)
            ))
            predicted_count = current_count + 1
            check = self.emp_manager.check_staffing_overflow(target_wydzial, new_zmiana, predicted_count)
            policy = self.emp_manager.get_overflow_policy()

            if check.get('overflow'):
                required = check.get('required', 0)
                excess_after = max(0, predicted_count - required)

                if policy == "warning":
                    response = messagebox.askyesno(
                        "⚠️ Przekroczenie obsady",
                        f"Wydział: {target_wydzial}, Zmiana: {new_zmiana}\n"
                        f"Wymagana obsada: {required}\n"
                        f"Aktualnie pracujących: {current_count}\n"
                        f"Po tej zmianie: {predicted_count} (+{excess_after})\n\n"
                        f"Czy na pewno chcesz dodać kolejnego pracownika?"
                    )
                    if not response:
                        self.refresh_summary_if_open()

                        return False
                elif policy == "auto_adjust":
                    moved = self.emp_manager.auto_adjust_overflow(target_wydzial, new_zmiana)
                    if moved:
                        messagebox.showinfo(
                            "Automatyczna korekta obsady",
                            "Dostosowano obsadę poprzez przeniesienie:\n" +
                            "\n".join([f"• {m['name']} → {m['to_shift']}" for m in moved])
                        )
                elif policy == "block":
                    messagebox.showwarning("Blokada",
                                           "Operacja zablokowana przez politykę przekroczeń obsady.")
                    return False

            result = self.emp_manager.move_employee(emp_id, new_wydzial, new_zmiana, new_stanowisko)

        if result and old_data:
            # Push undo dla edit po zmianie
            new_data = self.db_manager.fetch_one("SELECT * FROM employees WHERE id=?", (emp_id,))
            if new_data:
                self.push_undo_action('edit', f"Przeniesienie pracownika ID {emp_id}", data=new_data, old_data=old_data)
            if new_wydzial is not None:
                self._log_field_change(emp_id, "Wydział", old_w, new_wydzial)
            if new_zmiana is not None:
                self._log_field_change(emp_id, "Zmiana", old_z, new_zmiana)
            if new_stanowisko is not None:
                self._log_field_change(emp_id, "Stanowisko", old_s, new_stanowisko)

            self.refresh_employee_list()
            self.apply_filters()
            self.refresh_summary_if_open()  # NOWOŚĆ: Odśwież podsumowanie po przeniesieniu
        return result

    def safe_bulk_move(self, emp_ids, new_wydzial=None, new_zmiana=None, new_stanowisko=None):
        success_count = 0
        for emp_id in emp_ids:
            if self.safe_move_employee(emp_id, new_wydzial, new_zmiana, new_stanowisko):
                success_count += 1
        return success_count

    def move_employee_action(self, emp_id, new_wydzial=None, new_zmiana=None, new_stanowisko=None):
        if self.safe_move_employee(emp_id, new_wydzial, new_zmiana, new_stanowisko):
            messagebox.showinfo("Sukces", "Pracownik przeniesiony i historia zapisana.")
        else:
            messagebox.showerror("Błąd", "Nie udało się przenieść pracownika.")

    def change_status_action(self, emp_id, new_status):
        old_row = self._get_emp_row(emp_id)
        old_status = old_row[6] if old_row else None
        old_data = self.db_manager.fetch_one("SELECT * FROM employees WHERE id=?", (emp_id,))
        if self.emp_manager.update_employee_status(emp_id, new_status):
            self._log_field_change(emp_id, "Status", old_status, new_status)
            # Push undo dla edit
            new_data = self.db_manager.fetch_one("SELECT * FROM employees WHERE id=?", (emp_id,))
            if new_data and old_data:
                self.push_undo_action('edit', f"Zmiana statusu ID {emp_id}", data=new_data, old_data=old_data)
            messagebox.showinfo("Sukces", f"Status zmieniony na '{new_status}' i historia zapisana.")
            self.refresh_employee_list()
            self.apply_filters()
            self.refresh_summary_if_open()  # NOWOŚĆ: Odśwież podsumowanie po zmianie statusu
        else:
            messagebox.showerror("Błąd", "Nie udało się zmienić statusu.")

    def delete_employee_action(self, emp_id):
        # Zapisz dane przed usunięciem
        emp_data = self.db_manager.fetch_one("SELECT * FROM employees WHERE id=?", (emp_id,))
        if messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz usunąć tego pracownika?"):
            if self.emp_manager.delete_employee(emp_id):
                self._log_history_emp("Usunięcie pracownika", "Usunięto pracownika z bazy", emp_id)
                # Dodaj do undo
                if emp_data:
                    self.push_undo_action('delete', f"Usunięcie pracownika {emp_data[1]} {emp_data[2]} (ID: {emp_id})", data=emp_data)
                    print(f"DEBUG: Dodano push delete dla ID {emp_id}")
                messagebox.showinfo("Sukces", "Pracownik usunięty.")
                self.refresh_employee_list()
                self.apply_filters()
                self.refresh_summary_if_open()  # NOWOŚĆ: Odśwież podsumowanie po usunięciu
            else:
                messagebox.showerror("Błąd", "Nie udało się usunąć pracownika.")

    # ---------------- INNE OKNA ----------------
    def open_add_employee_dialog(self):
        # POPRAWKA: Zapisz liczbę rekordów przed dialogiem
        old_count = len(self.emp_manager.get_all_employees())
        print(f"DEBUG: Przed dodaniem – liczba rekordów: {old_count}")
        
        dialog = EmployeeDialog(self, self.emp_manager)
        self.wait_window(dialog)
        
        # Sprawdź duplikaty po dodaniu
        self._check_for_duplicates_after_add()
        
        # POPRAWKA: Sprawdź, czy liczba wzrosła – jeśli tak, push nowy rekord do undo
        try:
            new_count = len(self.emp_manager.get_all_employees())
            print(f"DEBUG: Po dodaniu – liczba rekordów: {new_count}")
            if new_count > old_count:
                # Znajdź nowy rekord (ostatni ID)
                last_id_result = self.db_manager.fetch_one("SELECT MAX(id) as last_id FROM employees")
                new_emp_id = last_id_result[0] if last_id_result else None
                if new_emp_id:
                    emp_data = self.db_manager.fetch_one("SELECT * FROM employees WHERE id=?", (new_emp_id,))
                    if emp_data:
                        self.push_undo_action('add', f"Dodanie pracownika {emp_data[1]} {emp_data[2]} (ID: {new_emp_id})", data=emp_data)
                        print(f"DEBUG: DODANO PUSH UNDO dla ID {new_emp_id} – stos: {len(self.undo_stack)}")
                    else:
                        print("DEBUG: Nie znaleziono danych nowego rekordu")
                else:
                    print("DEBUG: Nie znaleziono nowego ID")
            else:
                print("DEBUG: Liczba rekordów nie wzrosła – brak push do undo")
        except Exception as e:
            print(f"DEBUG BŁĄD push add: {e}")
        
        self.refresh_employee_list()
        self.apply_filters()
        self.refresh_summary_if_open()  # NOWOŚĆ: Odśwież podsumowanie po dodaniu

    # Funkcja sprawdzająca duplikaty po dodaniu
    def _check_for_duplicates_after_add(self):
        try:
            # Pobierz ID nowo dodanego (ostatni rekord)
            last_id_result = self.db_manager.fetch_one("SELECT MAX(id) as last_id FROM employees")
            if not last_id_result:
                self.refresh_summary_if_open()
                return
            new_emp_id = last_id_result[0]
            if not new_emp_id:
                return

            # Pobierz dane nowego
            new_emp_data = self.db_manager.fetch_one("SELECT * FROM employees WHERE id=?", (new_emp_id,))
            if not new_emp_data:
                return
            new_imie, new_nazwisko = new_emp_data[1], new_emp_data[2]

            # Sprawdź duplikaty (inny ID, to samo imię+nazwisko case-insensitive)
            dup_query = """
                SELECT id FROM employees 
                WHERE LOWER(imie) = LOWER(?) AND LOWER(nazwisko) = LOWER(?) AND id != ?
                LIMIT 1
            """
            duplicate = self.db_manager.fetch_one(dup_query, (new_imie, new_nazwisko, new_emp_id))
            
            if duplicate:
                existing_id = duplicate[0]
                response = messagebox.askyesno(
                    "Duplikat wykryty!",
                    f"Znaleziono istniejącego pracownika o imieniu '{new_imie}' i nazwisku '{new_nazwisko}' (ID: {existing_id}).\n\n"
                    f"Czy chcesz edytować istniejącego zamiast dodawać nowy?"
                )
                
                # W obu przypadkach usuń nowy duplikat
                if self.emp_manager.delete_employee(new_emp_id):
                    self._log_history_emp("Usunięcie duplikatu", f"Usunięto duplikat ID {new_emp_id} (imię: {new_imie}, nazwisko: {new_nazwisko})", new_emp_id)
                    # Push undo dla delete duplikatu
                    self.push_undo_action('delete', f"Usunięcie duplikatu ID {new_emp_id}", data=new_emp_data)
                
                if response:
                    # Edytuj istniejącego
                    existing_data = self.emp_manager.db.fetch_one("SELECT * FROM employees WHERE id=?", (existing_id,))
                    if existing_data:
                        self.open_edit_dialog(existing_data)
                else:
                    messagebox.showinfo("Anulowano", "Nowy wpis został usunięty, aby uniknąć duplikatów.")
                    
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd podczas sprawdzania duplikatów: {e}")
        self.refresh_summary_if_open()  # NOWOŚĆ: Odśwież podsumowanie po sprawdzeniu duplikatów

    def show_summary(self):
        self.summary_window = SummaryWindow(self, self.emp_manager)  # NOWOŚĆ: Zachowaj referencję do okna

    def show_history(self):
        HistoryWindow(self, self.emp_manager)

    def show_settings(self):
        if self.current_user and self.current_user.get('role') in ['admin', 'manager']:
            settings_win = SettingsWindow(self, self.emp_manager)
            self.wait_window(settings_win)  # NOWOŚĆ: Czekaj na zamknięcie ustawień
            self.refresh_summary_if_open()  # NOWOŚĆ: Odśwież podsumowanie po zmianach w ustawieniach
        else:
            messagebox.showerror("Brak uprawnień", "Tylko administratorzy i menedżerowie mogą otwierać ustawienia.")

    def show_color_editor(self):
        ColorEditor(self, self.emp_manager)

    # ---------------- BACKUP / IMPORT / EKSPORT ----------------
    def create_backup(self):
        backup_file = self.db_manager.backup_database()
        if backup_file:
            messagebox.showinfo("Backup", f"Utworzono backup bazy danych:\n{backup_file}")
        else:
            messagebox.showerror("Błąd", "Nie udało się utworzyć backupu.")

    def export_to_excel(self):
        try:
            vacations = self.emp_manager.get_vacations() or []
            l4_records = self.emp_manager.get_l4_records() or []
            vacation_map = {v[1]: f"{v[2]} - {v[3]}" for v in vacations}
            l4_map = {l[1]: f"{l[2]} - {l[3]}" for l in l4_records}

            export_data = []
            for emp in self.all_employees_data:
                emp_id, imie, nazwisko, stanowisko, wydzial, zmiana, status, maszyna = emp
                export_data.append({
                    "ID": emp_id, "Imię": imie, "Nazwisko": nazwisko,
                    "Stanowisko": stanowisko, "Wydział": wydzial, "Zmiana": self.emp_manager.get_shift_full_name(zmiana),
                    "Status": status, "Maszyna/Urządzenie": maszyna,
                    "Urlop od-do": vacation_map.get(emp_id, ""),
                    "L4 od-do": l4_map.get(emp_id, "")
                })

            df = pd.DataFrame(export_data)
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")],
                title="Zapisz dane do Excel"
            )
            if not file_path:
                return

            with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Pracownicy', index=False)
                workbook = writer.book
                worksheet = writer.sheets['Pracownicy']
                header_format = workbook.add_format({
                    'bold': True, 'text_wrap': True, 'valign': 'top',
                    'fg_color': '#D7E4BC', 'border': 1
                })
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                for i, col in enumerate(df.columns):
                    max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                    worksheet.set_column(i, i, max_len)

            self.emp_manager.log_history("Export Excel", f"Wyeksportowano dane do {file_path}")
            messagebox.showinfo("Sukces", f"Dane zostały wyeksportowane do:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd podczas eksportu do Excel: {e}")

    def import_employees_from_excel(self):
        file_path = filedialog.askopenfilename(defaultextension=".xlsx",
                                               filetypes=[("Excel files", "*.xlsx")],
                                               title="Wybierz plik Excel do importu")
        if not file_path:
            return
        try:
            df = pd.read_excel(file_path)
            df.columns = [c.lower().replace(' ', '_') for c in df.columns]
            if 'imie' not in df.columns or 'nazwisko' not in df.columns:
                messagebox.showerror("Błąd Importu", "Plik musi zawierać kolumny: imie, nazwisko")
                return

            df['stanowisko'] = df.get('stanowisko', 'Nieustawione')
            df['wydzial'] = df.get('wydzial', 'Nieustawiony')
            df['zmiana'] = df.get('zmiana', 'D - Wolne')
            df['status'] = df.get('status', 'Wolne')
            df['maszyna'] = df.get('maszyna', 'Brak')

            cols = ['imie', 'nazwisko', 'stanowisko', 'wydzial', 'zmiana', 'status', 'maszyna']
            imported_count = 0
            for _, row in df.iterrows():
                if pd.isna(row['imie']) or pd.isna(row['nazwisko']):
                    continue
                data = tuple(row[c] for c in cols)
                self.db_manager.execute_query("""
                    INSERT INTO employees (imie, nazwisko, stanowisko, wydzial, zmiana, status, maszyna)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, data)
                imported_count += 1

            self.emp_manager.log_history("Import Excel", f"Zaimportowano {imported_count} pracowników z pliku {file_path}")
            messagebox.showinfo("Sukces Importu", f"Zaimportowano {imported_count} pracowników.")
            self.refresh_employee_list()
            self.apply_filters()
            self.refresh_summary_if_open()  # NOWOŚĆ: Odśwież podsumowanie po imporcie
        except Exception as e:
            messagebox.showerror("Błąd Importu", f"Błąd podczas wczytywania pliku Excel: {e}")

    # ---------------- ALERTY / STATUS / DASHBOARD ----------------
    def check_alerts_periodically(self):
        try:
            alerts = self.emp_manager.check_staffing_alerts() or []
            if alerts:
                alert_text = "🚨 ALERT - Braki kadrowe:\n\n"
                for alert in alerts:
                    alert_text += f"• {alert['wydzial']} - {alert['zmiana']}: brakuje {alert['brakuje']} osób\n"
                if not hasattr(self, '_last_alert_time') or \
                        (datetime.now() - getattr(self, '_last_alert_time', datetime.now())).total_seconds() > 3600:
                    messagebox.showwarning("Alert Kadrowy", alert_text)
                    self._last_alert_time = datetime.now()
            self.after(300000, self.check_alerts_periodically)
        except Exception as e:
            print(f"Błąd sprawdzania alertów: {e}")
            self.after(300000, self.check_alerts_periodically)

    def update_status_bar(self):
        pass

    def update_dashboard(self):
        pass

    # ---------------- WYLOGOWANIE / ZAMKNIĘCIE ----------------
    def logout(self):
        if messagebox.askyesno("Wylogowanie", "Czy na pewno chcesz się wylogować?"):
            self.current_user = None
            self.emp_manager.set_current_user(None)
            self._app_initialized = False  # pozwól ponownie zbudować UI po zalogowaniu
            for w in self.winfo_children():
                try:
                    w.destroy()
                except Exception:
                    pass
            self.create_login_screen()

    def on_closing(self):
        if messagebox.askokcancel("Wyjście", "Czy na pewno chcesz zamknąć aplikację?"):
            try:
                self.db_manager.conn.close()
            except Exception:
                pass
            self.destroy()

    # ---------------- NOWOŚĆ: SYSTEM UNDO ----------------
    def push_undo_action(self, action_type, description, data=None, old_data=None):
        """Dodaje akcję do stosu undo."""
        action = {
            'type': action_type,
            'description': description,
            'data': data,
            'old_data': old_data,
            'timestamp': datetime.now()
        }
        
        self.undo_stack.append(action)
        
        # Ogranicz rozmiar stosu
        if len(self.undo_stack) > self.undo_max_size:
            self.undo_stack.pop(0)
        
        # Aktywuj przycisk Cofnij
        self.undo_button.config(state='normal')
        
        print(f"DEBUG: Dodano akcję undo: {description} (stos: {len(self.undo_stack)})")

    def undo_last_action(self):
        """Cofa ostatnią akcję ze stosu undo."""
        if not self.undo_stack:
            messagebox.showinfo("Brak akcji", "Nie ma akcji do cofnięcia.")
            return
        
        action = self.undo_stack.pop()
        
        try:
            if action['type'] == 'add':
                # Cofnięcie dodania - usuń pracownika
                emp_id = action['data'][0]
                if self.emp_manager.delete_employee(emp_id):
                    self.emp_manager.log_history("Cofnięcie dodania", f"Cofnięto dodanie pracownika: {action['description']}")
                    messagebox.showinfo("Cofnięto", f"Cofnięto: {action['description']}")
            
            elif action['type'] == 'edit':
                # Cofnięcie edycji - przywróć stare dane
                emp_id = action['old_data'][0]
                old_data = action['old_data']
                
                # Przywróć stare dane
                self.db_manager.execute_query("""
                    UPDATE employees 
                    SET imie=?, nazwisko=?, stanowisko=?, wydzial=?, zmiana=?, status=?, maszyna=?
                    WHERE id=?
                """, (old_data[1], old_data[2], old_data[3], old_data[4], old_data[5], old_data[6], old_data[7], emp_id))
                
                self.emp_manager.log_history("Cofnięcie edycji", f"Cofnięto edycję pracownika: {action['description']}")
                messagebox.showinfo("Cofnięto", f"Cofnięto: {action['description']}")
            
            elif action['type'] == 'delete':
                # Cofnięcie usunięcia - przywróć pracownika
                emp_data = action['data']
                self.db_manager.execute_query("""
                    INSERT INTO employees (id, imie, nazwisko, stanowisko, wydzial, zmiana, status, maszyna)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (emp_data[0], emp_data[1], emp_data[2], emp_data[3], emp_data[4], emp_data[5], emp_data[6], emp_data[7]))
                
                self.emp_manager.log_history("Cofnięcie usunięcia", f"Cofnięto usunięcie pracownika: {action['description']}")
                messagebox.showinfo("Cofnięto", f"Cofnięto: {action['description']}")
        
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się cofnąć akcji: {str(e)}")
            # Przywróć akcję do stosu w przypadku błędu
            self.undo_stack.append(action)
        
        # Odśwież interfejs
        self.refresh_employee_list()
        self.refresh_summary_if_open()  # NOWOŚĆ: Odśwież podsumowanie po undo
        
        # Deaktywuj przycisk jeśli stos pusty
        if not self.undo_stack:
            self.undo_button.config(state='disabled')


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()

def refresh_employee_list_and_shifts(self):
    # Odśwież listę i przebuduj kolumnę 'Zmiana' wg nowych godzin
    try:
        self.refresh_employee_list()
    except Exception as e:
        print("refresh_employee_list error:", e)
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, time
import pandas as pd
from employee_management import EmployeeManagement
from db_manager import DBManager
from login_window import LoginWindow
from employee_dialog import EmployeeDialog
from settings_window import SettingsWindow
from history_window import HistoryWindow
from summary_window import SummaryWindow
from machine_dialog import MachineDialog
from move_dialog import MoveDialog
from status_dialog import StatusDialog
from vacation_dialog import VacationDialog
from l4_dialog import L4Dialog
from color_editor import ColorEditor
from collections import defaultdict
from PIL import Image, ImageTk
import os

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("System Zarządzania Pracownikami (Python/Tkinter)")
        self.geometry("1400x800")
        
        # System motywów
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
        
        # Ustaw domyślny motyw
        self.setup_light_theme()
        
        self.create_login_screen()

    # SYSTEM MOTYWÓW
    def setup_light_theme(self):
        """Domyślny jasny motyw"""
        self.current_theme = 'light'
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Kolory jasnego motywu
        self.bg_color = '#ffffff'
        self.fg_color = '#000000'
        self.accent_color = '#007acc'
        self.success_color = '#28a745'
        self.warning_color = '#ffc107'
        self.danger_color = '#dc3545'
        
        self.configure(bg=self.bg_color)
        self.style.configure('.', background=self.bg_color, foreground=self.fg_color)
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color, foreground=self.fg_color)
        self.style.configure('TLabelFrame', background=self.bg_color)
        self.style.configure('TButton', background='#f0f0f0', foreground=self.fg_color)
        self.style.configure('Accent.TButton', background=self.accent_color, foreground='white')
        self.style.configure('Success.TButton', background=self.success_color, foreground='white')
        self.style.configure('Warning.TButton', background=self.warning_color, foreground='white')
        self.style.configure('Danger.TButton', background=self.danger_color, foreground='white')
        self.style.configure('Treeview', background='white', foreground='black', fieldbackground='white')
        self.style.configure('Treeview.Heading', background='#e0e0e0', foreground='black')
        self.style.configure('TCombobox', background='white', foreground='black')
        self.style.configure('TEntry', background='white', foreground='black')
        self.style.configure('Horizontal.TProgressbar', background=self.accent_color)
        
        # NOWE: Style dla małych przycisków
        self.style.configure('Small.TButton', font=('Arial', 8))
        self.style.configure('Danger.Small.TButton', font=('Arial', 8), background=self.danger_color, foreground='white')

    def setup_dark_theme(self):
        """Ciemny motyw"""
        self.current_theme = 'dark'
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Kolory ciemnego motywu
        self.bg_color = '#2b2b2b'
        self.fg_color = '#ffffff'
        self.accent_color = '#4CAF50'
        self.success_color = '#388e3c'
        self.warning_color = '#f57c00'
        self.danger_color = '#d32f2f'
        self.tree_bg = '#3c3f41'
        self.tree_fg = '#ffffff'
        
        self.configure(bg=self.bg_color)
        self.style.configure('.', background=self.bg_color, foreground=self.fg_color)
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color, foreground=self.fg_color)
        self.style.configure('TLabelFrame', background=self.bg_color, foreground=self.fg_color)
        self.style.configure('TButton', background='#404040', foreground=self.fg_color)
        self.style.configure('Accent.TButton', background=self.accent_color, foreground='white')
        self.style.configure('Success.TButton', background=self.success_color, foreground='white')
        self.style.configure('Warning.TButton', background=self.warning_color, foreground='white')
        self.style.configure('Danger.TButton', background=self.danger_color, foreground='white')
        self.style.configure('Treeview', background=self.tree_bg, foreground=self.tree_fg, fieldbackground=self.tree_bg)
        self.style.configure('Treeview.Heading', background='#404040', foreground=self.fg_color)
        self.style.configure('TCombobox', background=self.tree_bg, foreground=self.tree_fg)
        self.style.configure('TEntry', background=self.tree_bg, foreground=self.tree_fg)
        
        # NOWE: Style dla małych przycisków
        self.style.configure('Small.TButton', font=('Arial', 8))
        self.style.configure('Danger.Small.TButton', font=('Arial', 8), background=self.danger_color, foreground='white')

    def setup_blue_theme(self):
        """Niebieski motyw korporacyjny"""
        self.current_theme = 'blue'
        self.style = ttk.Style()
        self.style.theme_use('vista')
        
        # Kolory niebieskiego motywu
        self.bg_color = '#f0f8ff'
        self.fg_color = '#1e3a5f'
        self.accent_color = '#1e88e5'
        self.success_color = '#43a047'
        self.warning_color = '#ff9800'
        self.danger_color = '#e53935'
        
        self.configure(bg=self.bg_color)
        self.style.configure('.', background=self.bg_color, foreground=self.fg_color)
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color, foreground=self.fg_color)
        self.style.configure('TLabelFrame', background=self.bg_color, bordercolor=self.accent_color)
        self.style.configure('TButton', background=self.accent_color, foreground='white')
        self.style.configure('Accent.TButton', background='#1565c0', foreground='white')
        self.style.configure('Success.TButton', background=self.success_color, foreground='white')
        self.style.configure('Warning.TButton', background=self.warning_color, foreground='white')
        self.style.configure('Danger.TButton', background=self.danger_color, foreground='white')
        self.style.configure('Treeview', background='white', foreground='black')
        self.style.configure('Treeview.Heading', background=self.accent_color, foreground='white')
        self.style.configure('TCombobox', background='white', foreground='black')
        self.style.configure('TEntry', background='white', foreground='black')
        
        # NOWE: Style dla małych przycisków
        self.style.configure('Small.TButton', font=('Arial', 8))
        self.style.configure('Danger.Small.TButton', font=('Arial', 8), background=self.danger_color, foreground='white')

    def setup_modern_theme(self):
        """Nowoczesny motyw z gradientami"""
        self.current_theme = 'modern'
        self.style = ttk.Style()
        self.style.theme_use('alt')
        
        # Nowoczesna paleta kolorów
        self.bg_color = '#f8fafc'
        self.fg_color = '#2d3748'
        self.accent_color = '#667eea'
        self.success_color = '#48bb78'
        self.warning_color = '#ed8936'
        self.danger_color = '#f56565'
        
        self.configure(bg=self.bg_color)
        self.style.configure('.', background=self.bg_color, foreground=self.fg_color)
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color, foreground=self.fg_color)
        self.style.configure('TLabelFrame', background=self.bg_color, bordercolor=self.accent_color)
        self.style.configure('TButton', background=self.accent_color, foreground='white')
        self.style.configure('Accent.TButton', background='#5a67d8', foreground='white')
        self.style.configure('Success.TButton', background=self.success_color, foreground='white')
        self.style.configure('Warning.TButton', background=self.warning_color, foreground='white')
        self.style.configure('Danger.TButton', background=self.danger_color, foreground='white')
        self.style.configure('Treeview', background='white', foreground=self.fg_color)
        self.style.configure('Treeview.Heading', background=self.accent_color, foreground='white')
        self.style.configure('TCombobox', background='white', foreground=self.fg_color)
        self.style.configure('TEntry', background='white', foreground=self.fg_color)
        
        # NOWE: Style dla małych przycisków
        self.style.configure('Small.TButton', font=('Arial', 8))
        self.style.configure('Danger.Small.TButton', font=('Arial', 8), background=self.danger_color, foreground='white')

    def change_theme(self, theme_name):
        """Zmienia motyw aplikacji"""
        if theme_name in self.themes:
            self.themes[theme_name]()
            if hasattr(self, 'main_frame'):
                self.refresh_interface()

    def refresh_interface(self):
        """Odświeża interfejs po zmianie motywu"""
        self.refresh_employee_list()
        self.update_status_bar()

    def create_login_screen(self):
        self.withdraw()
        LoginWindow(self, self.db_manager, self.on_login_success)

    def on_login_success(self, user):
        self.current_user = user
        self.emp_manager.set_current_user(user)
        self.title(f"System Zarządzania Pracownikami - Zalogowano jako: {user['username']} ({user['role']})")
        self.deiconify()
        self.state('zoomed')
        self.create_main_app_interface()
        
        # Uruchom automatyczne sprawdzanie alertów
        self.after(5000, self.check_alerts_periodically)

    def create_main_app_interface(self):
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill="both", expand=True)

        self.create_control_panel()
        self.create_employee_list_section()
        
        self.refresh_employee_list()
        self.update_dashboard()

        self.main_frame.grid_rowconfigure(4, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

    # NOWE METODY DO ZARZĄDZANIA OBSADĄ
    def safe_move_employee(self, emp_id, new_wydzial=None, new_zmiana=None, new_stanowisko=None):
        """Bezpieczne przenoszenie z kontrolą obsady"""
        if not new_zmiana or "Wolne" in new_zmiana:
            # Brak zmiany lub zmiana wolne - bez kontroli
            return self.emp_manager.move_employee(emp_id, new_wydzial, new_zmiana, new_stanowisko)
        
        # Sprawdź aktualną liczbę pracowników
        target_wydzial = new_wydzial if new_wydzial else \
            self.emp_manager.db.fetch_one("SELECT wydzial FROM employees WHERE id=?", (emp_id,))[0]
        
        current_count = len(self.emp_manager.db.fetch_all(
            "SELECT id FROM employees WHERE wydzial=? AND zmiana=? AND status='W Pracy'",
            (target_wydzial, new_zmiana)
        ))
        
        # Sprawdź czy będzie przekroczenie
        check = self.emp_manager.check_staffing_overflow(target_wydzial, new_zmiana, current_count + 1)
        policy = self.emp_manager.get_overflow_policy()
        
        if check['overflow']:
            if policy == "warning":
                # Pytaj użytkownika co zrobić
                response = messagebox.askyesno(
                    "⚠️ Przekroczenie obsady",
                    f"Wydział: {target_wydzial}, Zmiana: {new_zmiana}\n"
                    f"Wymagana obsada: {check['required']}\n"
                    f"Aktualnie pracujących: {check['current']}\n"
                    f"Po tej zmianie: {check['current'] + 1} (+{check['excess'] + 1})\n\n"
                    f"Czy na pewno chcesz dodać kolejnego pracownika?"
                )
                if not response:
                    return False
            elif policy == "auto_adjust":
                # Automatyczna korekta
                moved = self.emp_manager.auto_adjust_overflow(target_wydzial, new_zmiana)
                if moved:
                    messagebox.showinfo(
                        "Automatyczna korekta obsady",
                        f"Dostosowano obsadę poprzez przeniesienie:\n" +
                        "\n".join([f"• {m['name']} → {m['to_shift']}" for m in moved])
                    )
        
        return self.emp_manager.move_employee(emp_id, new_wydzial, new_zmiana, new_stanowisko)

    def safe_bulk_move(self, emp_ids, new_wydzial=None, new_zmiana=None, new_stanowisko=None):
        """Bezpieczne grupowe przenoszenie"""
        if not new_zmiana or "Wolne" in new_zmiana:
            # Brak kontroli dla zmian wolnych
            success_count = 0
            for emp_id in emp_ids:
                if self.emp_manager.move_employee(emp_id, new_wydzial, new_zmiana, new_stanowisko):
                    success_count += 1
            return success_count
        
        policy = self.emp_manager.get_overflow_policy()
        success_count = 0
        
        for emp_id in emp_ids:
            if self.safe_move_employee(emp_id, new_wydzial, new_zmiana, new_stanowisko):
                success_count += 1
        
        return success_count

    def create_control_panel(self):
        panel_frame = ttk.Frame(self.main_frame, padding="5")
        panel_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        # Górny pasek z statusem i wyborem motywu
        top_bar_frame = ttk.Frame(panel_frame)
        top_bar_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        
        # Kompaktowy pasek statusu
        self.create_compact_status_bar(top_bar_frame)
        
        # Wybór motywu (po prawej)
        theme_frame = ttk.Frame(top_bar_frame)
        theme_frame.grid(row=0, column=1, sticky="e")
        
        ttk.Label(theme_frame, text="Motyw:").pack(side='left', padx=(20, 5))
        self.theme_var = tk.StringVar(value=self.current_theme)
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var, 
                                  values=list(self.themes.keys()), 
                                  state='readonly', width=10)
        theme_combo.pack(side='left')
        theme_combo.bind('<<ComboboxSelected>>', lambda e: self.change_theme(self.theme_var.get()))
        
        top_bar_frame.columnconfigure(0, weight=1)
        
        # Główne przyciski nawigacji
        nav_frame = ttk.LabelFrame(panel_frame, text="Nawigacja", padding="5")
        nav_frame.grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        ttk.Button(nav_frame, text="➕ Dodaj Pracownika", command=self.open_add_employee_dialog).pack(side='left', padx=2)
        ttk.Button(nav_frame, text="📊 Podsumowanie", command=self.show_summary).pack(side='left', padx=2)
        ttk.Button(nav_frame, text="📋 Historia", command=self.show_history).pack(side='left', padx=2)
        ttk.Button(nav_frame, text="⚙️ Ustawienia", command=self.show_settings).pack(side='left', padx=2)
        ttk.Button(nav_frame, text="🎨 Kolory", command=self.show_color_editor).pack(side='left', padx=2)
        ttk.Button(nav_frame, text="💾 Backup", command=self.create_backup).pack(side='left', padx=2)
        

        
        # Operacje grupowe - ZMIENIONE NA MNIEJSZĄ CZCIONKĘ
        operations_frame = ttk.LabelFrame(panel_frame, text="Operacje Grupowe", padding="5")
        operations_frame.grid(row=2, column=0, sticky="w", pady=(5, 0))
        
        # Grupa 1: Podstawowe operacje
        basic_ops_frame = ttk.Frame(operations_frame)
        basic_ops_frame.pack(fill='x', pady=2)
        
        ttk.Button(basic_ops_frame, text="Status", 
                  command=self.bulk_change_status, width=14, style='Small.TButton').pack(side='left', padx=1)
        ttk.Button(basic_ops_frame, text="Przeniesienie", 
                  command=self.bulk_move_employees, width=14, style='Small.TButton').pack(side='left', padx=1)
        ttk.Button(basic_ops_frame, text="Maszyna", 
                  command=self.bulk_change_machine, width=14, style='Small.TButton').pack(side='left', padx=1)
        
        # Grupa 2: Wyszukiwanie brakujących danych
        search_ops_frame = ttk.Frame(operations_frame)
        search_ops_frame.pack(fill='x', pady=2)
        
        ttk.Button(search_ops_frame, text="Bez Stanowiska", 
                  command=self.find_without_position, width=14, style='Small.TButton').pack(side='left', padx=1)
        ttk.Button(search_ops_frame, text="Bez Wydziału", 
                  command=self.find_without_department, width=14, style='Small.TButton').pack(side='left', padx=1)
        ttk.Button(search_ops_frame, text="Bez Maszyny", 
                  command=self.find_without_machine, width=14, style='Small.TButton').pack(side='left', padx=1)
        ttk.Button(search_ops_frame, text="Wszystkie Braki", 
                  command=self.find_all_missing_data, width=14, style='Small.TButton').pack(side='left', padx=1)
        
        # Grupa 3: Operacje niebezpieczne
        danger_ops_frame = ttk.Frame(operations_frame)
        danger_ops_frame.pack(fill='x', pady=2)
        
        ttk.Button(danger_ops_frame, text="Usuń Zaznaczonych", 
                  command=self.bulk_delete_employees, style='Danger.Small.TButton', width=14).pack(side='left', padx=1)
        
        # Panel informacyjny użytkownika
        info_frame = ttk.LabelFrame(panel_frame, text="Informacje", padding="5")
        info_frame.grid(row=1, column=1, rowspan=2, sticky="ne", pady=(5, 0), padx=(20, 0))
        
        self.time_label = tk.Label(info_frame, text="", font=('Arial', 9))
        self.time_label.pack(side='top', anchor='e')
        
        self.user_label = tk.Label(info_frame, text=f"👤 {self.current_user['username']}", font=('Arial', 9))
        self.user_label.pack(side='top', anchor='e')
        
        self.role_label = tk.Label(info_frame, text=f"🎭 {self.current_user['role']}", font=('Arial', 9))
        self.role_label.pack(side='top', anchor='e')
        
        self.selected_count_label = tk.Label(info_frame, text="📌 Zaznaczono: 0", font=('Arial', 9, 'bold'), foreground='blue')
        self.selected_count_label.pack(side='top', anchor='e')
        
        # Przyciski systemowe
        system_frame = ttk.Frame(panel_frame)
        system_frame.grid(row=3, column=0, columnspan=2, sticky="e", pady=(5, 0))
        
        ttk.Button(system_frame, text="🚪 Wyloguj", command=self.logout, width=12).pack(side='right', padx=2)
        ttk.Button(system_frame, text="❌ Zamknij", command=self.on_closing, width=12).pack(side='right', padx=2)
        
        panel_frame.columnconfigure(0, weight=1)
        panel_frame.columnconfigure(1, weight=0)
        
        self.update_time()

    def show_staffing_management(self):
        """Pokazuje okno zarządzania obsadą"""
        from staffing_window import StaffingManagementWindow
        StaffingManagementWindow(self, self.emp_manager)

    def create_compact_status_bar(self, parent):
        """Tworzy zminimalizowany pasek informacyjny z podsumowaniem statusów"""
        status_frame = ttk.Frame(parent, relief='solid', borderwidth=1, padding="8")
        status_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        # Nagłówek
        ttk.Label(status_frame, text="📊 Stan Kadry:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        # Pobierz kolory statusów z bazy
        status_colors = {}
        try:
            status_config = self.emp_manager.get_statuses_config()
            for name, color in status_config:
                status_colors[name] = color
        except:
            # Domyślne kolory jeśli nie uda się pobrać
            status_colors = {
                "W Pracy": "#3CB371",
                "Urlop": "#FFA500", 
                "L4": "#FF4500",
                "Wolne": "#98FB98"
            }
        
        # Statusy do wyświetlenia - bardziej kompaktowe
        statuses_to_show = ["W Pracy", "Urlop", "L4", "Wolne"]
        
        self.status_labels = {}
        
        for i, status in enumerate(statuses_to_show):
            # Kompaktowa ramka dla każdego statusu
            status_item_frame = ttk.Frame(status_frame)
            status_item_frame.grid(row=0, column=i+1, sticky="nsew", padx=8)
            
            # Mały kolorowy kwadrat
            color_canvas = tk.Canvas(status_item_frame, width=12, height=12, bg=status_colors.get(status, 'white'), 
                                   highlightthickness=1, highlightbackground="black")
            color_canvas.pack(side='left', padx=(0, 4))
            
            # Nazwa statusu i liczba w jednej linii
            count_label = tk.Label(status_item_frame, text="0", font=('Arial', 10, 'bold'),
                                 foreground=status_colors.get(status, 'black'))
            count_label.pack(side='left', padx=(0, 2))
            
            name_label = tk.Label(status_item_frame, text=status, font=('Arial', 9))
            name_label.pack(side='left')
            
            self.status_labels[status] = count_label
        
        # ALL - suma wszystkich pracowników (bardziej kompaktowe)
        all_frame = ttk.Frame(status_frame)
        all_frame.grid(row=0, column=len(statuses_to_show)+1, sticky="nsew", padx=8)
        
        all_color_canvas = tk.Canvas(all_frame, width=12, height=12, bg='#4169E1', 
                                   highlightthickness=1, highlightbackground="black")
        all_color_canvas.pack(side='left', padx=(0, 4))
        
        all_count_label = tk.Label(all_frame, text="0", font=('Arial', 10, 'bold'), foreground='#4169E1')
        all_count_label.pack(side='left', padx=(0, 2))
        
        all_name_label = tk.Label(all_frame, text="RAZEM", font=('Arial', 9, 'bold'))
        all_name_label.pack(side='left')
        
        self.all_count_label = all_count_label
        
        # Ustaw równe rozłożenie kolumn
        for i in range(len(statuses_to_show) + 2):
            status_frame.columnconfigure(i, weight=1)

    def update_status_bar(self):
        """Aktualizuje pasek statusów z aktualnymi danymi"""
        employees = self.emp_manager.get_all_employees()
        
        # Inicjalizuj liczniki
        status_counts = {status: 0 for status in self.status_labels.keys()}
        status_counts["ALL"] = len(employees)
        
        # Policz pracowników według statusów
        for emp in employees:
            status = emp[6]  # status jest na pozycji 6
            if status in status_counts:
                status_counts[status] += 1
        
        # Aktualizuj etykiety
        for status, label in self.status_labels.items():
            label.config(text=str(status_counts[status]))
        
        self.all_count_label.config(text=str(status_counts["ALL"]))

    def update_time(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=f"🕒 {now}")
        self.after(1000, self.update_time)
        
    def update_dashboard(self):
        employees = self.emp_manager.get_all_employees()
        status_counts = {"W Pracy": 0, "Urlop": 0, "L4": 0, "Wolne": 0}
        
        for emp in employees:
            status = emp[6]
            if status in status_counts:
                status_counts[status] += 1

    def create_employee_list_section(self):
        filter_frame = ttk.LabelFrame(self.main_frame, text="Filtrowanie i Operacje", padding="5")
        filter_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        self.filters = {}
        
        filter_cols_combo = ["Wydział", "Zmiana", "Status"]
        self.dynamic_filter_vars = {}
        for i, col in enumerate(filter_cols_combo):
            tk.Label(filter_frame, text=f"{col}:").grid(row=0, column=i * 2, padx=5, sticky='w')
            self.dynamic_filter_vars[col] = tk.StringVar(self)
            combo = ttk.Combobox(filter_frame, textvariable=self.dynamic_filter_vars[col], state='readonly')
            combo.grid(row=0, column=i * 2 + 1, padx=5, sticky='ew')
            combo.bind('<<ComboboxSelected>>', self.apply_filters)
            self.filters[col] = combo
            
        tk.Label(filter_frame, text="Nazwisko:").grid(row=0, column=len(filter_cols_combo) * 2, padx=5, sticky='w')
        self.nazwisko_entry = tk.Entry(filter_frame)
        self.nazwisko_entry.grid(row=0, column=len(filter_cols_combo) * 2 + 1, padx=5, sticky='ew')
        self.nazwisko_entry.bind('<KeyRelease>', self.apply_filters)
        
        ttk.Button(filter_frame, text="Resetuj Filtry", command=self.reset_filters).grid(row=0, column=len(filter_cols_combo) * 2 + 2, padx=5, sticky='ew')
        ttk.Button(filter_frame, text="📥 Import z Excel", command=self.import_employees_from_excel).grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        ttk.Button(filter_frame, text="📤 Export do Excel", command=self.export_to_excel).grid(row=1, column=2, columnspan=2, padx=5, pady=5, sticky='ew')
        
        filter_frame.columnconfigure(1, weight=1)
        filter_frame.columnconfigure(3, weight=1)
        filter_frame.columnconfigure(5, weight=1)
        
        self.update_dynamic_filters()

        # NOWY KAFELEK PODSUMOWANIA (początkowo ukryty) - ZMNIEJSZONY
        self.summary_tile_frame = ttk.LabelFrame(self.main_frame, text="🎯 Podsumowanie Filtrowania", padding="5")
        self.summary_tile_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=2)  # Zmniejszone pady
        self.summary_tile_frame.grid_remove()  # Ukryj na starcie

        # Kontener dla kafelka podsumowania
        self.summary_content_frame = ttk.Frame(self.summary_tile_frame)
        self.summary_content_frame.pack(fill='both', expand=True)

        # NOWE KOLUMNY: Dodano kolumny dla urlopów i L4
        columns = ("ID", "Imię", "Nazwisko", "Stanowisko", "Wydział", "Zmiana", "Status", "Maszyna/Urządzenie", "Urlop od-do", "L4 od-do")
        self.employee_tree = ttk.Treeview(self.main_frame, columns=columns, show="headings", selectmode='extended')
        
        for col in columns:
            self.employee_tree.heading(col, text=col, command=lambda c=col: self.sort_column(self.employee_tree, c, False))
            self.employee_tree.column(col, width=120, anchor=tk.W)
        
        # Ustawienia szerokości kolumn
        self.employee_tree.column("ID", width=40, stretch=tk.NO)
        self.employee_tree.column("Status", width=100, stretch=tk.NO)
        self.employee_tree.column("Urlop od-do", width=120, stretch=tk.NO)
        self.employee_tree.column("L4 od-do", width=120, stretch=tk.NO)

        v_scroll = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.employee_tree.yview)
        h_scroll = ttk.Scrollbar(self.main_frame, orient="horizontal", command=self.employee_tree.xview)
        self.employee_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        v_scroll.grid(row=4, column=1, sticky="ns")
        h_scroll.grid(row=5, column=0, sticky="ew")
        self.employee_tree.grid(row=4, column=0, sticky="nsew", pady=(3, 0))  # Zmniejszony odstęp
        
        self.employee_tree.bind('<Double-1>', self.on_double_click_employee)
        self.employee_tree.bind('<Button-3>', self.show_context_menu)
        self.employee_tree.bind('<<TreeviewSelect>>', self.on_selection_change)

    def on_selection_change(self, event):
        """Aktualizuje licznik zaznaczonych pracowników"""
        selected_count = len(self.employee_tree.selection())
        self.selected_count_label.config(text=f"📌 Zaznaczono: {selected_count}")

    def update_dynamic_filters(self):
        wydzialy = [''] + self.emp_manager.get_setting('wydzialy')
        shifts = [''] + [s[0] for s in self.emp_manager.get_shifts_config()]
        statuses = [''] + [s[0] for s in self.emp_manager.get_statuses_config()]
        
        self.filters["Wydział"]['values'] = wydzialy
        self.filters["Zmiana"]['values'] = shifts
        self.filters["Status"]['values'] = statuses
        
    def refresh_employee_list(self, filter_data=None):
        if filter_data is None:
            self.all_employees_data = self.emp_manager.get_all_employees()
            data_to_display = self.all_employees_data
        else:
            data_to_display = filter_data

        for item in self.employee_tree.get_children():
            self.employee_tree.delete(item)
            
        status_colors = {name: color for name, color in self.emp_manager.get_statuses_config()}
        
        # Pobierz dane urlopów i L4
        vacations = self.emp_manager.get_vacations()
        l4_records = self.emp_manager.get_l4_records()
        
        # Oznacz pracowników którzy powodują przekroczenie
        overflow_data = {}
        for emp in data_to_display:
            wydzial, zmiana, status = emp[4], emp[5], emp[6]
            if status == "W Pracy" and "Wolne" not in zmiana:
                key = (wydzial, zmiana)
                if key not in overflow_data:
                    required = self.emp_manager.get_required_staff_by_wydzial_shift(wydzial, zmiana)
                    current_count = len([e for e in data_to_display 
                                       if e[4] == wydzial and e[5] == zmiana and e[6] == "W Pracy"])
                    overflow_data[key] = {
                        'required': required,
                        'current': current_count,
                        'overflow': current_count > required if required > 0 else False
                    }
        
        for emp in data_to_display:
            emp_id, imie, nazwisko, stanowisko, wydzial, zmiana, status, maszyna = emp
            
            # Znajdź urlop dla pracownika
            vacation_info = ""
            for vac in vacations:
                if vac[1] == emp_id:  # vac[1] to employee_id
                    start = vac[2]  # start_date
                    end = vac[3]    # end_date
                    vacation_info = f"{start} - {end}"
                    break
            
            # Znajdź L4 dla pracownika
            l4_info = ""
            for l4 in l4_records:
                if l4[1] == emp_id:  # l4[1] to employee_id
                    start = l4[2]  # start_date
                    end = l4[3]    # end_date
                    l4_info = f"{start} - {end}"
                    break
            
            values = (emp_id, imie, nazwisko, stanowisko, wydzial, zmiana, status, maszyna, vacation_info, l4_info)
            
            color_tag = status.replace(' ', '_')
            self.employee_tree.tag_configure(color_tag, background=status_colors.get(status, 'white'))
            
            tags = [color_tag]
            
            # Dodaj oznaczenie przekroczenia
            if status == "W Pracy" and "Wolne" not in zmiana:
                key = (wydzial, zmiana)
                if key in overflow_data and overflow_data[key]['overflow']:
                    # Znajdź który pracownik jest nadmiarowy
                    required = overflow_data[key]['required']
                    current = overflow_data[key]['current']
                    if current > required:
                        # Oznacz na pomarańczowo pracowników ponad limit
                        self.employee_tree.tag_configure('OVERFLOW', background='#FFF0E0')
                        tags.append('OVERFLOW')
            
            self.employee_tree.insert("", tk.END, values=values, tags=tuple(tags))
            
        # Aktualizuj pasek statusów i licznik zaznaczonych
        self.update_status_bar()
        self.on_selection_change(None)
        self.update_dashboard()

    def apply_filters(self, event=None):
        filtered_data = []
        
        filter_wydzial = self.dynamic_filter_vars["Wydział"].get()
        filter_zmiana = self.dynamic_filter_vars["Zmiana"].get()
        filter_status = self.dynamic_filter_vars["Status"].get()
        filter_nazwisko = self.nazwisko_entry.get().strip().lower()

        for emp in self.all_employees_data:
            match_wydzial = not filter_wydzial or emp[4] == filter_wydzial
            match_zmiana = not filter_zmiana or emp[5] == filter_zmiana
            match_status = not filter_status or emp[6] == filter_status
            match_nazwisko = not filter_nazwisko or filter_nazwisko in emp[2].lower()

            if match_wydzial and match_zmiana and match_status and match_nazwisko:
                filtered_data.append(emp)
                
        self.refresh_employee_list(filtered_data)
        
        # POKAŻ/UKRYJ KAFELEK PODSUMOWANIA
        if filter_wydzial or filter_zmiana or filter_status or filter_nazwisko:
            self.show_summary_tile(filtered_data, filter_wydzial, filter_zmiana, filter_status)
        else:
            self.hide_summary_tile()

    def show_summary_tile(self, filtered_data, filter_wydzial, filter_zmiana, filter_status):
        """Pokazuje KOMPAKTOWY kafelek z podsumowaniem filtrowania"""
        # Wyczyść poprzednią zawartość
        for widget in self.summary_content_frame.winfo_children():
            widget.destroy()
        
        # KOMPAKTOWY NAGŁÓWEK - jedna linia
        header_frame = ttk.Frame(self.summary_content_frame)
        header_frame.pack(fill='x', pady=3)
        
        # Filtry w jednej linii
        filters_applied = []
        if filter_wydzial:
            filters_applied.append(f"🏭 {filter_wydzial}")
        if filter_zmiana:
            filters_applied.append(f"🕐 {filter_zmiana}")
        if filter_status:
            filters_applied.append(f"📊 {filter_status}")
        
        if filters_applied:
            filter_text = " • ".join(filters_applied)
        else:
            filter_text = "👥 Wszyscy pracownicy"
        
        # GŁÓWNA INFORMACJA W JEDNEJ LINII
        main_info_frame = ttk.Frame(header_frame)
        main_info_frame.pack(fill='x')
        
        # Liczba pracowników - KOMPAKTOWA
        count_label = tk.Label(main_info_frame, text=f"📋 {len(filtered_data)}", 
                              font=('Arial', 14, 'bold'), foreground='#1E6FBA')
        count_label.pack(side='left', padx=(0, 10))
        
        # Filtry - KOMPAKTOWE
        filter_label = tk.Label(main_info_frame, text=filter_text, 
                               font=('Arial', 9), foreground='#666666')
        filter_label.pack(side='left')
        
        # PRZYCISK ZAMKNIĘCIA PODSUMOWANIA
        close_btn = ttk.Button(main_info_frame, text="✕", width=2, 
                              command=self.hide_summary_tile,
                              style='Small.TButton')
        close_btn.pack(side='right')
        
        # STATYSTYKI STATUSÓW - W JEDNEJ LINII (jeśli są dane)
        status_counts = self.calculate_status_counts(filtered_data)
        if any(count > 0 for count in status_counts.values()):
            stats_frame = ttk.Frame(self.summary_content_frame)
            stats_frame.pack(fill='x', pady=2)
            
            # Pobierz kolory statusów
            status_colors = {}
            try:
                status_config = self.emp_manager.get_statuses_config()
                for name, color in status_config:
                    status_colors[name] = color
            except:
                status_colors = {"W Pracy": "#3CB371", "Urlop": "#FFA500", "L4": "#FF4500", "Wolne": "#98FB98"}
            
            # Statystyki w JEDNEJ LINII - kompaktowe
            stats_texts = []
            for status, count in status_counts.items():
                if count > 0:
                    color = status_colors.get(status, '#666666')
                    # Używaj emoji zamiast kolorowych kwadratów dla oszczędności miejsca
                    emoji_map = {"W Pracy": "🟢", "Urlop": "🟠", "L4": "🔴", "Wolne": "🟢"}
                    emoji = emoji_map.get(status, "▪")
                    stats_texts.append(f"{emoji} {status}: {count}")
            
            if stats_texts:
                stats_label = tk.Label(stats_frame, text="  ".join(stats_texts), 
                                     font=('Arial', 8), foreground='#444444')
                stats_label.pack()
        
        # ALERTY KADROWE - tylko jeśli są braki (BARDZO KOMPAKTOWE)
        alerts = self.check_staffing_alerts_for_filtered(filtered_data)
        if alerts:
            alerts_frame = ttk.Frame(self.summary_content_frame)
            alerts_frame.pack(fill='x', pady=2)
            
            alert_texts = []
            for alert in alerts[:1]:  # Tylko 1 najważniejszy alert
                alert_texts.append(f"🚨 {alert['wydzial']}-{alert['zmiana']}: -{alert['brakuje']}")
            
            alert_label = tk.Label(alerts_frame, text=" | ".join(alert_texts), 
                                 font=('Arial', 8, 'bold'), foreground='#E74C3C')
            alert_label.pack()
        
        # DODAJ INFORMACJE O PRZEKROCZENIACH
        overflow_alerts = self.emp_manager.get_overflow_alerts()
        current_overflow = [oa for oa in overflow_alerts 
                           if (not filter_wydzial or oa['wydzial'] == filter_wydzial) and
                              (not filter_zmiana or oa['zmiana'] == filter_zmiana)]
        
        if current_overflow:
            overflow_frame = ttk.Frame(self.summary_content_frame)
            overflow_frame.pack(fill='x', pady=2)
            
            overflow_texts = []
            for alert in current_overflow[:2]:  # Maksymalnie 2 alerty
                overflow_texts.append(f"⚠️ {alert['wydzial']}-{alert['zmiana']}: +{alert['nadmiar']}")
            
            overflow_label = tk.Label(overflow_frame, text=" | ".join(overflow_texts), 
                                     font=('Arial', 8, 'bold'), foreground='#FF8C00')
            overflow_label.pack()
    
        # Pokazuj kafelek
        self.summary_tile_frame.grid()

    def check_staffing_alerts_for_filtered(self, filtered_data):
        """Sprawdza alerty tylko dla przefiltrowanych danych"""
        alerts = []
        
        # Grupuj przefiltrowanych pracowników według wydziału i zmiany
        wydzial_zmiana_groups = {}
        for emp in filtered_data:
            key = (emp[4], emp[5])  # (wydzial, zmiana)
            if key not in wydzial_zmiana_groups:
                wydzial_zmiana_groups[key] = []
            wydzial_zmiana_groups[key].append(emp)
        
        # Sprawdź wymaganą obsadę dla każdej grupy
        for (wydzial, zmiana), employees in wydzial_zmiana_groups.items():
            required = self.emp_manager.get_required_staff_by_wydzial_shift(wydzial, zmiana)
            if required > 0:
                working_count = len([e for e in employees if e[6] == "W Pracy"])
                if working_count < required:
                    alerts.append({
                        'wydzial': wydzial,
                        'zmiana': zmiana,
                        'wymagane': required,
                        'aktualne': working_count,
                        'brakuje': required - working_count
                    })
        
        return alerts

    def hide_summary_tile(self):
        """Ukrywa kafelek podsumowania"""
        self.summary_tile_frame.grid_remove()

    def calculate_status_counts(self, employees):
        """Oblicza liczbę pracowników według statusów"""
        status_counts = {"W Pracy": 0, "Urlop": 0, "L4": 0, "Wolne": 0}
        for emp in employees:
            status = emp[6]
            if status in status_counts:
                status_counts[status] += 1
        return status_counts

    def reset_filters(self):
        self.dynamic_filter_vars["Wydział"].set('')
        self.dynamic_filter_vars["Zmiana"].set('')
        self.dynamic_filter_vars["Status"].set('')
        self.nazwisko_entry.delete(0, tk.END)
        self.refresh_employee_list()
        self.hide_summary_tile()

    def sort_column(self, tree, col, reverse):
        l = [(tree.set(k, col), k) for k in tree.get_children('')]
        
        if col == "ID":
            l.sort(key=lambda t: int(t[0]) if t[0].isdigit() else t[0], reverse=reverse)
        else:
            l.sort(key=lambda t: t[0].lower(), reverse=reverse)
            
        for index, (val, k) in enumerate(l):
            tree.move(k, '', index)
            
        tree.heading(col, command=lambda: self.sort_column(tree, col, not reverse))

    def get_selected_employee_ids(self):
        """Zwraca listę ID zaznaczonych pracowników"""
        selected_items = self.employee_tree.selection()
        selected_ids = []
        for item in selected_items:
            values = self.employee_tree.item(item, 'values')
            selected_ids.append(int(values[0]))
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
            EmployeeDialog(self, self.emp_manager, employee_data=data)

    def show_context_menu(self, event):
        item_id = self.employee_tree.identify_row(event.y)
        if not item_id: return
        
        self.employee_tree.selection_set(item_id)
        data = self.get_selected_employee_data()
        if not data: return

        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="✏️ Edytuj Pracownika", command=lambda: EmployeeDialog(self, self.emp_manager, employee_data=data))
        menu.add_separator()
        
        # NOWE OPCJE: Planowanie urlopu i L4
        menu.add_command(label="🏖️ Planuj urlop", 
                        command=lambda: VacationDialog(self, self.emp_manager, data[0], f"{data[1]} {data[2]}"))
        
        menu.add_command(label="🏥 Zarejestruj L4", 
                        command=lambda: L4Dialog(self, self.emp_manager, data[0], f"{data[1]} {data[2]}"))
        
        move_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="➡️ Przenieś", menu=move_menu)
        
        wydzial_menu = tk.Menu(move_menu, tearoff=0)
        move_menu.add_cascade(label="Zmień Wydział na...", menu=wydzial_menu)
        for wydzial in self.emp_manager.get_setting('wydzialy'):
            wydzial_menu.add_command(label=wydzial, command=lambda w=wydzial: self.safe_move_employee(data[0], new_wydzial=w))
            
        zmiana_menu = tk.Menu(move_menu, tearoff=0)
        move_menu.add_cascade(label="Zmień Zmianę na...", menu=zmiana_menu)
        for zmiana in [s[0] for s in self.emp_manager.get_shifts_config()]:
            zmiana_menu.add_command(label=zmiana, command=lambda z=zmiana: self.safe_move_employee(data[0], new_zmiana=z))
            
        stanowisko_menu = tk.Menu(move_menu, tearoff=0)
        move_menu.add_cascade(label="Zmień Stanowisko na...", menu=stanowisko_menu)
        for stanowisko in self.emp_manager.get_setting('stanowiska'):
             stanowisko_menu.add_command(label=stanowisko, command=lambda s=stanowisko: self.safe_move_employee(data[0], new_stanowisko=s))

        menu.add_separator()
        
        status_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="🔄 Zmień Status na...", menu=status_menu)
        for status in [s[0] for s in self.emp_manager.get_statuses_config()]:
            status_menu.add_command(label=status, command=lambda s=status: self.change_status_action(data[0], s))

        menu.add_command(label="⚙️ Zmień Maszynę/Urządzenie", command=lambda: MachineDialog(self, self.emp_manager, data[0], f"{data[1]} {data[2]}", data[7]))

        menu.add_separator()
        menu.add_command(label="🗑️ Usuń Pracownika", command=lambda: self.delete_employee_action(data[0]))
        
        menu.tk_popup(event.x_root, event.y_root)

    # FUNKCJE DO OPERACJI GRUPOWYCH

    def bulk_change_status(self):
        """Grupowa zmiana statusu dla zaznaczonych pracowników"""
        selected_ids = self.get_selected_employee_ids()
        if not selected_ids:
            messagebox.showwarning("Brak zaznaczenia", "Zaznacz przynajmniej jednego pracownika.")
            return
        
        # Okno dialogowe do wyboru statusu
        status_dialog = tk.Toplevel(self)
        status_dialog.title("Grupowa zmiana statusu")
        status_dialog.geometry("300x150")
        status_dialog.transient(self)
        status_dialog.grab_set()
        
        tk.Label(status_dialog, text=f"Zmiana statusu dla {len(selected_ids)} pracowników", 
                font=('Arial', 10, 'bold')).pack(pady=10)
        
        status_var = tk.StringVar()
        status_combo = ttk.Combobox(status_dialog, textvariable=status_var, 
                                  values=[s[0] for s in self.emp_manager.get_statuses_config()], 
                                  state='readonly')
        status_combo.pack(pady=5)
        
        def apply_bulk_status():
            new_status = status_var.get()
            if not new_status:
                messagebox.showwarning("Błąd", "Wybierz status.")
                return
                
            success_count = 0
            for emp_id in selected_ids:
                if self.emp_manager.update_employee_status(emp_id, new_status):
                    success_count += 1
            
            status_dialog.destroy()
            messagebox.showinfo("Sukces", f"Zmieniono status dla {success_count}/{len(selected_ids)} pracowników.")
            self.refresh_employee_list()
        
        ttk.Button(status_dialog, text="Zastosuj", command=apply_bulk_status).pack(pady=10)
        
        # Centrowanie okna
        status_dialog.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (status_dialog.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (status_dialog.winfo_height() // 2)
        status_dialog.geometry(f'+{x}+{y}')

    def bulk_move_employees(self):
        """Grupowe przenoszenie zaznaczonych pracowników"""
        selected_ids = self.get_selected_employee_ids()
        if not selected_ids:
            messagebox.showwarning("Brak zaznaczenia", "Zaznacz przynajmniej jednego pracownika.")
            return
        
        # Okno dialogowe do wyboru parametrów przeniesienia
        move_dialog = tk.Toplevel(self)
        move_dialog.title("Grupowe przeniesienie")
        move_dialog.geometry("350x200")
        move_dialog.transient(self)
        move_dialog.grab_set()
        
        tk.Label(move_dialog, text=f"Przeniesienie {len(selected_ids)} pracowników", 
                font=('Arial', 10, 'bold')).pack(pady=10)
        
        # Wydział
        wydzial_frame = ttk.Frame(move_dialog)
        wydzial_frame.pack(fill='x', padx=20, pady=5)
        tk.Label(wydzial_frame, text="Nowy wydział:").pack(side='left')
        wydzial_var = tk.StringVar()
        wydzial_combo = ttk.Combobox(wydzial_frame, textvariable=wydzial_var, 
                                   values=self.emp_manager.get_setting('wydzialy'), 
                                   state='readonly')
        wydzial_combo.pack(side='left', padx=10)
        
        # Zmiana
        zmiana_frame = ttk.Frame(move_dialog)
        zmiana_frame.pack(fill='x', padx=20, pady=5)
        tk.Label(zmiana_frame, text="Nowa zmiana:").pack(side='left')
        zmiana_var = tk.StringVar()
        zmiana_combo = ttk.Combobox(zmiana_frame, textvariable=zmiana_var, 
                                  values=[s[0] for s in self.emp_manager.get_shifts_config()], 
                                  state='readonly')
        zmiana_combo.pack(side='left', padx=10)
        
        # Stanowisko
        stanowisko_frame = ttk.Frame(move_dialog)
        stanowisko_frame.pack(fill='x', padx=20, pady=5)
        tk.Label(stanowisko_frame, text="Nowe stanowisko:").pack(side='left')
        stanowisko_var = tk.StringVar()
        stanowisko_combo = ttk.Combobox(stanowisko_frame, textvariable=stanowisko_var, 
                                      values=self.emp_manager.get_setting('stanowiska'), 
                                      state='readonly')
        stanowisko_combo.pack(side='left', padx=10)
        
        def apply_bulk_move():
            new_wydzial = wydzial_var.get() or None
            new_zmiana = zmiana_var.get() or None
            new_stanowisko = stanowisko_var.get() or None
            
            if not any([new_wydzial, new_zmiana, new_stanowisko]):
                messagebox.showwarning("Błąd", "Wybierz przynajmniej jeden parametr do zmiany.")
                return
                
            success_count = self.safe_bulk_move(selected_ids, new_wydzial, new_zmiana, new_stanowisko)
            
            move_dialog.destroy()
            messagebox.showinfo("Sukces", f"Przeniesiono {success_count}/{len(selected_ids)} pracowników.")
            self.refresh_employee_list()
        
        ttk.Button(move_dialog, text="Zastosuj", command=apply_bulk_move).pack(pady=10)
        
        # Centrowanie okna
        move_dialog.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (move_dialog.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (move_dialog.winfo_height() // 2)
        move_dialog.geometry(f'+{x}+{y}')

    def bulk_change_machine(self):
        """Grupowa zmiana maszyny dla zaznaczonych pracowników"""
        selected_ids = self.get_selected_employee_ids()
        if not selected_ids:
            messagebox.showwarning("Brak zaznaczenia", "Zaznacz przynajmniej jednego pracownika.")
            return
        
        # Okno dialogowe do wyboru maszyny
        machine_dialog = tk.Toplevel(self)
        machine_dialog.title("Grupowa zmiana maszyny")
        machine_dialog.geometry("300x150")
        machine_dialog.transient(self)
        machine_dialog.grab_set()
        
        tk.Label(machine_dialog, text=f"Zmiana maszyny dla {len(selected_ids)} pracowników", 
                font=('Arial', 10, 'bold')).pack(pady=10)
        
        machine_var = tk.StringVar()
        machine_combo = ttk.Combobox(machine_dialog, textvariable=machine_var, 
                                   values=self.emp_manager.get_setting('maszyny'), 
                                   state='readonly')
        machine_combo.pack(pady=5)
        
        def apply_bulk_machine():
            new_machine = machine_var.get()
            if not new_machine:
                messagebox.showwarning("Błąd", "Wybierz maszynę.")
                return
                
            success_count = 0
            for emp_id in selected_ids:
                if self.emp_manager.update_employee_machine(emp_id, new_machine):
                    success_count += 1
            
            machine_dialog.destroy()
            messagebox.showinfo("Sukces", f"Zmieniono maszynę dla {success_count}/{len(selected_ids)} pracowników.")
            self.refresh_employee_list()
        
        ttk.Button(machine_dialog, text="Zastosuj", command=apply_bulk_machine).pack(pady=10)
        
        # Centrowanie okna
        machine_dialog.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (machine_dialog.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (machine_dialog.winfo_height() // 2)
        machine_dialog.geometry(f'+{x}+{y}')

    def bulk_delete_employees(self):
        """Grupowe usuwanie zaznaczonych pracowników"""
        selected_ids = self.get_selected_employee_ids()
        if not selected_ids:
            messagebox.showwarning("Brak zaznaczenia", "Zaznacz przynajmniej jednego pracownika.")
            return
        
        if messagebox.askyesno("Potwierdzenie", 
                              f"Czy na pewno chcesz usunąć {len(selected_ids)} zaznaczonych pracowników?"):
            success_count = 0
            for emp_id in selected_ids:
                if self.emp_manager.delete_employee(emp_id):
                    success_count += 1
            
            messagebox.showinfo("Sukces", f"Usunięto {success_count}/{len(selected_ids)} pracowników.")
            self.refresh_employee_list()

    # FUNKCJE DO SZYBKIEGO WYSZUKIWANIA

    def find_without_position(self):
        """Wyszukuje pracowników bez ustawionego stanowiska"""
        filtered_data = []
        for emp in self.all_employees_data:
            stanowisko = str(emp[3]).strip() if emp[3] else ""
            if (not stanowisko or 
                stanowisko.lower() in ['', 'nieustawione', 'brak', 'none', 'null']):
                filtered_data.append(emp)
        
        if filtered_data:
            self.refresh_employee_list(filtered_data)
            messagebox.showinfo("Znaleziono", f"Znaleziono {len(filtered_data)} pracowników bez stanowiska.")
        else:
            messagebox.showinfo("Brak wyników", "Wszyscy pracownicy mają ustawione stanowisko.")

    def find_without_department(self):
        """Wyszukuje pracowników bez ustawionego wydziału"""
        filtered_data = []
        for emp in self.all_employees_data:
            wydzial = str(emp[4]).strip() if emp[4] else ""
            if (not wydzial or 
                wydzial.lower() in ['', 'nieustawiony', 'brak', 'none', 'null']):
                filtered_data.append(emp)
        
        if filtered_data:
            self.refresh_employee_list(filtered_data)
            messagebox.showinfo("Znaleziono", f"Znaleziono {len(filtered_data)} pracowników bez wydziału.")
        else:
            messagebox.showinfo("Brak wyników", "Wszyscy pracownicy mają ustawiony wydział.")

    def find_without_machine(self):
        """Wyszukuje pracowników bez ustawionej maszyny"""
        filtered_data = []
        for emp in self.all_employees_data:
            maszyna = str(emp[7]).strip() if emp[7] else ""
            if (not maszyna or 
                maszyna.lower() in ['', 'brak', 'none', 'null', 'nieustawione']):
                filtered_data.append(emp)
        
        if filtered_data:
            self.refresh_employee_list(filtered_data)
            messagebox.showinfo("Znaleziono", f"Znaleziono {len(filtered_data)} pracowników bez maszyny.")
        else:
            messagebox.showinfo("Brak wyników", "Wszyscy pracownicy mają ustawioną maszynę.")

    def find_all_missing_data(self):
        """Wyszukuje wszystkich pracowników z jakimikolwiek brakującymi danymi"""
        filtered_data = []
        for emp in self.all_employees_data:
            stanowisko = str(emp[3]).strip() if emp[3] else ""
            wydzial = str(emp[4]).strip() if emp[4] else ""
            maszyna = str(emp[7]).strip() if emp[7] else ""
            
            if (not stanowisko or stanowisko.lower() in ['', 'nieustawione', 'brak', 'none', 'null'] or
                not wydzial or wydzial.lower() in ['', 'nieustawiony', 'brak', 'none', 'null'] or
                not maszyna or maszyna.lower() in ['', 'brak', 'none', 'null', 'nieustawione']):
                filtered_data.append(emp)
        
        if filtered_data:
            self.refresh_employee_list(filtered_data)
            messagebox.showinfo("Znaleziono", f"Znaleziono {len(filtered_data)} pracowników z brakującymi danymi.")
            
            missing_details = self.analyze_missing_data(filtered_data)
            detail_msg = f"Szczegóły brakujących danych:\n{missing_details}"
            messagebox.showinfo("Szczegóły brakujących danych", detail_msg)
        else:
            messagebox.showinfo("Brak wyników", "Wszyscy pracownicy mają kompletne dane.")

    def analyze_missing_data(self, employees):
        """Analizuje jakie dane są brakujące u pracowników"""
        missing_position = 0
        missing_department = 0
        missing_machine = 0
        
        for emp in employees:
            stanowisko = str(emp[3]).strip() if emp[3] else ""
            wydzial = str(emp[4]).strip() if emp[4] else ""
            maszyna = str(emp[7]).strip() if emp[7] else ""
            
            if not stanowisko or stanowisko.lower() in ['', 'nieustawione', 'brak', 'none', 'null']:
                missing_position += 1
            if not wydzial or wydzial.lower() in ['', 'nieustawiony', 'brak', 'none', 'null']:
                missing_department += 1
            if not maszyna or maszyna.lower() in ['', 'brak', 'none', 'null', 'nieustawione']:
                missing_machine += 1
    
        return (f"• Bez stanowiska: {missing_position}\n"
                f"• Bez wydziału: {missing_department}\n"
                f"• Bez maszyny: {missing_machine}")

    # NOWE FUNKCJE

    def show_color_editor(self):
        """Otwiera edytor kolorów"""
        ColorEditor(self, self.emp_manager)

    def create_backup(self):
        """Tworzy backup bazy danych"""
        backup_file = self.db_manager.backup_database()
        if backup_file:
            messagebox.showinfo("Backup", f"Utworzono backup bazy danych:\n{backup_file}")
        else:
            messagebox.showerror("Błąd", "Nie udało się utworzyć backupu.")

    def export_to_excel(self):
        """Eksportuje dane do Excela"""
        try:
            import pandas as pd
            
            # Pobierz dane urlopów i L4
            vacations = self.emp_manager.get_vacations()
            l4_records = self.emp_manager.get_l4_records()
            
            # Przygotuj dane z nowymi kolumnami
            export_data = []
            for emp in self.all_employees_data:
                emp_id, imie, nazwisko, stanowisko, wydzial, zmiana, status, maszyna = emp
                
                # Znajdź urlop dla pracownika
                vacation_info = ""
                for vac in vacations:
                    if vac[1] == emp_id:  # vac[1] to employee_id
                        start = vac[2]  # start_date
                        end = vac[3]    # end_date
                        vacation_info = f"{start} - {end}"
                        break
                
                # Znajdź L4 dla pracownika
                l4_info = ""
                for l4 in l4_records:
                    if l4[1] == emp_id:  # l4[1] to employee_id
                        start = l4[2]  # start_date
                        end = l4[3]    # end_date
                        l4_info = f"{start} - {end}"
                        break
                
                # Dodaj pracownika z wszystkimi kolumnami
                export_data.append({
                    "ID": emp_id,
                    "Imię": imie,
                    "Nazwisko": nazwisko,
                    "Stanowisko": stanowisko,
                    "Wydział": wydzial,
                    "Zmiana": zmiana,
                    "Status": status,
                    "Maszyna/Urządzenie": maszyna,
                    "Urlop od-do": vacation_info,
                    "L4 od-do": l4_info
                })
            
            # Utwórz DataFrame z wszystkimi kolumnami
            df = pd.DataFrame(export_data)
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx", 
                filetypes=[("Excel files", "*.xlsx")], 
                title="Zapisz dane do Excel"
            )
            
            if file_path:
                with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                    df.to_excel(writer, sheet_name='Pracownicy', index=False)
                    
                    workbook = writer.book
                    worksheet = writer.sheets['Pracownicy']
                    
                    # Formatowanie
                    header_format = workbook.add_format({
                        'bold': True,
                        'text_wrap': True,
                        'valign': 'top',
                        'fg_color': '#D7E4BC',
                        'border': 1
                    })
                    
                    for col_num, value in enumerate(df.columns.values):
                        worksheet.write(0, col_num, value, header_format)
                    
                    for i, col in enumerate(df.columns):
                        max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                        worksheet.set_column(i, i, max_len)
                
                self.emp_manager.log_history("Export Excel", f"Wyeksportowano dane do {file_path}")
                messagebox.showinfo("Sukces", f"Dane zostały wyeksportowane do:\n{file_path}\n\nZawiera nowe kolumny: Urlop od-do i L4 od-do")
                
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd podczas eksportu do Excel: {e}")

    def check_alerts_periodically(self):
        """Automatyczne sprawdzanie alertów o brakach kadrowych"""
        try:
            alerts = self.emp_manager.check_staffing_alerts()
            if alerts:
                alert_text = "🚨 ALERT - Braki kadrowe:\n\n"
                for alert in alerts:
                    alert_text += f"• {alert['wydzial']} - {alert['zmiana']}: brakuje {alert['brakuje']} osób\n"
                
                # Pokazuj alert tylko raz na godzinę
                if not hasattr(self, '_last_alert_time') or \
                   (datetime.now() - getattr(self, '_last_alert_time', datetime.now())).total_seconds() > 3600:
                    messagebox.showwarning("Alert Kadrowy", alert_text)
                    self._last_alert_time = datetime.now()
            
            # Sprawdzaj co 5 minut
            self.after(300000, self.check_alerts_periodically)
            
        except Exception as e:
            print(f"Błąd sprawdzania alertów: {e}")
            self.after(300000, self.check_alerts_periodically)

    def move_employee_action(self, emp_id, new_wydzial=None, new_zmiana=None, new_stanowisko=None):
        if self.safe_move_employee(emp_id, new_wydzial, new_zmiana, new_stanowisko):
            messagebox.showinfo("Sukces", "Pracownik przeniesiony i historia zapisana.")
            self.refresh_employee_list()
        else:
            messagebox.showerror("Błąd", "Nie udało się przenieść pracownika.")

    def change_status_action(self, emp_id, new_status):
        if self.emp_manager.update_employee_status(emp_id, new_status):
            messagebox.showinfo("Sukces", f"Status zmieniony na '{new_status}' i historia zapisana.")
            self.refresh_employee_list()
        else:
            messagebox.showerror("Błąd", "Nie udało się zmienić statusu.")
        
    def delete_employee_action(self, emp_id):
        if messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz usunąć tego pracownika?"):
            if self.emp_manager.delete_employee(emp_id):
                messagebox.showinfo("Sukces", "Pracownik usunięty.")
                self.refresh_employee_list()
            else:
                messagebox.showerror("Błąd", "Nie udało się usunąć pracownika.")

    def open_add_employee_dialog(self):
        EmployeeDialog(self, self.emp_manager)
        
    def show_summary(self):
        SummaryWindow(self, self.emp_manager)

    def show_history(self):
        HistoryWindow(self, self.emp_manager)

    def show_settings(self):
        if self.current_user and self.current_user.get('role') in ['admin', 'manager']:
            SettingsWindow(self, self.emp_manager)
        else:
            messagebox.showerror("Brak uprawnień", "Tylko administratorzy i menedżerowie mogą otwierać ustawienia.")
    
    def import_employees_from_excel(self):
        file_path = filedialog.askopenfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")], title="Wybierz plik Excel do importu")
        
        if file_path:
            try:
                df = pd.read_excel(file_path)
                
                required_cols = ["imie", "nazwisko"] 
                
                df.columns = [c.lower().replace(' ', '_') for c in df.columns]

                df['stanowisko'] = df.get('stanowisko', 'Nieustawione')
                df['wydzial'] = df.get('wydzial', 'Nieustawiony')
                df['zmiana'] = df.get('zmiana', 'D - Wolne')
                df['status'] = df.get('status', 'Wolne')
                df['maszyna'] = df.get('maszyna', 'Brak')
                
                cols_to_insert = ['imie', 'nazwisko', 'stanowisko', 'wydzial', 'zmiana', 'status', 'maszyna']
                
                imported_count = 0
                for index, row in df.iterrows():
                    if pd.isna(row['imie']) or pd.isna(row['nazwisko']):
                        continue
                        
                    data = tuple(row[col] for col in cols_to_insert)
                    
                    self.db_manager.execute_query("""
                        INSERT INTO employees (imie, nazwisko, stanowisko, wydzial, zmiana, status, maszyna)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, data)
                    imported_count += 1
                
                self.emp_manager.log_history("Import Excel", f"Zaimportowano {imported_count} pracowników z pliku {file_path}")
                messagebox.showinfo("Sukces Importu", f"Zaimportowano {imported_count} pracowników.")
                self.refresh_employee_list()
                
            except Exception as e:
                messagebox.showerror("Błąd Importu", f"Błąd podczas wczytywania pliku Excel: {e}")

    def logout(self):
        if messagebox.askyesno("Wylogowanie", "Czy na pewno chcesz się wylogować?"):
            self.current_user = None
            self.emp_manager.set_current_user(None)
            self.destroy()
            # Restart aplikacji
            app = MainWindow()
            app.mainloop()

    def on_closing(self):
        if messagebox.askokcancel("Wyjście", "Czy na pewno chcesz zamknąć aplikację?"):
            self.db_manager.conn.close()
            self.destroy()

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
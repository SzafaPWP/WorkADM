import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import pandas as pd
from collections import defaultdict

class SummaryWindow(tk.Toplevel):
    def __init__(self, master, emp_manager):
        super().__init__(master)
        self.master = master
        self.emp_manager = emp_manager
        self.title("📊 Podsumowanie Kadrowe")
        
        # Ustawienia dla drugiego monitora
        self.attributes('-topmost', False)  # Nie zawsze na wierzchu
        self.transient(master)
        
        # Umożliwia niezależną pracę na drugim monitorze
        self.grab_release()
        
        # Ustaw rozmiar na 90% drugiego monitora
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.9)
        x_position = int((screen_width - window_width) / 2)
        y_position = int((screen_height - window_height) / 2)
        
        self.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        
        self.filtered_data = []
        self.current_filters = {}
        
        self.create_widgets()
        
        # NOWOŚĆ: Natychmiastowe odświeżenie po otwarciu (bez migania/auto-refresh)
        self.apply_filters()

    def create_widgets(self):
        # Główny kontener
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Nagłówek
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(header_frame, text="📊 Zaawansowane Podsumowanie Kadrowe", 
                 font=('Arial', 16, 'bold')).pack(side='left')
        
        # NOWOŚĆ: Usunięto przycisk auto-refresh
        ttk.Button(header_frame, text="📤 Eksportuj do Excel",
                  command=self.export_summary).pack(side='right', padx=5)
        
        # Sekcja filtrów
        self.create_filters_section(main_frame)
        
        # Sekcja kafelków (początkowo ukryta)
        self.tiles_frame = ttk.LabelFrame(main_frame, text="📈 Podsumowanie", padding="15")
        self.tiles_frame.pack(fill="x", pady=(0, 15))
        self.tiles_frame.pack_forget()  # Ukryj na starcie
        
        # Sekcja listy pracowników
        self.create_employees_section(main_frame)
        
        main_frame.grid_rowconfigure(3, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

    def create_filters_section(self, parent):
        """Tworzy sekcję filtrów z automatycznym zastosowaniem"""
        filter_frame = ttk.LabelFrame(parent, text="🔍 Filtry Podsumowania", padding="15")
        filter_frame.pack(fill="x", pady=(0, 15))
        
        # Pierwszy wiersz filtrów
        row1_frame = ttk.Frame(filter_frame)
        row1_frame.pack(fill="x", pady=5)
        
        ttk.Label(row1_frame, text="Wydział:", font=('Arial', 10)).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.wydzial_var = tk.StringVar()
        self.wydzial_combo = ttk.Combobox(row1_frame, textvariable=self.wydzial_var,
                                        values=[''] + self.emp_manager.get_setting('wydzialy'),
                                        state='readonly', width=25)
        self.wydzial_combo.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.wydzial_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filters())
        
        ttk.Label(row1_frame, text="Zmiana:", font=('Arial', 10)).grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.zmiana_var = tk.StringVar()
        self.zmiana_combo = ttk.Combobox(row1_frame, textvariable=self.zmiana_var,
                                       values=[''] + [s[0] for s in self.emp_manager.get_shifts_config()],
                                       state='readonly', width=25)
        self.zmiana_combo.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        self.zmiana_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filters())
        
        ttk.Label(row1_frame, text="Status:", font=('Arial', 10)).grid(row=0, column=4, padx=5, pady=5, sticky='w')
        self.status_var = tk.StringVar()
        self.status_combo = ttk.Combobox(row1_frame, textvariable=self.status_var,
                                       values=[''] + [s[0] for s in self.emp_manager.get_statuses_config()],
                                       state='readonly', width=25)
        self.status_combo.grid(row=0, column=5, padx=5, pady=5, sticky='w')
        self.status_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filters())
        
        # Drugi wiersz filtrów
        row2_frame = ttk.Frame(filter_frame)
        row2_frame.pack(fill="x", pady=5)
        
        ttk.Label(row2_frame, text="Stanowisko:", font=('Arial', 10)).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.stanowisko_var = tk.StringVar()
        self.stanowisko_combo = ttk.Combobox(row2_frame, textvariable=self.stanowisko_var,
                                           values=[''] + self.emp_manager.get_setting('stanowiska'),
                                           state='readonly', width=25)
        self.stanowisko_combo.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.stanowisko_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filters())
        
        ttk.Label(row2_frame, text="Maszyna:", font=('Arial', 10)).grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.maszyna_var = tk.StringVar()
        self.maszyna_combo = ttk.Combobox(row2_frame, textvariable=self.maszyna_var,
                                        values=[''] + self.emp_manager.get_setting('maszyny'),
                                        state='readonly', width=25)
        self.maszyna_combo.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        self.maszyna_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filters())
        
        # Przyciski akcji
        button_frame = ttk.Frame(filter_frame)
        button_frame.pack(fill="x", pady=10)
        
        ttk.Button(button_frame, text="🗑️ Wyczyść Wszystkie Filtry", 
                  command=self.clear_filters).pack(side='left', padx=5)
        ttk.Button(button_frame, text="📊 Pokaż Wszystkich", 
                  command=self.show_all_employees).pack(side='left', padx=5)
        # NOWOŚĆ: Usunięto przycisk auto-refresh
        
        # Ustaw równe rozłożenie kolumn
        for i in range(6):
            row1_frame.columnconfigure(i, weight=1)
            row2_frame.columnconfigure(i, weight=1)

    def create_employees_section(self, parent):
        """Tworzy sekcję listy pracowników"""
        employees_frame = ttk.LabelFrame(parent, text="👥 Lista Pracowników", padding="10")
        employees_frame.pack(fill="both", expand=True)
        
        # Tworzenie Treeview z tymi samymi kolumnami co w głównym oknie
        columns = ("ID", "Imię", "Nazwisko", "Stanowisko", "Wydział", "Zmiana", "Status", "Maszyna/Urządzenie")
        self.employees_tree = ttk.Treeview(employees_frame, columns=columns, show="headings", selectmode='extended')
        
        # Konfiguracja kolumn
        column_widths = {
            "ID": 50, "Imię": 120, "Nazwisko": 120, "Stanowisko": 150,
            "Wydział": 150, "Zmiana": 150, "Status": 100, "Maszyna/Urządzenie": 200
        }
        
        for col in columns:
            self.employees_tree.heading(col, text=col)
            self.employees_tree.column(col, width=column_widths.get(col, 120), anchor=tk.W)
        
        # Scrollbary
        v_scroll = ttk.Scrollbar(employees_frame, orient="vertical", command=self.employees_tree.yview)
        h_scroll = ttk.Scrollbar(employees_frame, orient="horizontal", command=self.employees_tree.xview)
        self.employees_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Układ
        self.employees_tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        
        employees_frame.grid_rowconfigure(0, weight=1)
        employees_frame.grid_columnconfigure(0, weight=1)
        
        # Bindowanie zdarzeń
        self.employees_tree.bind('<Double-1>', self.on_double_click_employee)
        self.employees_tree.bind('<Button-3>', self.show_context_menu)
        self.employees_tree.bind('<<TreeviewSelect>>', self.on_selection_change)
        
        # Etykieta z liczbą znalezionych pracowników
        self.count_label = ttk.Label(employees_frame, text="Znaleziono: 0 pracowników", 
                                   font=('Arial', 10, 'bold'))
        self.count_label.grid(row=2, column=0, sticky="w", pady=5)

    def create_tiles_section(self):
        """Tworzy sekcję kafelków z podsumowaniami"""
        # Wyczyść poprzednie kafelki
        for widget in self.tiles_frame.winfo_children():
            widget.destroy()
        
        # Oblicz statystyki
        stats = self.calculate_statistics()
        
        # Kafelek 1: Podsumowanie ogólne
        tile1 = self.create_tile("📊 OGÓLNE", [
            f"Łącznie: {stats['total']}",
            f"W Pracy: {stats['working']}",
            f"Urlopy: {stats['vacation']}",
            f"L4: {stats['l4']}",
            f"Wolne: {stats['free']}"
        ], "#4CAF50")
        
        # Kafelek 2: Podsumowanie zmian
        tile2 = self.create_tile("🕐 ZMIANY", [
            f"Zmiana A: {stats['shift_a']}",
            f"Zmiana B: {stats['shift_b']}",
            f"Zmiana C: {stats['shift_c']}",
            f"Zmiana D: {stats['shift_d']}",
            f"Razem: {stats['total_shifts']}"
        ], "#2196F3")
        
        # Kafelek 3: Wymagana obsada
        tile3 = self.create_tile("🎯 OBSADA", [
            f"Wymagana: {stats['required_total']}",
            f"Aktualna: {stats['current_total']}",
            f"Brakuje: {stats['shortage_total']}",
            f"Nadmiar: {stats['overflow_total']}",
            f"Pokrycie: {stats['coverage_percent']}%"
        ], "#FF9800")
        
        # Kafelek 4: Alerty
        tile4 = self.create_tile("🚨 ALERTY", [
            f"Brakujących: {len(stats['shortages'])}",
            f"Przekroczeń: {len(stats['overflows'])}",
            f"Bez stanowiska: {stats['no_position']}",
            f"Bez maszyny: {stats['no_machine']}",
            f"Status: {'OK' if not stats['alerts'] else 'PROBLEMY'}"
        ], "#F44336")
        
        # Układ kafelków
        tile1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        tile2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        tile3.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        tile4.grid(row=0, column=3, padx=10, pady=10, sticky="nsew")
        
        # Ustaw równe rozłożenie
        for i in range(4):
            self.tiles_frame.columnconfigure(i, weight=1)

    def create_tile(self, title, items, color):
        """Tworzy pojedynczy kafelek"""
        tile = ttk.Frame(self.tiles_frame, relief='solid', borderwidth=1)
        
        # Nagłówek kafelka
        header = tk.Frame(tile, bg=color, height=30)
        header.pack(fill="x")
        ttk.Label(header, text=title, font=('Arial', 12, 'bold'), 
                 background=color, foreground='white').pack(pady=5)
        
        # Zawartość kafelka
        content_frame = ttk.Frame(tile, padding="10")
        content_frame.pack(fill="both", expand=True)
        
        for item in items:
            ttk.Label(content_frame, text=item, font=('Arial', 10)).pack(anchor='w', pady=2)
        
        return tile

    def calculate_statistics(self):
        """Oblicza statystyki na podstawie przefiltrowanych danych"""
        stats = {
            'total': len(self.filtered_data),
            'working': 0, 'vacation': 0, 'l4': 0, 'free': 0,
            'shift_a': 0, 'shift_b': 0, 'shift_c': 0, 'shift_d': 0,
            'total_shifts': 0, 'required_total': 0, 'current_total': 0,
            'shortage_total': 0, 'overflow_total': 0, 'coverage_percent': 0,
            'no_position': 0, 'no_machine': 0, 'shortages': [], 'overflows': [], 'alerts': []
        }
        
        # Statystyki statusów
        for emp in self.filtered_data:
            status = emp[6]
            if status == "W Pracy": stats['working'] += 1
            elif status == "Urlop": stats['vacation'] += 1
            elif status == "L4": stats['l4'] += 1
            elif status == "Wolne": stats['free'] += 1
        
        # Statystyki zmian
        for emp in self.filtered_data:
            zmiana = emp[5]
            if "A -" in zmiana: stats['shift_a'] += 1
            elif "B -" in zmiana: stats['shift_b'] += 1
            elif "C -" in zmiana: stats['shift_c'] += 1
            elif "D -" in zmiana: stats['shift_d'] += 1
        
        stats['total_shifts'] = stats['shift_a'] + stats['shift_b'] + stats['shift_c'] + stats['shift_d']
        
        # Braki danych
        for emp in self.filtered_data:
            if not emp[3] or emp[3] in ['', 'Nieustawione', 'Brak']:
                stats['no_position'] += 1
            if not emp[7] or emp[7] in ['', 'Brak']:
                stats['no_machine'] += 1
        
        # Analiza obsady (tylko jeśli jest filtr na wydział/zmianę)
        if self.current_filters.get('wydzial') or self.current_filters.get('zmiana'):
            stats.update(self.calculate_staffing_stats())
        
        return stats

    def calculate_staffing_stats(self):
        """Oblicza statystyki związane z obsadą"""
        staffing_stats = {
            'required_total': 0, 'current_total': 0, 'shortage_total': 0,
            'overflow_total': 0, 'coverage_percent': 0, 'shortages': [], 'overflows': []
        }
        
        # Grupuj według wydziału i zmiany
        groups = {}
        for emp in self.filtered_data:
            if emp[6] == "W Pracy":  # Tylko pracujący
                key = (emp[4], emp[5])  # (wydzial, zmiana)
                if key not in groups:
                    groups[key] = 0
                groups[key] += 1
        
        # Analizuj każdę grupę
        for (wydzial, zmiana), count in groups.items():
            required = self.emp_manager.get_required_staff_by_wydzial_shift(wydzial, zmiana)
            if required > 0:
                staffing_stats['required_total'] += required
                staffing_stats['current_total'] += count
                
                if count < required:
                    shortage = required - count
                    staffing_stats['shortage_total'] += shortage
                    staffing_stats['shortages'].append({
                        'wydzial': wydzial, 'zmiana': zmiana,
                        'required': required, 'current': count, 'shortage': shortage
                    })
                elif count > required:
                    overflow = count - required
                    staffing_stats['overflow_total'] += overflow
                    staffing_stats['overflows'].append({
                        'wydzial': wydzial, 'zmiana': zmiana,
                        'required': required, 'current': count, 'overflow': overflow
                    })
        
        # Oblicz procent pokrycia
        if staffing_stats['required_total'] > 0:
            staffing_stats['coverage_percent'] = round(
                (staffing_stats['current_total'] / staffing_stats['required_total']) * 100, 1
            )
        
        staffing_stats['alerts'] = staffing_stats['shortages'] + staffing_stats['overflows']
        
        return staffing_stats

    def apply_filters(self, event=None):
        """NOWOŚĆ: Natychmiastowe odświeżenie po otwarciu i zmianach (bez auto-refresh)"""
        # Zbierz filtry
        filters = {
            'wydzial': self.wydzial_var.get(),
            'zmiana': self.zmiana_var.get(),
            'status': self.status_var.get(),
            'stanowisko': self.stanowisko_var.get(),
            'maszyna': self.maszyna_var.get()
        }
        
        self.current_filters = {k: v for k, v in filters.items() if v}
        
        # Filtruj dane
        all_employees = self.emp_manager.get_all_employees()
        self.filtered_data = []
        
        for emp in all_employees:
            matches = True
            
            for field, value in filters.items():
                if value:  # Jeśli filtr jest ustawiony
                    if field == 'wydzial' and emp[4] != value:
                        matches = False
                        break
                    elif field == 'zmiana' and emp[5] != value:
                        matches = False
                        break
                    elif field == 'status' and emp[6] != value:
                        matches = False
                        break
                    elif field == 'stanowisko' and emp[3] != value:
                        matches = False
                        break
                    elif field == 'maszyna' and emp[7] != value:
                        matches = False
                        break
            
            if matches:
                self.filtered_data.append(emp)
        
        # Aktualizuj widok
        self.update_display()

    def clear_filters(self):
        """Czyści wszystkie filtry"""
        self.wydzial_var.set('')
        self.zmiana_var.set('')
        self.status_var.set('')
        self.stanowisko_var.set('')
        self.maszyna_var.set('')
        
        self.current_filters = {}
        self.filtered_data = self.emp_manager.get_all_employees()
        self.update_display()

    def show_all_employees(self):
        """Pokazuje wszystkich pracowników"""
        self.filtered_data = self.emp_manager.get_all_employees()
        self.current_filters = {}
        self.update_display()

    def update_display(self):
        """Aktualizuje cały widok"""
        # Pokazuj/ukryj kafelki tylko jeśli są aktywne filtry
        if self.current_filters:
            self.tiles_frame.pack(fill="x", pady=(0, 15))
            self.create_tiles_section()
        else:
            self.tiles_frame.pack_forget()
        
        # Aktualizuj listę pracowników
        self.refresh_employees_list()
        
        # Aktualizuj licznik
        self.count_label.config(text=f"Znaleziono: {len(self.filtered_data)} pracowników")

    def refresh_employees_list(self):
        """Odświeża listę pracowników"""
        for item in self.employees_tree.get_children():
            self.employees_tree.delete(item)
        
        status_colors = {name: color for name, color in self.emp_manager.get_statuses_config()}
        
        for emp in self.filtered_data:
            emp_id, imie, nazwisko, stanowisko, wydzial, zmiana, status, maszyna = emp
            values = (emp_id, imie, nazwisko, stanowisko, wydzial, zmiana, status, maszyna)
            
            # Kolorowanie wierszy według statusu
            color_tag = status.replace(' ', '_')
            self.employees_tree.tag_configure(color_tag, background=status_colors.get(status, 'white'))
            
            self.employees_tree.insert("", tk.END, values=values, tags=(color_tag,))

    def on_selection_change(self, event):
        """Aktualizuje informacje o zaznaczeniu"""
        selected_count = len(self.employees_tree.selection())

    def on_double_click_employee(self, event):
        """Podwójne kliknięcie na pracownika - edycja"""
        selected_item = self.employees_tree.selection()
        if selected_item:
            values = self.employees_tree.item(selected_item[0], 'values')
            emp_id = values[0]
            full_data = self.emp_manager.db.fetch_one("SELECT * FROM employees WHERE id=?", (emp_id,))
            if full_data:
                from employee_dialog import EmployeeDialog
                dialog = EmployeeDialog(self, self.emp_manager, employee_data=full_data)
                # Po zamknięciu dialogu odśwież dane
                self.wait_window(dialog)
                self.apply_filters()

    def show_context_menu(self, event):
        """Pokazuje menu kontekstowe dla pracownika"""
        item_id = self.employees_tree.identify_row(event.y)
        if not item_id:
            return
            
        self.employees_tree.selection_set(item_id)
        values = self.employees_tree.item(item_id, 'values')
        emp_id = values[0]
        full_data = self.emp_manager.db.fetch_one("SELECT * FROM employees WHERE id=?", (emp_id,))
        
        if not full_data:
            return

        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="✏️ Edytuj Pracownika", 
                        command=lambda: self.open_employee_dialog(full_data))
        menu.add_separator()
        
        # Planowanie urlopu i L4
        menu.add_command(label="🏖️ Planuj urlop", 
                        command=lambda: self.open_vacation_dialog(full_data))
        menu.add_command(label="🏥 Zarejestruj L4", 
                        command=lambda: self.open_l4_dialog(full_data))
        
        # Menu przenoszenia
        move_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="➡️ Przenieś", menu=move_menu)
        
        # Przenoszenie między wydziałami
        wydzial_menu = tk.Menu(move_menu, tearoff=0)
        move_menu.add_cascade(label="Zmień Wydział na...", menu=wydzial_menu)
        for wydzial in self.emp_manager.get_setting('wydzialy'):
            wydzial_menu.add_command(label=wydzial, 
                                   command=lambda w=wydzial: self.move_employee(emp_id, new_wydzial=w))
        
        # Przenoszenie między zmianami
        zmiana_menu = tk.Menu(move_menu, tearoff=0)
        move_menu.add_cascade(label="Zmień Zmianę na...", menu=zmiana_menu)
        for zmiana in [s[0] for s in self.emp_manager.get_shifts_config()]:
            zmiana_menu.add_command(label=zmiana, 
                                  command=lambda z=zmiana: self.move_employee(emp_id, new_zmiana=z))
        
        # Przenoszenie między stanowiskami
        stanowisko_menu = tk.Menu(move_menu, tearoff=0)
        move_menu.add_cascade(label="Zmień Stanowisko na...", menu=stanowisko_menu)
        for stanowisko in self.emp_manager.get_setting('stanowiska'):
            stanowisko_menu.add_command(label=stanowisko, 
                                      command=lambda s=stanowisko: self.move_employee(emp_id, new_stanowisko=s))
        
        menu.add_separator()
        
        # Zmiana statusu
        status_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="🔄 Zmień Status na...", menu=status_menu)
        for status in [s[0] for s in self.emp_manager.get_statuses_config()]:
            status_menu.add_command(label=status, 
                                  command=lambda s=status: self.change_status(emp_id, s))
        
        menu.add_command(label="⚙️ Zmień Maszynę/Urządzenie", 
                        command=lambda: self.open_machine_dialog(full_data))
        
        menu.add_separator()
        menu.add_command(label="🗑️ Usuń Pracownika", 
                        command=lambda: self.delete_employee(emp_id))
        
        menu.tk_popup(event.x_root, event.y_root)

    # Metody pomocnicze dla menu kontekstowego
    def open_employee_dialog(self, employee_data):
        from employee_dialog import EmployeeDialog
        dialog = EmployeeDialog(self, self.emp_manager, employee_data=employee_data)
        self.wait_window(dialog)
        self.apply_filters()

    def open_vacation_dialog(self, employee_data):
        from vacation_dialog import VacationDialog
        dialog = VacationDialog(self, self.emp_manager, employee_data[0], f"{employee_data[1]} {employee_data[2]}")
        self.wait_window(dialog)
        self.apply_filters()

    def open_l4_dialog(self, employee_data):
        from l4_dialog import L4Dialog
        dialog = L4Dialog(self, self.emp_manager, employee_data[0], f"{employee_data[1]} {employee_data[2]}")
        self.wait_window(dialog)
        self.apply_filters()

    def open_machine_dialog(self, employee_data):
        from machine_dialog import MachineDialog
        MachineDialog(self, self.emp_manager, employee_data[0], f"{employee_data[1]} {employee_data[2]}", employee_data[7])

    def move_employee(self, emp_id, new_wydzial=None, new_zmiana=None, new_stanowisko=None):
        if hasattr(self.master, 'safe_move_employee'):
            success = self.master.safe_move_employee(emp_id, new_wydzial, new_zmiana, new_stanowisko)
        else:
            success = self.emp_manager.move_employee(emp_id, new_wydzial, new_zmiana, new_stanowisko)
        
        if success:
            messagebox.showinfo("Sukces", "Pracownik przeniesiony.")
            self.apply_filters()
        else:
            messagebox.showerror("Błąd", "Nie udało się przenieść pracownika.")

    def change_status(self, emp_id, new_status):
        if self.emp_manager.update_employee_status(emp_id, new_status):
            messagebox.showinfo("Sukces", f"Status zmieniony na '{new_status}'.")
            self.apply_filters()
        else:
            messagebox.showerror("Błąd", "Nie udało się zmienić statusu.")

    def delete_employee(self, emp_id):
        if messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz usunąć tego pracownika?"):
            if self.emp_manager.delete_employee(emp_id):
                messagebox.showinfo("Sukces", "Pracownik usunięty.")
                self.apply_filters()
            else:
                messagebox.showerror("Błąd", "Nie udało się usunąć pracownika.")

    def export_summary(self):
        """Eksportuje podsumowanie do Excel"""
        try:
            import pandas as pd
            from tkinter import filedialog
            
            # Przygotuj dane do eksportu
            export_data = []
            for emp in self.filtered_data:
                export_data.append({
                    "ID": emp[0], "Imię": emp[1], "Nazwisko": emp[2],
                    "Stanowisko": emp[3], "Wydział": emp[4], "Zmiana": emp[5],
                    "Status": emp[6], "Maszyna": emp[7]
                })
            
            df = pd.DataFrame(export_data)
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                title="Zapisz podsumowanie do Excel"
            )
            
            if file_path:
                with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                    # Arkusz z danymi
                    df.to_excel(writer, sheet_name='Pracownicy', index=False)
                    
                    # Arkusz z podsumowaniem
                    summary_data = self.calculate_statistics()
                    summary_df = pd.DataFrame([
                        ["Łączna liczba pracowników", summary_data['total']],
                        ["W Pracy", summary_data['working']],
                        ["Na urlopie", summary_data['vacation']],
                        ["Na L4", summary_data['l4']],
                        ["Wolne", summary_data['free']],
                        ["", ""],
                        ["Zmiana A", summary_data['shift_a']],
                        ["Zmiana B", summary_data['shift_b']],
                        ["Zmiana C", summary_data['shift_c']],
                        ["Zmiana D", summary_data['shift_d']],
                        ["", ""],
                        ["Wymagana obsada", summary_data['required_total']],
                        ["Aktualna obsada", summary_data['current_total']],
                        ["Brakuje", summary_data['shortage_total']],
                        ["Nadmiar", summary_data['overflow_total']],
                        ["Pokrycie", f"{summary_data['coverage_percent']}%"]
                    ])
                    summary_df.to_excel(writer, sheet_name='Podsumowanie', index=False, header=False)
                
                messagebox.showinfo("Sukces", f"Podsumowanie zostało wyeksportowane do:\n{file_path}")
                
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wyeksportować danych: {e}")

    def destroy(self):
        """Zamyka okno i zatrzymuje automatyczne odświeżanie"""
        # NOWOŚĆ: Usunięto stop_auto_refresh()
        super().destroy()
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, colorchooser
import datetime
from employee_management import EmployeeManagement

class SettingsWindow(tk.Toplevel):
    def __init__(self, master, emp_manager: EmployeeManagement):
        super().__init__(master)
        self.master = master
        self.emp_manager = emp_manager
        self.title("Ustawienia Systemu (Tylko dla Admina)")
        self.state('zoomed')
        self.transient(master)
        self.grab_set()

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.create_general_settings_tab()
        self.create_shifts_tab()
        self.create_statuses_tab()
        self.create_user_management_tab()
        self.create_required_staff_tab()
        self.create_overflow_policy_tab()  # NOWA ZAKŁADKA
        
        self.center_window()
        self.refresh_all_lists()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')

    def create_general_settings_tab(self):
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="Ogólne")
        
        self.list_configs = {
            'Wydziały': {'key': 'wydzialy', 'listbox': None, 'entry': None},
            'Stanowiska': {'key': 'stanowiska', 'listbox': None, 'entry': None},
            'Maszyny/Urządzenia': {'key': 'maszyny', 'listbox': None, 'entry': None}
        }

        row_start = 0
        for title, config in self.list_configs.items():
            ttk.Label(frame, text=f"--- {title} ---", font=('Arial', 10, 'bold')).grid(row=row_start, column=0, columnspan=2, sticky="w", pady=(10, 5))
            
            config['listbox'] = tk.Listbox(frame, height=6, width=50)
            config['listbox'].grid(row=row_start + 1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
            config['listbox'].bind('<Double-1>', lambda event, key=config['key']: self.edit_general_item(key, config['listbox']))
            
            config['entry'] = tk.Entry(frame, width=40, font=('Arial', 10))
            config['entry'].grid(row=row_start + 2, column=0, padx=5, pady=5, sticky="ew")

            btn_frame = ttk.Frame(frame)
            btn_frame.grid(row=row_start + 2, column=1, padx=5, pady=5, sticky="w")
            
            ttk.Button(btn_frame, text="Dodaj", 
                      command=lambda key=config['key'], lb=config['listbox'], entry=config['entry']: self.add_general_item(key, lb, entry)).pack(side='left', padx=2)
            ttk.Button(btn_frame, text="Usuń", 
                      command=lambda key=config['key'], lb=config['listbox']: self.delete_general_item(key, lb)).pack(side='left', padx=2)
            ttk.Button(btn_frame, text="Edytuj", 
                      command=lambda key=config['key'], lb=config['listbox']: self.edit_general_item(key, lb)).pack(side='left', padx=2)
            
            row_start += 4

        ttk.Button(frame, text="Wyczyść Listę Pracowników", command=self.clear_all_employees,
                  style='Accent.TButton').grid(row=row_start + 1, column=0, columnspan=2, pady=20)
        
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

    def create_shifts_tab(self):
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="Zmiany")
        
        # Nagłówek
        ttk.Label(frame, text="Konfiguracja Zmian - System 4 Zmianowy", 
                 font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        # Ramka dla listy zmian
        list_frame = ttk.LabelFrame(frame, text="Lista Zmian", padding="10")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.shifts_tree = ttk.Treeview(list_frame, columns=("Zmiana", "Start", "Koniec"), show="headings", height=8)
        self.shifts_tree.heading("#1", text="Zmiana")
        self.shifts_tree.heading("#2", text="Godzina rozpoczęcia")
        self.shifts_tree.heading("#3", text="Godzina zakończenia")
        self.shifts_tree.column("#1", width=200, stretch=tk.NO)
        self.shifts_tree.column("#2", width=150, stretch=tk.NO)
        self.shifts_tree.column("#3", width=150, stretch=tk.NO)
        
        v_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.shifts_tree.yview)
        self.shifts_tree.configure(yscrollcommand=v_scroll.set)
        
        self.shifts_tree.pack(side='left', fill='both', expand=True)
        v_scroll.pack(side='right', fill='y')
        
        # Ramka formularza
        form_frame = ttk.LabelFrame(frame, text="Dodaj/Edytuj Zmianę", padding="10")
        form_frame.pack(fill='x', padx=5, pady=10)
        
        # Nazwa zmiany
        ttk.Label(form_frame, text="Nazwa zmiany:", font=('Arial', 10)).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.shift_name_entry = ttk.Entry(form_frame, width=20, font=('Arial', 10))
        self.shift_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        # Godzina rozpoczęcia
        ttk.Label(form_frame, text="Godzina rozpoczęcia:", font=('Arial', 10)).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        start_frame = ttk.Frame(form_frame)
        start_frame.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        self.start_hour_var = tk.StringVar(value="06")
        self.start_minute_var = tk.StringVar(value="00")
        
        start_hour_combo = ttk.Combobox(start_frame, textvariable=self.start_hour_var, 
                                      values=[f"{i:02d}" for i in range(0, 24)], 
                                      width=3, state='readonly')
        start_hour_combo.pack(side='left')
        
        ttk.Label(start_frame, text=":").pack(side='left', padx=2)
        
        start_minute_combo = ttk.Combobox(start_frame, textvariable=self.start_minute_var,
                                        values=[f"{i:02d}" for i in range(0, 60, 30)],
                                        width=3, state='readonly')
        start_minute_combo.pack(side='left')
        
        # Godzina zakończenia
        ttk.Label(form_frame, text="Godzina zakończenia:", font=('Arial', 10)).grid(row=2, column=0, padx=5, pady=5, sticky='w')
        end_frame = ttk.Frame(form_frame)
        end_frame.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        
        self.end_hour_var = tk.StringVar(value="14")
        self.end_minute_var = tk.StringVar(value="00")
        
        end_hour_combo = ttk.Combobox(end_frame, textvariable=self.end_hour_var,
                                    values=[f"{i:02d}" for i in range(0, 24)],
                                    width=3, state='readonly')
        end_hour_combo.pack(side='left')
        
        ttk.Label(end_frame, text=":").pack(side='left', padx=2)
        
        end_minute_combo = ttk.Combobox(end_frame, textvariable=self.end_minute_var,
                                      values=[f"{i:02d}" for i in range(0, 60, 30)],
                                      width=3, state='readonly')
        end_minute_combo.pack(side='left')
        
        # Kolor - UKRYTY, ale nadal używany w systeme
        self.shift_color_entry = ttk.Entry(form_frame, width=10, font=('Arial', 10))
        self.shift_color_entry.insert(0, "#ADD8E6")
        self.shift_color_entry.grid_remove()
        
        # Przyciski szybkiego ustawienia zmian
        quick_btn_frame = ttk.LabelFrame(form_frame, text="Szybkie ustawienia zmian", padding="5")
        quick_btn_frame.grid(row=0, column=2, rowspan=2, padx=20, pady=5, sticky='n')
        
        ttk.Button(quick_btn_frame, text="Zmiana A (6:00-14:00)", 
                  command=lambda: self.set_quick_shift("A - Rano (6-14)", "06", "00", "14", "00", "#ADD8E6")).pack(fill='x', pady=2)
        ttk.Button(quick_btn_frame, text="Zmiana B (14:00-22:00)", 
                  command=lambda: self.set_quick_shift("B - Południe (14-22)", "14", "00", "22", "00", "#F08080")).pack(fill='x', pady=2)
        ttk.Button(quick_btn_frame, text="Zmiana C (22:00-6:00)", 
                  command=lambda: self.set_quick_shift("C - Noc (22-6)", "22", "00", "06", "00", "#20B2AA")).pack(fill='x', pady=2)
        ttk.Button(quick_btn_frame, text="Zmiana D (Wolne)", 
                  command=lambda: self.set_quick_shift("D - Wolne", "00", "00", "00", "00", "#90EE90")).pack(fill='x', pady=2)
        
        # Szybkie ustawienie godzin dla wybranej zmiany
        quick_time_frame = ttk.LabelFrame(form_frame, text="Szybkie ustawienie godzin", padding="5")
        quick_time_frame.grid(row=2, column=2, rowspan=2, padx=20, pady=5, sticky='n')

        ttk.Label(quick_time_frame, text="Dla zaznaczonej zmiany:").pack(pady=2)

        time_buttons_frame = ttk.Frame(quick_time_frame)
        time_buttons_frame.pack(fill='x', pady=5)

        ttk.Button(time_buttons_frame, text="6:00-14:00", 
                  command=lambda: self.set_quick_time("06", "00", "14", "00")).pack(fill='x', pady=1)
        ttk.Button(time_buttons_frame, text="14:00-22:00", 
                  command=lambda: self.set_quick_time("14", "00", "22", "00")).pack(fill='x', pady=1)
        ttk.Button(time_buttons_frame, text="22:00-6:00", 
                  command=lambda: self.set_quick_time("22", "00", "06", "00")).pack(fill='x', pady=1)
        ttk.Button(time_buttons_frame, text="Wolne (0:00-0:00)", 
                  command=lambda: self.set_quick_time("00", "00", "00", "00")).pack(fill='x', pady=1)
        
        # Przyciski akcji
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Dodaj/Zapisz Zmianę", 
                  command=self.add_edit_shift, style='Accent.TButton').pack(side='left', padx=5)
        ttk.Button(button_frame, text="Usuń Wybraną Zmianę", 
                  command=self.delete_shift).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Wyczyść Formularz", 
                  command=self.clear_shift_form).pack(side='left', padx=5)
        
        form_frame.columnconfigure(1, weight=1)
        self.shifts_tree.bind('<<TreeviewSelect>>', self.load_shift_data_to_entries)

    def create_overflow_policy_tab(self):
        """NOWA ZAKŁADKA: Ustawienia polityki przekroczeń"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="🚨 Polityka Obsady")
        
        # Nagłówek
        ttk.Label(frame, text="Ustawienia Zarządzania Przekroczeniami Obsady", 
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Główne ustawienia
        settings_frame = ttk.LabelFrame(frame, text="Polityka Przekroczeń Obsady", padding="15")
        settings_frame.pack(fill='x', padx=10, pady=10)
        
        # Wybór polityki
        ttk.Label(settings_frame, text="Reakcja na przekroczenie obsady:", 
                 font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky='w', pady=10)
        
        self.policy_var = tk.StringVar(value=self.emp_manager.get_overflow_policy())
        
        # Opcja 1: Ostrzeżenie
        policy1_frame = ttk.Frame(settings_frame)
        policy1_frame.grid(row=1, column=0, sticky='w', pady=5)
        ttk.Radiobutton(policy1_frame, text="⚠️  POKAZUJ OSTRZEŻENIE", 
                       variable=self.policy_var, value="warning").pack(anchor='w')
        ttk.Label(policy1_frame, text="System pyta czy na pewno chcesz dodać pracownika przy przekroczeniu obsady",
                 font=('Arial', 9), foreground='gray').pack(anchor='w', padx=25)
        
        # Opcja 2: Automatyczna korekta
        policy2_frame = ttk.Frame(settings_frame)
        policy2_frame.grid(row=2, column=0, sticky='w', pady=5)
        ttk.Radiobutton(policy2_frame, text="🔄  AUTOMATYCZNA KOREKTA", 
                       variable=self.policy_var, value="auto_adjust").pack(anchor='w')
        ttk.Label(policy2_frame, text="System automatycznie przenosi nadmiarowych pracowników na inne zmiany",
                 font=('Arial', 9), foreground='gray').pack(anchor='w', padx=25)
        
        # Opcja 3: Blokada
        policy3_frame = ttk.Frame(settings_frame)
        policy3_frame.grid(row=3, column=0, sticky='w', pady=5)
        ttk.Radiobutton(policy3_frame, text="❌  BLOKADA DODAWANIA", 
                       variable=self.policy_var, value="block").pack(anchor='w')
        ttk.Label(policy3_frame, text="System nie pozwala na dodanie pracownika przy przekroczeniu obsady",
                 font=('Arial', 9), foreground='gray').pack(anchor='w', padx=25)
        
        # Przycisk zapisu
        ttk.Button(settings_frame, text="💾 Zapisz Ustawienia", 
                  command=self.save_overflow_policy, style='Accent.TButton').grid(row=4, column=0, pady=20)
        
        # Sekcja informacyjna
        info_frame = ttk.LabelFrame(frame, text="Informacje o Aktualnej Situacji", padding="15")
        info_frame.pack(fill='x', padx=10, pady=10)
        
        # Przycisk odświeżania
        ttk.Button(info_frame, text="🔄 Sprawdź Aktualne Przekroczenia", 
                  command=self.show_current_overflows).pack(pady=5)
        
        # Lista przekroczeń
        self.overflow_tree = ttk.Treeview(info_frame, columns=("Wydział", "Zmiana", "Wymagana", "Aktualna", "Nadmiar"), 
                                         show="headings", height=6)
        self.overflow_tree.heading("#1", text="Wydział")
        self.overflow_tree.heading("#2", text="Zmiana")
        self.overflow_tree.heading("#3", text="Wymagana")
        self.overflow_tree.heading("#4", text="Aktualna")
        self.overflow_tree.heading("#5", text="Nadmiar")
        
        self.overflow_tree.column("#1", width=150)
        self.overflow_tree.column("#2", width=150)
        self.overflow_tree.column("#3", width=80)
        self.overflow_tree.column("#4", width=80)
        self.overflow_tree.column("#5", width=80)
        
        self.overflow_tree.pack(fill='x', pady=10)
        
        # Przyciski akcji dla przekroczeń
        action_frame = ttk.Frame(info_frame)
        action_frame.pack(fill='x', pady=5)
        
        ttk.Button(action_frame, text="🔧 Automatycznie Popraw Przekroczenia", 
                  command=self.auto_fix_overflows).pack(side='left', padx=5)
        ttk.Button(action_frame, text="📊 Pokaż Szczegóły", 
                  command=self.show_overflow_details).pack(side='left', padx=5)

    def save_overflow_policy(self):
        """Zapisuje ustawienia polityki przekroczeń"""
        policy = self.policy_var.get()
        self.emp_manager.save_overflow_policy(policy)
        messagebox.showinfo("Sukces", f"Polityka przekroczeń została ustawiona na: {policy}")
        
    def show_current_overflows(self):
        """Pokazuje aktualne przekroczenia obsady"""
        for item in self.overflow_tree.get_children():
            self.overflow_tree.delete(item)
            
        overflows = self.emp_manager.get_overflow_alerts()
        
        if not overflows:
            self.overflow_tree.insert("", tk.END, values=("Brak przekroczeń", "", "", "", ""))
            return
            
        for overflow in overflows:
            self.overflow_tree.insert("", tk.END, values=(
                overflow['wydzial'],
                overflow['zmiana'],
                overflow['wymagane'],
                overflow['aktualne'],
                overflow['nadmiar']
            ))

    def auto_fix_overflows(self):
        """Automatycznie poprawia przekroczenia obsady"""
        overflows = self.emp_manager.get_overflow_alerts()
        fixed_count = 0
        
        for overflow in overflows:
            moved = self.emp_manager.auto_adjust_overflow(overflow['wydzial'], overflow['zmiana'])
            if moved:
                fixed_count += len(moved)
                
        if fixed_count > 0:
            messagebox.showinfo("Sukces", f"Automatycznie przeniesiono {fixed_count} pracowników")
            self.show_current_overflows()
            if hasattr(self.master, 'refresh_employee_list'):
                self.master.refresh_employee_list()
        else:
            messagebox.showinfo("Info", "Brak przekroczeń do poprawienia")

    def show_overflow_details(self):
        """Pokazuje szczegóły przekroczeń"""
        overflows = self.emp_manager.get_overflow_alerts()
        
        if not overflows:
            messagebox.showinfo("Przekroczenia", "Brak aktualnych przekroczeń obsady")
            return
            
        details = "🚨 AKTUALNE PRZEKROCZENIA OBSADY:\n\n"
        for overflow in overflows:
            details += f"• {overflow['wydzial']} - {overflow['zmiana']}: {overflow['aktualne']}/{overflow['wymagane']} (+{overflow['nadmiar']})\n"
            
        messagebox.showinfo("Szczegóły Przekroczeń", details)

    # ... (reszta metod pozostaje bez zmian - set_quick_shift, set_quick_time, refresh_shifts_list, itd.)
    # Pozostałe metody są identyczne jak w oryginalnym pliku, więc je pomijam dla czytelności

    def set_quick_shift(self, name, start_hour, start_minute, end_hour, end_minute, color):
        self.shift_name_entry.delete(0, tk.END)
        self.shift_name_entry.insert(0, name)
        self.start_hour_var.set(start_hour)
        self.start_minute_var.set(start_minute)
        self.end_hour_var.set(end_hour)
        self.end_minute_var.set(end_minute)
        self.shift_color_entry.delete(0, tk.END)
        self.shift_color_entry.insert(0, color)

    def set_quick_time(self, start_hour, start_minute, end_hour, end_minute):
        self.start_hour_var.set(start_hour)
        self.start_minute_var.set(start_minute)
        self.end_hour_var.set(end_hour)
        self.end_minute_var.set(end_minute)
        
        current_name = self.shift_name_entry.get()
        if " - " in current_name:
            base_name = current_name.split(" - ")[0]
            start_time = f"{start_hour}:{start_minute}"
            end_time = f"{end_hour}:{end_minute}"
            
            time_ranges = {
                "06:00-14:00": "Rano (6-14)",
                "14:00-22:00": "Południe (14-22)", 
                "22:00-06:00": "Noc (22-6)",
                "00:00-00:00": "Wolne"
            }
            
            time_key = f"{start_time}-{end_time}"
            time_suffix = time_ranges.get(time_key, f"({start_time}-{end_time})")
            
            new_name = f"{base_name} - {time_suffix}"
            self.shift_name_entry.delete(0, tk.END)
            self.shift_name_entry.insert(0, new_name)

    def refresh_shifts_list(self):
        for item in self.shifts_tree.get_children():
            self.shifts_tree.delete(item)
            
        shifts = self.emp_manager.get_shifts_config()
        seen = set()
        unique_shifts = []
        for name, start, end, color in shifts:
            if name not in seen:
                seen.add(name)
                unique_shifts.append((name, start, end, color))
        
        for name, start, end, color in unique_shifts:
            self.shifts_tree.insert("", tk.END, values=(name, start, end))

    def load_shift_data_to_entries(self, event):
        selected_item = self.shifts_tree.selection()
        if selected_item:
            item = self.shifts_tree.item(selected_item[0])
            name, start, end = item['values']
            
            start_hour, start_minute = start.split(':')
            end_hour, end_minute = end.split(':')
            
            self.shift_name_entry.delete(0, tk.END)
            self.shift_name_entry.insert(0, name)
            self.start_hour_var.set(start_hour)
            self.start_minute_var.set(start_minute)
            self.end_hour_var.set(end_hour)
            self.end_minute_var.set(end_minute)
            
            color = self.emp_manager.get_shift_color(name)
            self.shift_color_entry.delete(0, tk.END)
            self.shift_color_entry.insert(0, color)

    def add_edit_shift(self):
        name = self.shift_name_entry.get().strip()
        start_time = f"{self.start_hour_var.get()}:{self.start_minute_var.get()}"
        end_time = f"{self.end_hour_var.get()}:{self.end_minute_var.get()}"
        color = self.shift_color_entry.get().strip()
        
        if not all([name, color]):
            messagebox.showerror("Błąd", "Nazwa i kolor zmiany są wymagane.")
            return

        try:
            datetime.datetime.strptime(start_time, '%H:%M')
            datetime.datetime.strptime(end_time, '%H:%M')
        except ValueError:
            messagebox.showerror("Błąd", "Nieprawidłowy format czasu.")
            return

        selected_item = self.shifts_tree.selection()
        is_editing = bool(selected_item)
        
        data = {'name': name, 'start_time': start_time, 'end_time': end_time, 'color': color}
        
        if is_editing:
            old_name = self.shifts_tree.item(selected_item[0])['values'][0]
            
            if self.emp_manager.delete_setting('shifts', old_name):
                if self.emp_manager.add_setting('shifts', data):
                    messagebox.showinfo("Sukces", f"Zmiana '{name}' została zaktualizowana.")
                    self.refresh_shifts_list()
                    if hasattr(self.master, 'update_dynamic_filters'):
                        self.master.update_dynamic_filters()
                else:
                    self.emp_manager.add_setting('shifts', {'name': old_name, 'start_time': start_time, 'end_time': end_time, 'color': color})
                    messagebox.showerror("Błąd", "Nie udało się zaktualizować zmiany.")
            else:
                messagebox.showerror("Błąd", "Nie udało się zaktualizować zmiany.")
        else:
            existing_shifts = self.emp_manager.get_shifts_config()
            existing_names = [shift[0] for shift in existing_shifts]
            if name in existing_names:
                messagebox.showerror("Błąd", f"Zmiana o nazwie '{name}' już istnieje.")
                return
                
            if self.emp_manager.add_setting('shifts', data):
                messagebox.showinfo("Sukces", f"Zmiana '{name}' została dodana.")
                self.refresh_shifts_list()
                if hasattr(self.master, 'update_dynamic_filters'):
                    self.master.update_dynamic_filters()
            else:
                messagebox.showerror("Błąd", "Nie udało się dodać zmiany.")

    def delete_shift(self):
        selected_item = self.shifts_tree.selection()
        if selected_item:
            name = self.shifts_tree.item(selected_item[0])['values'][0]
            if messagebox.askyesno("Potwierdzenie", f"Czy na pewno usunąć zmianę '{name}'?"):
                if self.emp_manager.delete_setting('shifts', name):
                    self.refresh_shifts_list()
                    if hasattr(self.master, 'update_dynamic_filters'):
                        self.master.update_dynamic_filters()
                else:
                    messagebox.showerror("Błąd", "Nie udało się usunąć zmiany.")
        else:
            messagebox.showerror("Błąd", "Wybierz zmianę do usunięcia.")

    def clear_shift_form(self):
        self.shift_name_entry.delete(0, tk.END)
        self.start_hour_var.set("06")
        self.start_minute_var.set("00")
        self.end_hour_var.set("14")
        self.end_minute_var.set("00")
        self.shift_color_entry.delete(0, tk.END)
        self.shift_color_entry.insert(0, "#ADD8E6")
        for item in self.shifts_tree.selection():
            self.shifts_tree.selection_remove(item)

    def create_statuses_tab(self):
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="Statusy")
        
        self.statuses_tree = ttk.Treeview(frame, columns=("Kolor",), show="headings", height=8)
        self.statuses_tree.heading("#0", text="Nazwa Statusu")
        self.statuses_tree.heading("#1", text="Kolor")
        self.statuses_tree.column("#0", width=200, stretch=tk.NO)
        self.statuses_tree.column("#1", width=150, stretch=tk.NO)
        self.statuses_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        entry_frame = ttk.LabelFrame(frame, text="Dodaj/Edytuj Status", padding="10")
        entry_frame.pack(fill='x', padx=5, pady=10)
        
        ttk.Label(entry_frame, text="Nazwa Statusu:", font=('Arial', 10)).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.status_name_entry = ttk.Entry(entry_frame, width=20, font=('Arial', 10))
        self.status_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(entry_frame, text="Kolor:", font=('Arial', 10)).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        
        color_frame = ttk.Frame(entry_frame)
        color_frame.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        self.status_color_entry = ttk.Entry(color_frame, width=10, font=('Arial', 10))
        self.status_color_entry.grid(row=0, column=0, padx=(0, 5))
        self.status_color_entry.insert(0, "#3CB371")
        
        self.color_button = ttk.Button(color_frame, text="Wybierz kolor", 
                                      command=self.choose_status_color)
        self.color_button.grid(row=0, column=1, padx=5)
        
        self.color_preview = tk.Label(color_frame, text="   ", background="#3CB371", 
                                     relief='solid', borderwidth=1, width=4)
        self.color_preview.grid(row=0, column=2, padx=5)
        
        quick_btn_frame = ttk.LabelFrame(entry_frame, text="Szybkie ustawienia", padding="5")
        quick_btn_frame.grid(row=0, column=2, rowspan=2, padx=20, pady=5, sticky='n')
        
        ttk.Button(quick_btn_frame, text="W Pracy", 
                  command=lambda: self.set_quick_status("W Pracy", "#3CB371")).pack(fill='x', pady=2)
        ttk.Button(quick_btn_frame, text="Urlop", 
                  command=lambda: self.set_quick_status("Urlop", "#FFA500")).pack(fill='x', pady=2)
        ttk.Button(quick_btn_frame, text="L4", 
                  command=lambda: self.set_quick_status("L4", "#FF4500")).pack(fill='x', pady=2)
        ttk.Button(quick_btn_frame, text="Wolne", 
                  command=lambda: self.set_quick_status("Wolne", "#98FB98")).pack(fill='x', pady=2)
        
        button_frame = ttk.Frame(entry_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Dodaj/Zapisz Status", 
                  command=self.add_edit_status, style='Accent.TButton').pack(side='left', padx=5)
        ttk.Button(button_frame, text="Usuń Wybrany Status", 
                  command=self.delete_status).pack(side='left', padx=5)
        
        self.statuses_tree.bind('<<TreeviewSelect>>', self.load_status_data_to_entries)

    def choose_status_color(self):
        try:
            color_code = self.status_color_entry.get()
            color = colorchooser.askcolor(initialcolor=color_code, title="Wybierz kolor statusu")
            if color and color[1]:
                self.status_color_entry.delete(0, tk.END)
                self.status_color_entry.insert(0, color[1])
                self.color_preview.config(background=color[1])
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wybrać koloru: {e}")

    def set_quick_status(self, name, color):
        self.status_name_entry.delete(0, tk.END)
        self.status_name_entry.insert(0, name)
        self.status_color_entry.delete(0, tk.END)
        self.status_color_entry.insert(0, color)
        self.color_preview.config(background=color)

    def refresh_statuses_list(self):
        for item in self.statuses_tree.get_children():
            self.statuses_tree.delete(item)
            
        statuses = self.emp_manager.get_statuses_config()
        for name, color in statuses:
            self.statuses_tree.insert("", tk.END, text=name, values=(color,))

    def load_status_data_to_entries(self, event):
        selected_item = self.statuses_tree.selection()
        if selected_item:
            item = self.statuses_tree.item(selected_item[0])
            name = item['text']
            color = item['values'][0]
            
            self.status_name_entry.delete(0, tk.END)
            self.status_name_entry.insert(0, name)
            self.status_color_entry.delete(0, tk.END)
            self.status_color_entry.insert(0, color)
            self.color_preview.config(background=color)

    def add_edit_status(self):
        name = self.status_name_entry.get().strip()
        color = self.status_color_entry.get().strip()
        
        if not all([name, color]):
            messagebox.showerror("Błąd", "Nazwa i kolor statusu są wymagane.")
            return

        selected_item = self.statuses_tree.selection()
        is_editing = bool(selected_item)
        
        data = {'name': name, 'color': color}
        
        if is_editing:
            old_name = self.statuses_tree.item(selected_item[0])['text']
            
            if self.emp_manager.delete_setting('statuses', old_name):
                if self.emp_manager.add_setting('statuses', data):
                    messagebox.showinfo("Sukces", f"Status '{name}' został zaktualizowany.")
                    self.refresh_statuses_list()
                    if hasattr(self.master, 'update_dynamic_filters'):
                        self.master.update_dynamic_filters()
                else:
                    self.emp_manager.add_setting('statuses', {'name': old_name, 'color': color})
                    messagebox.showerror("Błąd", "Nie udało się zaktualizować statusu.")
            else:
                messagebox.showerror("Błąd", "Nie udało się zaktualizować statusu.")
        else:
            if self.emp_manager.add_setting('statuses', data):
                messagebox.showinfo("Sukces", f"Status '{name}' został dodany.")
                self.refresh_statuses_list()
                if hasattr(self.master, 'update_dynamic_filters'):
                    self.master.update_dynamic_filters()
            else:
                messagebox.showerror("Błąd", "Nie udało się dodać statusu.")

    def delete_status(self):
        selected_item = self.statuses_tree.selection()
        if selected_item:
            name = self.statuses_tree.item(selected_item[0])['text']
            if messagebox.askyesno("Potwierdzenie", f"Czy na pewno usunąć status '{name}'?"):
                if self.emp_manager.delete_setting('statuses', name):
                    self.refresh_statuses_list()
                    if hasattr(self.master, 'update_dynamic_filters'):
                        self.master.update_dynamic_filters()
                else:
                    messagebox.showerror("Błąd", "Nie udało się usunąć statusu.")
        else:
            messagebox.showerror("Błąd", "Wybierz status do usunięcia.")

    def create_user_management_tab(self):
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="Użytkownicy")
        
        self.users_tree = ttk.Treeview(frame, columns=("Rola",), show="headings", height=8)
        self.users_tree.heading("#0", text="Nazwa Użytkownika")
        self.users_tree.heading("#1", text="Rola")
        self.users_tree.column("#0", width=200, stretch=tk.NO)
        self.users_tree.column("#1", width=150, stretch=tk.NO)
        self.users_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        entry_frame = ttk.LabelFrame(frame, text="Dodaj/Edytuj Użytkownika", padding="10")
        entry_frame.pack(fill='x', padx=5, pady=10)
        
        ttk.Label(entry_frame, text="Użytkownik:", font=('Arial', 10)).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.user_name_entry = ttk.Entry(entry_frame, width=20, font=('Arial', 10))
        self.user_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(entry_frame, text="Hasło:", font=('Arial', 10)).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.user_password_entry = ttk.Entry(entry_frame, width=20, show="*", font=('Arial', 10))
        self.user_password_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(entry_frame, text="Rola:", font=('Arial', 10)).grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.user_role_var = tk.StringVar(value="operator")
        self.user_role_combo = ttk.Combobox(entry_frame, textvariable=self.user_role_var, 
                                          values=['admin', 'manager', 'operator'], 
                                          state='readonly', width=18, font=('Arial', 10))
        self.user_role_combo.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        
        button_frame = ttk.Frame(entry_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Dodaj/Zapisz Użytkownika", 
                  command=self.add_edit_user, style='Accent.TButton').pack(side='left', padx=5)
        ttk.Button(button_frame, text="Usuń Wybranego Użytkownika", 
                  command=self.delete_user).pack(side='left', padx=5)
        
        self.users_tree.bind('<<TreeviewSelect>>', self.load_user_data_to_entries)

    def refresh_users_list(self):
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
            
        users = self.emp_manager.db.fetch_all("SELECT username, role FROM users")
        for username, role in users:
            self.users_tree.insert("", tk.END, text=username, values=(role,))

    def load_user_data_to_entries(self, event):
        selected_item = self.users_tree.selection()
        if selected_item:
            item = self.users_tree.item(selected_item[0])
            username = item['text']
            role = item['values'][0]
            
            self.user_name_entry.delete(0, tk.END)
            self.user_name_entry.insert(0, username)
            self.user_role_var.set(role)
            self.user_password_entry.delete(0, tk.END)

    def add_edit_user(self):
        username = self.user_name_entry.get().strip()
        password = self.user_password_entry.get()
        role = self.user_role_var.get()
        
        if not all([username, password, role]):
            messagebox.showerror("Błąd", "Wszystkie pola użytkownika są wymagane.")
            return

        data = {'username': username, 'password': password, 'role': role}
        if self.emp_manager.add_setting('users', data):
            messagebox.showinfo("Sukces", f"Użytkownik '{username}' został zapisany/zaktualizowany.")
            self.refresh_users_list()
            self.user_name_entry.delete(0, tk.END)
            self.user_password_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Błąd", "Nie udało się zapisać użytkownika.")

    def delete_user(self):
        selected_item = self.users_tree.selection()
        if selected_item:
            username = self.users_tree.item(selected_item[0])['text']
            if username == 'admin':
                messagebox.showerror("Błąd", "Nie można usunąć głównego administratora.")
                return
                
            if messagebox.askyesno("Potwierdzenie", f"Czy na pewno usunąć użytkownika '{username}'?"):
                if self.emp_manager.delete_setting('users', username):
                    self.refresh_users_list()
                else:
                    messagebox.showerror("Błąd", "Nie udało się usunąć użytkownika.")
        else:
            messagebox.showerror("Błąd", "Wybierz użytkownika do usunięcia.")

    def create_required_staff_tab(self):
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="Wymagana Obsada")
        
        # NOWE: Filtry nad listą
        filter_frame = ttk.LabelFrame(frame, text="Filtry", padding="10")
        filter_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Wydział:", font=('Arial', 10)).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.filter_wydzial_var = tk.StringVar()
        self.filter_wydzial_combo = ttk.Combobox(filter_frame, textvariable=self.filter_wydzial_var, 
                                               values=[''] + self.emp_manager.get_setting('wydzialy'), 
                                               state='readonly', width=20, font=('Arial', 10))
        self.filter_wydzial_combo.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.filter_wydzial_combo.bind('<<ComboboxSelected>>', self.apply_required_staff_filter)
        
        ttk.Label(filter_frame, text="Zmiana:", font=('Arial', 10)).grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.filter_zmiana_var = tk.StringVar()
        self.filter_zmiana_combo = ttk.Combobox(filter_frame, textvariable=self.filter_zmiana_var, 
                                              values=[''] + [s[0] for s in self.emp_manager.get_shifts_config()], 
                                              state='readonly', width=20, font=('Arial', 10))
        self.filter_zmiana_combo.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        self.filter_zmiana_combo.bind('<<ComboboxSelected>>', self.apply_required_staff_filter)
        
        ttk.Button(filter_frame, text="Wyczyść Filtry", 
                  command=self.clear_required_staff_filters).grid(row=0, column=4, padx=5, pady=5)
        
        filter_frame.columnconfigure(1, weight=1)
        filter_frame.columnconfigure(3, weight=1)
        
        ttk.Label(frame, text="Ustaw wymaganą liczbę pracowników na Wydział i Zmianę", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        self.required_staff_tree = ttk.Treeview(frame, columns=("Wydział", "Zmiana", "Wymagana Liczba"), show="headings", height=8)
        self.required_staff_tree.heading("#1", text="Wydział")
        self.required_staff_tree.heading("#2", text="Zmiana")
        self.required_staff_tree.heading("#3", text="Wymagana Liczba")
        self.required_staff_tree.column("#1", width=200, stretch=tk.NO)
        self.required_staff_tree.column("#2", width=200, stretch=tk.NO)
        self.required_staff_tree.column("#3", width=150, stretch=tk.NO)
        self.required_staff_tree.pack(fill='both', expand=True, padx=5, pady=5)

        entry_frame = ttk.LabelFrame(frame, text="Ustaw Wymaganą Obsadę", padding="10")
        entry_frame.pack(fill='x', padx=5, pady=10)

        ttk.Label(entry_frame, text="Wydział:", font=('Arial', 10)).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.req_wydzial_var = tk.StringVar()
        self.req_wydzial_combo = ttk.Combobox(entry_frame, textvariable=self.req_wydzial_var, 
                                            values=self.emp_manager.get_setting('wydzialy'), 
                                            state='readonly', width=20, font=('Arial', 10))
        self.req_wydzial_combo.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(entry_frame, text="Zmiana:", font=('Arial', 10)).grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.req_zmiana_var = tk.StringVar()
        self.req_zmiana_combo = ttk.Combobox(entry_frame, textvariable=self.req_zmiana_var, 
                                           values=[s[0] for s in self.emp_manager.get_shifts_config()], 
                                           state='readonly', width=20, font=('Arial', 10))
        self.req_zmiana_combo.grid(row=0, column=3, padx=5, pady=5, sticky='w')

        ttk.Label(entry_frame, text="Wymagana Liczba:", font=('Arial', 10)).grid(row=0, column=4, padx=5, pady=5, sticky='w')
        self.req_count_entry = ttk.Entry(entry_frame, width=10, font=('Arial', 10))
        self.req_count_entry.grid(row=0, column=5, padx=5, pady=5, sticky='w')
        
        button_frame = ttk.Frame(entry_frame)
        button_frame.grid(row=1, column=0, columnspan=6, pady=10)
        
        ttk.Button(button_frame, text="Ustaw Wymaganą Obsadę", 
                  command=self.save_required_staff, style='Accent.TButton').pack(side='left', padx=5)
        ttk.Button(button_frame, text="Wyczyść Wszystkie", 
                  command=self.clear_all_required_staff).pack(side='left', padx=5)
        
        self.required_staff_tree.bind('<<TreeviewSelect>>', self.load_required_staff_to_entries)

    def apply_required_staff_filter(self, event=None):
        filter_wydzial = self.filter_wydzial_var.get()
        filter_zmiana = self.filter_zmiana_var.get()
        
        for item in self.required_staff_tree.get_children():
            self.required_staff_tree.delete(item)
            
        wydzialy = self.emp_manager.get_setting('wydzialy')
        shifts = [s[0] for s in self.emp_manager.get_shifts_config()]
        
        for wydzial in wydzialy:
            for shift in shifts:
                # Sprawdź czy pasuje do filtrów
                if filter_wydzial and wydzial != filter_wydzial:
                    continue
                if filter_zmiana and shift != filter_zmiana:
                    continue
                    
                count = self.emp_manager.get_required_staff_by_wydzial_shift(wydzial, shift)
                self.required_staff_tree.insert("", tk.END, values=(wydzial, shift, count))

    def clear_required_staff_filters(self):
        self.filter_wydzial_var.set('')
        self.filter_zmiana_var.set('')
        self.refresh_required_staff_list()

    def refresh_required_staff_list(self):
        for item in self.required_staff_tree.get_children():
            self.required_staff_tree.delete(item)
            
        wydzialy = self.emp_manager.get_setting('wydzialy')
        shifts = [s[0] for s in self.emp_manager.get_shifts_config()]
        
        for wydzial in wydzialy:
            for shift in shifts:
                count = self.emp_manager.get_required_staff_by_wydzial_shift(wydzial, shift)
                self.required_staff_tree.insert("", tk.END, values=(wydzial, shift, count))

    def load_required_staff_to_entries(self, event):
        selected_item = self.required_staff_tree.selection()
        if selected_item:
            item = self.required_staff_tree.item(selected_item[0])
            wydzial, zmiana, count = item['values']
            
            self.req_wydzial_var.set(wydzial)
            self.req_zmiana_var.set(zmiana)
            self.req_count_entry.delete(0, tk.END)
            self.req_count_entry.insert(0, count)

    def save_required_staff(self):
        wydzial = self.req_wydzial_var.get()
        zmiana = self.req_zmiana_var.get()
        count_str = self.req_count_entry.get().strip()
        
        try:
            count = int(count_str)
            if count < 0: raise ValueError
        except ValueError:
            messagebox.showerror("Błąd", "Wymagana liczba musi być nieujemną liczbą całkowitą.")
            return

        if not all([wydzial, zmiana]):
            messagebox.showerror("Błąd", "Wydział i Zmiana muszą być wybrane.")
            return
        
        self.emp_manager.save_required_staff(wydzial, zmiana, count)
        messagebox.showinfo("Sukces", f"Wymagana obsada dla {wydzial} na zmianie {zmiana} ustawiona na {count}.")
        self.refresh_required_staff_list()
        if hasattr(self.master, 'update_dashboard'):
            self.master.update_dashboard()

    def clear_all_required_staff(self):
        if messagebox.askyesno("Potwierdzenie", "Czy na pewno wyczyścić wszystkie ustawienia wymaganej obsady?"):
            wydzialy = self.emp_manager.get_setting('wydzialy')
            shifts = [s[0] for s in self.emp_manager.get_shifts_config()]
            
            for wydzial in wydzialy:
                for shift in shifts:
                    self.emp_manager.save_required_staff(wydzial, shift, 0)
            
            self.refresh_required_staff_list()
            messagebox.showinfo("Sukces", "Wszystkie ustawienia wymaganej obsady zostały wyczyszczone.")

    # Pozostałe metody dla general settings
    def refresh_general_list(self, key):
        config = [c for c in self.list_configs.values() if c['key'] == key][0]
        data = self.emp_manager.get_setting(key)
        
        config['listbox'].delete(0, tk.END)
        for item in data:
            config['listbox'].insert(tk.END, item)

    def add_general_item(self, key, listbox, entry):
        name = entry.get().strip()
        if name:
            data = self.emp_manager.get_setting(key)
            if name not in data:
                data.append(name)
                self.emp_manager.save_setting(key, data)
                self.refresh_general_list(key)
                entry.delete(0, tk.END)
                if hasattr(self.master, 'update_dynamic_filters'):
                    self.master.update_dynamic_filters()
            else:
                messagebox.showerror("Błąd", f"Wpis '{name}' już istnieje.")
        else:
            messagebox.showerror("Błąd", "Wpis nie może być pusty.")

    def delete_general_item(self, key, listbox):
        try:
            selection = listbox.curselection()
            if selection:
                name = listbox.get(selection[0])
                if messagebox.askyesno("Potwierdzenie", f"Czy na pewno usunąć '{name}'?"):
                    self.emp_manager.delete_setting(key, name)
                    self.refresh_general_list(key)
                    if hasattr(self.master, 'update_dynamic_filters'):
                        self.master.update_dynamic_filters()
        except Exception as e:
            messagebox.showerror("Błąd", f"Wybierz element do usunięcia. {e}")
            
    def edit_general_item(self, key, listbox):
        selection = listbox.curselection()
        if selection:
            old_name = listbox.get(selection[0])
            new_name = simpledialog.askstring("Edycja", f"Edytuj {key[:-1]} '{old_name}':", initialvalue=old_name)
            if new_name and new_name != old_name:
                data = self.emp_manager.get_setting(key)
                if new_name not in data:
                    data.remove(old_name)
                    data.append(new_name)
                    self.emp_manager.save_setting(key, data)
                    self.refresh_general_list(key)
                    if hasattr(self.master, 'update_dynamic_filters'):
                        self.master.update_dynamic_filters()
                else:
                    messagebox.showerror("Błąd", f"Wpis '{new_name}' już istnieje.")

    def clear_all_employees(self):
        if messagebox.askyesno("Potwierdzenie", "Czy NA PEWNO chcesz usunąć WSZYSTKICH pracowników z bazy danych? Tej operacji nie można cofnąć!"):
            try:
                self.emp_manager.db.execute_query("DELETE FROM employees")
                self.emp_manager.log_history("Czyszczenie Bazy", "Usunięto wszystkich pracowników z bazy danych.")
                messagebox.showinfo("Sukces", "Wszyscy pracownicy zostali usunięci.")
                if hasattr(self.master, 'refresh_employee_list'):
                    self.master.refresh_employee_list()
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie udało się usunąć pracowników: {e}")

    def refresh_all_lists(self):
        for key in self.list_configs:
            self.refresh_general_list(self.list_configs[key]['key'])
        self.refresh_shifts_list()
        self.refresh_statuses_list()
        self.refresh_users_list()
        self.refresh_required_staff_list()
        self.req_wydzial_combo['values'] = self.emp_manager.get_setting('wydzialy')
        self.req_zmiana_combo['values'] = [s[0] for s in self.emp_manager.get_shifts_config()]
        # Aktualizuj też filtry
        self.filter_wydzial_combo['values'] = [''] + self.emp_manager.get_setting('wydzialy')
        self.filter_zmiana_combo['values'] = [''] + [s[0] for s in self.emp_manager.get_shifts_config()]
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from employee_management import EmployeeManagement
from calendar_widget import CalendarWidget

class VacationDialog(tk.Toplevel):
    def __init__(self, master, emp_manager: EmployeeManagement, emp_id, emp_name):
        super().__init__(master)
        self.master = master
        self.emp_manager = emp_manager
        self.emp_id = emp_id
        self.emp_name = emp_name
        
        self.title(f"Planowanie urlopu - {emp_name}")
        self.geometry("500x600")  # ZWIĘKSZONE WYSOKOŚĆ
        self.minsize(500, 600)   # MINIMALNY ROZMIAR
        self.transient(master)
        self.grab_set()
        self.resizable(True, True)  # POZWÓL NA ZMIANĘ ROZMIARU
        
        self.create_widgets()
        self.center_window()

    def create_widgets(self):
        # GŁÓWNY CONTENER Z SCROLLBAREMM
        main_container = ttk.Frame(self)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # CANVAS I SCROLLBAR
        self.canvas = tk.Canvas(main_container)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind scrollowania
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        
        # Nagłówek
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.pack(fill='x', pady=(0, 20))
        tk.Label(header_frame, text="🏖️ Planowanie urlopu", font=('Arial', 16, 'bold')).pack()
        tk.Label(header_frame, text=f"Pracownik: {self.emp_name}", font=('Arial', 12)).pack()
        
        # Ramka z formularzem
        form_frame = ttk.LabelFrame(self.scrollable_frame, text="Dane urlopu", padding="20")
        form_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Data rozpoczęcia
        start_frame = ttk.Frame(form_frame)
        start_frame.pack(fill='x', pady=15)
        tk.Label(start_frame, text="Data rozpoczęcia:", width=15, anchor='w', 
                font=('Arial', 11)).pack(side='left')
        
        start_subframe = ttk.Frame(start_frame)
        start_subframe.pack(side='left', padx=5)
        
        self.start_date = tk.Entry(start_subframe, width=12, font=('Arial', 10))
        self.start_date.pack(side='left')
        self.start_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        ttk.Button(start_subframe, text="📅 Kalendarz", width=10,
                  command=lambda: self.pick_date(self.start_date)).pack(side='left', padx=5)
        
        # Data zakończenia
        end_frame = ttk.Frame(form_frame)
        end_frame.pack(fill='x', pady=15)
        tk.Label(end_frame, text="Data zakończenia:", width=15, anchor='w', 
                font=('Arial', 11)).pack(side='left')
        
        end_subframe = ttk.Frame(end_frame)
        end_subframe.pack(side='left', padx=5)
        
        self.end_date = tk.Entry(end_subframe, width=12, font=('Arial', 10))
        self.end_date.pack(side='left')
        self.end_date.insert(0, (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"))
        
        ttk.Button(end_subframe, text="📅 Kalendarz", width=10,
                  command=lambda: self.pick_date(self.end_date)).pack(side='left', padx=5)
        
        # Typ urlopu
        type_frame = ttk.Frame(form_frame)
        type_frame.pack(fill='x', pady=15)
        tk.Label(type_frame, text="Typ urlopu:", width=15, anchor='w', 
                font=('Arial', 11)).pack(side='left')
        self.vacation_type = ttk.Combobox(type_frame, 
                                        values=["Wypoczynkowy", "Okolicznościowy", "Ojcostwo", "Macierzyński", "Bezpłatny"],
                                        state='readonly', width=20, font=('Arial', 10))
        self.vacation_type.pack(side='left', padx=5)
        self.vacation_type.set("Wypoczynkowy")
        
        # Informacje o urlopie
        info_frame = ttk.LabelFrame(self.scrollable_frame, text="Podsumowanie urlopu", padding="15")
        info_frame.pack(fill='x', pady=(0, 20))
        
        self.days_label = tk.Label(info_frame, text="Liczba dni roboczych: 0", 
                                 font=('Arial', 11, 'bold'))
        self.days_label.pack(anchor='w', pady=8)
        
        self.return_label = tk.Label(info_frame, text="Data powrotu: -", 
                                   font=('Arial', 11))
        self.return_label.pack(anchor='w', pady=8)
        
        # Dodatkowa informacja
        info_note = tk.Label(info_frame, 
                           text="Uwaga: Liczone są tylko dni robocze (poniedziałek-piątek)", 
                           font=('Arial', 9), foreground='gray')
        info_note.pack(anchor='w', pady=5)
        
        # PRZYCISKI NA STAŁE NA DOLE
        btn_frame = ttk.Frame(self.scrollable_frame)
        btn_frame.pack(fill='x', pady=(20, 10))
        
        ttk.Button(btn_frame, text="🔄 Oblicz", command=self.calculate_vacation, 
                  width=12).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="💾 Zapisz urlop", command=self.save_vacation, 
                  style='Accent.TButton', width=12).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="❌ Anuluj", command=self.destroy, 
                  width=12).pack(side='left', padx=5)
        
        # Oblicz początkową wartość
        self.calculate_vacation()
        
        # Aktualizacja rozmiaru canvas
        self.after(100, self._update_scrollregion)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _update_scrollregion(self):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def pick_date(self, entry_field):
        current_date = entry_field.get()
        try:
            selected_date = datetime.strptime(current_date, "%Y-%m-%d") if current_date else datetime.now()
        except ValueError:
            selected_date = datetime.now()
        
        calendar_dialog = CalendarWidget(self, selected_date)
        self.wait_window(calendar_dialog)
        
        if calendar_dialog.result:
            entry_field.delete(0, tk.END)
            entry_field.insert(0, calendar_dialog.result)
            self.calculate_vacation()

    def calculate_vacation(self):
        try:
            start = datetime.strptime(self.start_date.get(), "%Y-%m-%d")
            end = datetime.strptime(self.end_date.get(), "%Y-%m-%d")
            
            if end < start:
                messagebox.showerror("Błąd", "Data zakończenia nie może być wcześniejsza niż rozpoczęcia")
                return
            
            total_days = self.calculate_working_days(start, end)
            return_date = end + timedelta(days=1)
            
            self.days_label.config(text=f"Liczba dni roboczych: {total_days}")
            self.return_label.config(text=f"Data powrotu: {return_date.strftime('%Y-%m-%d (%A)')}")
            
        except ValueError:
            if self.start_date.get() and self.end_date.get():
                messagebox.showerror("Błąd", "Nieprawidłowy format daty. Użyj RRRR-MM-DD")

    def calculate_working_days(self, start, end):
        days = 0
        current = start
        while current <= end:
            if current.weekday() < 5:
                days += 1
            current += timedelta(days=1)
        return days

    def save_vacation(self):
        try:
            start = datetime.strptime(self.start_date.get(), "%Y-%m-%d")
            end = datetime.strptime(self.end_date.get(), "%Y-%m-%d")
            
            if end < start:
                messagebox.showerror("Błąd", "Data zakończenia nie może być wcześniejsza niż rozpoczęcia")
                return
                
            total_days = self.calculate_working_days(start, end)
            vacation_type = self.vacation_type.get()
            
            # Zapisz do bazy danych
            self.emp_manager.db.execute_query("""
                INSERT INTO vacations (employee_id, start_date, end_date, total_days, vacation_type)
                VALUES (?, ?, ?, ?, ?)
            """, (self.emp_id, start.date(), end.date(), total_days, vacation_type))
            
            # Zmień status pracownika na "Urlop"
            self.emp_manager.update_employee_status(self.emp_id, "Urlop")
            
            messagebox.showinfo("Sukces", 
                              f"Urlop zaplanowany pomyślnie!\n\n"
                              f"Typ: {vacation_type}\n"
                              f"Okres: {total_days} dni roboczych\n"
                              f"Powrót: {(end + timedelta(days=1)).strftime('%Y-%m-%d')}")
            
            self.master.refresh_employee_list()
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się zapisać urlopu: {e}")

    def center_window(self):
        self.update_idletasks()
        width = 500
        height = 600
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
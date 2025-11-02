import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import calendar

class CalendarWidget(tk.Toplevel):
    def __init__(self, master, selected_date=None):
        super().__init__(master)
        self.title("Wybierz datę")
        self.geometry("300x300")
        self.transient(master)
        self.grab_set()
        self.resizable(False, False)
        
        self.selected_date = selected_date or datetime.now()
        self.result = None
        
        self.create_widgets()
        self.center_window()

    def create_widgets(self):
        # Nagłówek z miesiącem i rokiem
        header_frame = ttk.Frame(self)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        self.prev_btn = ttk.Button(header_frame, text="◀", width=3, command=self.prev_month)
        self.prev_btn.pack(side='left')
        
        self.month_label = tk.Label(header_frame, text="", font=('Arial', 12, 'bold'))
        self.month_label.pack(side='left', expand=True)
        
        self.next_btn = ttk.Button(header_frame, text="▶", width=3, command=self.next_month)
        self.next_btn.pack(side='right')
        
        # Dni tygodnia
        days_frame = ttk.Frame(self)
        days_frame.pack(fill='x', padx=10)
        
        days = ["Pn", "Wt", "Śr", "Cz", "Pt", "So", "Nd"]
        for day in days:
            label = tk.Label(days_frame, text=day, font=('Arial', 9, 'bold'), width=4)
            label.pack(side='left')
        
        # Kalendarz
        self.calendar_frame = ttk.Frame(self)
        self.calendar_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Przyciski
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Dzisiaj", command=self.set_today).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Anuluj", command=self.cancel).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="OK", command=self.confirm, style='Accent.TButton').pack(side='right', padx=5)
        
        self.update_calendar()

    def update_calendar(self):
        # Czyść poprzednie przyciski
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        
        year = self.selected_date.year
        month = self.selected_date.month
        
        # Aktualizuj nagłówek
        month_names = ["Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec",
                      "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień"]
        self.month_label.config(text=f"{month_names[month-1]} {year}")
        
        # Twórz kalendarz
        cal = calendar.monthcalendar(year, month)
        today = datetime.now().date()
        
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day == 0:
                    # Puste miejsce
                    label = tk.Label(self.calendar_frame, text="", width=4)
                    label.grid(row=week_num, column=day_num, padx=1, pady=1)
                else:
                    date_str = f"{year}-{month:02d}-{day:02d}"
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                    
                    btn = tk.Button(self.calendar_frame, text=str(day), width=4,
                                  command=lambda d=date_str: self.select_date(d))
                    
                    # Podświetl dzisiejszą datę
                    if date_obj == today:
                        btn.config(bg='#e6f3ff', relief='solid')
                    
                    # Podświetl wybraną datę
                    if date_obj == self.selected_date.date():
                        btn.config(bg='#4CAF50', fg='white')
                    
                    btn.grid(row=week_num, column=day_num, padx=1, pady=1)

    def select_date(self, date_str):
        self.selected_date = datetime.strptime(date_str, "%Y-%m-%d")
        self.update_calendar()

    def prev_month(self):
        self.selected_date = self.selected_date.replace(day=1) - timedelta(days=1)
        self.selected_date = self.selected_date.replace(day=1)
        self.update_calendar()

    def next_month(self):
        next_month = self.selected_date.replace(day=28) + timedelta(days=4)
        self.selected_date = next_month.replace(day=1)
        self.update_calendar()

    def set_today(self):
        self.selected_date = datetime.now()
        self.update_calendar()

    def confirm(self):
        self.result = self.selected_date.strftime("%Y-%m-%d")
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')
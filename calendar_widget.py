
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import calendar

class CalendarWidget(tk.Toplevel):
    """
    Popup calendar picker.
    API compatible with existing usage:
      - constructor: CalendarWidget(parent, selected_date: datetime)
      - sets self.result to "YYYY-MM-DD" or None
    Visual:
      - 7 equal-width columns, weekday headers, uniform day buttons
      - Prev/Next month navigation
    """
    WEEKDAYS = ["Pn", "Wt", "Śr", "Cz", "Pt", "So", "Nd"]

    def __init__(self, master, selected_date=None):
        super().__init__(master)
        self.title("Wybierz datę")
        self.resizable(False, False)
        self.result = None
        self.selected = selected_date or datetime.now()

        # Frame
        container = ttk.Frame(self, padding=10)
        container.grid(row=0, column=0, sticky="nsew")

        # Header with navigation
        header = ttk.Frame(container)
        header.grid(row=0, column=0, columnspan=7, pady=(0,6))
        ttk.Button(header, text="◀", width=3, command=self.prev_month).pack(side="left")
        self.title_var = tk.StringVar()
        ttk.Label(header, textvariable=self.title_var, width=20, anchor="center").pack(side="left", padx=8)
        ttk.Button(header, text="▶", width=3, command=self.next_month).pack(side="left")

        # Weekday headers
        for col, name in enumerate(self.WEEKDAYS):
            lbl = ttk.Label(container, text=name, anchor="center")
            lbl.grid(row=1, column=col, padx=2, pady=2, sticky="nsew")

        # Grid for days
        self.days_frame = ttk.Frame(container)
        self.days_frame.grid(row=2, column=0, columnspan=7, sticky="nsew")

        # Buttons: OK / Anuluj / Dzisiaj
        btns = ttk.Frame(container)
        btns.grid(row=3, column=0, columnspan=7, pady=(8,0))
        ttk.Button(btns, text="Dzisiaj", command=self.pick_today).pack(side="left", padx=4)
        ttk.Button(btns, text="OK", command=self.ok).pack(side="left", padx=4)
        ttk.Button(btns, text="Anuluj", command=self.cancel).pack(side="left", padx=4)

        # Uniform column weights
        for i in range(7):
            container.grid_columnconfigure(i, weight=1, uniform="col")
        container.grid_rowconfigure(2, weight=1)

        self.build_month(self.selected.year, self.selected.month)
        self.center_on_parent()

        # Grab/focus
        self.transient(master)
        self.grab_set()
        self.focus_set()

    def center_on_parent(self):
        self.update_idletasks()
        w, h = self.winfo_reqwidth(), self.winfo_reqheight()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w)//2
        y = (sh - h)//2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def prev_month(self):
        y, m = self.year, self.month
        m -= 1
        if m < 1:
            m = 12
            y -= 1
        self.build_month(y, m)

    def next_month(self):
        y, m = self.year, self.month
        m += 1
        if m > 12:
            m = 1
            y += 1
        self.build_month(y, m)

    def build_month(self, year, month):
        self.year, self.month = year, month
        # Clear previous buttons
        for w in self.days_frame.winfo_children():
            w.destroy()

        # Title
        months_pl = ["Styczeń","Luty","Marzec","Kwiecień","Maj","Czerwiec","Lipiec","Sierpień","Wrzesień","Październik","Listopad","Grudzień"]
        self.title_var.set(f"{months_pl[month-1]} {year}")

        # Calendar matrix: start on Monday
        cal = calendar.Calendar(firstweekday=0)  # Monday
        month_days = cal.monthdatescalendar(year, month)

        # Create uniform buttons
        btn_opts = dict(width=4)  # fixed width for uniform grid
        today = datetime.now().date()

        for r, week in enumerate(month_days):
            for c, day in enumerate(week):
                txt = str(day.day)
                state = "normal" if day.month == month else "disabled"
                b = ttk.Button(self.days_frame, text=txt, width=4, command=lambda d=day: self.select_date(d))
                if state == "disabled":
                    b.state(["disabled"])
                # Mark today
                if day == today:
                    b.configure(style="Today.TButton")
                b.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")
        # equalize
        for i in range(7):
            self.days_frame.grid_columnconfigure(i, weight=1, uniform="dcol")
        for i in range(len(month_days)):
            self.days_frame.grid_rowconfigure(i, weight=1, uniform="drow")

        # Styles
        try:
            style = ttk.Style(self)
            style.configure("Today.TButton")
        except Exception:
            pass

    def select_date(self, d):
        self.selected = datetime(d.year, d.month, d.day)
        self.result = self.selected.strftime("%Y-%m-%d")

    def pick_today(self):
        self.selected = datetime.now()
        self.result = self.selected.strftime("%Y-%m-%d")
        self.destroy()

    def ok(self):
        if not self.result:
            self.result = self.selected.strftime("%Y-%m-%d")
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()

import tkinter as tk
from tkinter import ttk
from employee_management import EmployeeManagement
import datetime

class HistoryWindow(tk.Toplevel):
    def __init__(self, master, emp_manager: EmployeeManagement):
        super().__init__(master)
        self.master = master
        self.emp_manager = emp_manager
        self.title("Historia Zmian i Raporty")
        self.geometry("1000x700")
        self.transient(master)
        self.grab_set()

        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill="both", expand=True)

        self.create_widgets()
        self.refresh_history()
        
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')

    def create_widgets(self):
        filter_frame = ttk.LabelFrame(self.main_frame, text="Filtrowanie", padding="5")
        filter_frame.pack(fill='x', pady=5)
        
        self.filters = {}
        
        filter_cols = ["Operator", "Akcja", "Wydział"]
        
        for i, col in enumerate(filter_cols):
            ttk.Label(filter_frame, text=f"{col}:").grid(row=0, column=i * 2, padx=5, pady=2, sticky='w')
            if col == "Wydział":
                wydzialy = [''] + self.emp_manager.get_setting('wydzialy')
                var = tk.StringVar(self)
                combo = ttk.Combobox(filter_frame, textvariable=var, values=wydzialy, state='readonly')
                combo.grid(row=0, column=i * 2 + 1, padx=5, pady=2, sticky='ew')
                combo.bind('<<ComboboxSelected>>', self.apply_filters)
                self.filters[col] = combo
            else:
                entry = ttk.Entry(filter_frame)
                entry.grid(row=0, column=i * 2 + 1, padx=5, pady=2, sticky='ew')
                entry.bind('<KeyRelease>', self.apply_filters)
                self.filters[col] = entry

        ttk.Button(filter_frame, text="Wyczyść Filtry", command=self.clear_filters).grid(row=0, column=6, padx=5, pady=2)
        ttk.Button(filter_frame, text="Odśwież", command=self.refresh_history).grid(row=0, column=7, padx=5, pady=2)
        
        for i in range(8):
            filter_frame.columnconfigure(i, weight=1)

        columns = ("Timestamp", "Operator", "Akcja", "Szczegóły")
        self.history_tree = ttk.Treeview(self.main_frame, columns=columns, show="headings")
        
        self.history_tree.heading("Timestamp", text="Data/Czas", anchor=tk.W)
        self.history_tree.heading("Operator", text="Operator", anchor=tk.W)
        self.history_tree.heading("Akcja", text="Akcja", anchor=tk.W)
        self.history_tree.heading("Szczegóły", text="Szczegóły", anchor=tk.W)
        
        self.history_tree.column("Timestamp", width=150, stretch=tk.NO)
        self.history_tree.column("Operator", width=120, stretch=tk.NO)
        self.history_tree.column("Akcja", width=150, stretch=tk.NO)
        self.history_tree.column("Szczegóły", width=500, stretch=tk.YES)
        
        v_scroll = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.history_tree.yview)
        h_scroll = ttk.Scrollbar(self.main_frame, orient="horizontal", command=self.history_tree.xview)
        self.history_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")
        self.history_tree.pack(fill="both", expand=True)
        
        self.history_tree.heading("Timestamp", text="Data/Czas", command=lambda: self.sort_column(self.history_tree, "Timestamp", False))
        
    def refresh_history(self):
        self.all_history_data = self.emp_manager.get_history()
        self.display_history(self.all_history_data)

    def display_history(self, data):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
            
        for item in data:
            # Poprawiona konwersja czasu - użyj lokalnego czasu
            timestamp = self.convert_timestamp(item[1])
            self.history_tree.insert("", tk.END, values=(timestamp, item[2], item[3], item[4]))
            
    def convert_timestamp(self, timestamp):
        """Konwertuje timestamp na lokalną strefę czasową"""
        try:
            # Jeśli timestamp jest w formacie string, parsuj do datetime
            if isinstance(timestamp, str):
                # Usuń mikrosekundy jeśli istnieją
                if '.' in timestamp:
                    timestamp = timestamp.split('.')[0]
                dt = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            else:
                dt = timestamp
                
            # Dodaj godzinę (naprawa różnicy czasu)
            dt = dt + datetime.timedelta(hours=1)
            
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            print(f"Błąd konwersji czasu: {e}")
            return timestamp
            
    def apply_filters(self, event=None):
        filtered_data = []
        filter_operator = self.filters["Operator"].get().lower()
        filter_action = self.filters["Akcja"].get().lower()
        filter_wydzial = self.filters["Wydział"].get()
        
        for item in self.all_history_data:
            timestamp, operator, action, details = str(item[1]), str(item[2]), str(item[3]), str(item[4])
            
            match_operator = filter_operator in operator.lower()
            match_action = filter_action in action.lower()
            match_wydzial = not filter_wydzial or filter_wydzial in details
            
            if match_operator and match_action and match_wydzial:
                filtered_data.append(item)
                
        self.display_history(filtered_data)
        
    def clear_filters(self):
        for widget in self.filters.values():
            if isinstance(widget, ttk.Combobox):
                widget.set('')
            else:
                widget.delete(0, tk.END)
        self.refresh_history()
        
    def sort_column(self, tree, col, reverse):
        l = [(tree.set(k, col), k) for k in tree.get_children('')]
        
        if col == "Timestamp":
            l.sort(key=lambda t: datetime.datetime.strptime(t[0], '%Y-%m-%d %H:%M:%S'), reverse=reverse)
        else:
            l.sort(reverse=reverse)
            
        for index, (val, k) in enumerate(l):
            tree.move(k, '', index)
            
        tree.heading(col, command=lambda: self.sort_column(tree, col, not reverse))
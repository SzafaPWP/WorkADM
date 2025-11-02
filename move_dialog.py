import tkinter as tk
from tkinter import ttk, messagebox
from employee_management import EmployeeManagement

class MoveDialog(tk.Toplevel):
    def __init__(self, master, emp_manager: EmployeeManagement, emp_id, emp_name):
        super().__init__(master)
        self.master = master
        self.emp_manager = emp_manager
        self.emp_id = emp_id
        self.emp_name = emp_name

        self.title(f"Przenieś Pracownika: {emp_name}")
        self.geometry("400x200")
        self.transient(master)
        self.grab_set()
        
        # Dynamiczne pobranie list
        self.wydzialy = self.emp_manager.get_setting('wydzialy')
        self.stanowiska = self.emp_manager.get_setting('stanowiska')
        self.shifts = [s[0] for s in self.emp_manager.get_shifts_config()]

        self.create_widgets()
        
        # Centrowanie okna
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')

    def create_widgets(self):
        tk.Label(self, text=f"Pracownik: {self.emp_name}").grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        
        tk.Label(self, text="Nowy Wydział:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.wydzial_var = tk.StringVar(self)
        self.combo_wydzial = ttk.Combobox(self, textvariable=self.wydzial_var, values=self.wydzialy, state='readonly')
        self.combo_wydzial.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        tk.Label(self, text="Nowa Zmiana:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.zmiana_var = tk.StringVar(self)
        self.combo_zmiana = ttk.Combobox(self, textvariable=self.zmiana_var, values=self.shifts, state='readonly')
        self.combo_zmiana.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        
        tk.Label(self, text="Nowe Stanowisko:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.stanowisko_var = tk.StringVar(self)
        self.combo_stanowisko = ttk.Combobox(self, textvariable=self.stanowisko_var, values=self.stanowiska, state='readonly')
        self.combo_stanowisko.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        
        tk.Button(self, text="Zapisz", command=self.save_move).grid(row=4, column=0, padx=10, pady=10)
        tk.Button(self, text="Anuluj", command=self.destroy).grid(row=4, column=1, padx=10, pady=10)

    def save_move(self):
        new_wydzial = self.wydzial_var.get()
        new_zmiana = self.zmiana_var.get()
        new_stanowisko = self.stanowisko_var.get()
        
        if not any([new_wydzial, new_zmiana, new_stanowisko]):
            messagebox.showwarning("Brak zmian", "Proszę wybrać przynajmniej jedną wartość do zmiany.")
            return

        if self.emp_manager.move_employee(self.emp_id, new_wydzial, new_zmiana, new_stanowisko):
            messagebox.showinfo("Sukces", f"Pracownik {self.emp_name} został przeniesiony.")
            self.master.refresh_employee_list()
            self.destroy()
        else:
            messagebox.showerror("Błąd", "Nie udało się przenieść pracownika.")
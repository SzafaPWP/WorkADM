import tkinter as tk
from tkinter import ttk, messagebox
from employee_management import EmployeeManagement

class StatusDialog(tk.Toplevel):
    def __init__(self, master, emp_manager: EmployeeManagement, emp_id, emp_name, current_status):
        super().__init__(master)
        self.master = master
        self.emp_manager = emp_manager
        self.emp_id = emp_id
        self.emp_name = emp_name
        self.current_status = current_status

        self.title(f"Zmień Status dla: {emp_name}")
        self.geometry("350x150")
        self.transient(master)
        self.grab_set()
        
        # Dynamiczne pobranie listy statusów
        self.statuses = [s[0] for s in self.emp_manager.get_statuses_config()]

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
        
        tk.Label(self, text="Nowy Status:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.status_var = tk.StringVar(self)
        self.status_var.set(self.current_status)
        self.combo_status = ttk.Combobox(self, textvariable=self.status_var, values=self.statuses, state='readonly')
        self.combo_status.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        tk.Button(self, text="Zapisz", command=self.save_status_change).grid(row=2, column=0, padx=10, pady=10)
        tk.Button(self, text="Anuluj", command=self.destroy).grid(row=2, column=1, padx=10, pady=10)

    def save_status_change(self):
        new_status = self.status_var.get()
        if new_status and self.emp_manager.update_employee_status(self.emp_id, new_status):
            messagebox.showinfo("Sukces", f"Status dla {self.emp_name} został zmieniony na {new_status}.")
            self.master.refresh_employee_list()
            self.destroy()
        else:
            messagebox.showerror("Błąd", "Nie udało się zmienić statusu.")
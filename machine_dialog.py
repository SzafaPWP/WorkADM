import tkinter as tk
from tkinter import ttk, messagebox
from employee_management import EmployeeManagement

class MachineDialog(tk.Toplevel):
    def __init__(self, master, emp_manager: EmployeeManagement, emp_id, emp_name, current_machine):
        super().__init__(master)
        self.master = master
        self.emp_manager = emp_manager
        self.emp_id = emp_id
        self.emp_name = emp_name
        self.current_machine = current_machine

        self.title(f"Zmień Maszynę dla: {emp_name}")
        self.geometry("350x150")
        self.transient(master)
        self.grab_set()
        
        # Dynamiczne pobranie listy maszyn
        self.maszyny = self.emp_manager.get_setting('maszyny')

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
        
        tk.Label(self, text="Nowa Maszyna:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.maszyna_var = tk.StringVar(self)
        self.maszyna_var.set(self.current_machine)
        self.combo_maszyna = ttk.Combobox(self, textvariable=self.maszyna_var, values=self.maszyny, state='readonly')
        self.combo_maszyna.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        tk.Button(self, text="Zapisz", command=self.save_machine_change).grid(row=2, column=0, padx=10, pady=10)
        tk.Button(self, text="Anuluj", command=self.destroy).grid(row=2, column=1, padx=10, pady=10)

    def save_machine_change(self):
        new_machine = self.maszyna_var.get()
        if new_machine and self.emp_manager.update_employee_machine(self.emp_id, new_machine):
            messagebox.showinfo("Sukces", f"Maszyna dla {self.emp_name} została zmieniona na {new_machine}.")
            self.master.refresh_employee_list()
            self.destroy()
        else:
            messagebox.showerror("Błąd", "Nie udało się zmienić maszyny.")
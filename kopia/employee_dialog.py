import tkinter as tk
from tkinter import ttk, messagebox

class EmployeeDialog(tk.Toplevel):
    def __init__(self, master, emp_manager, employee_data=None):
        super().__init__(master)
        self.master = master
        self.emp_manager = emp_manager
        self.employee_data = employee_data
        
        if employee_data:
            self.title("Edytuj Pracownika")
        else:
            self.title("Dodaj Nowego Pracownika")
            
        self.geometry("500x450")
        self.transient(master)
        self.grab_set()
        
        self.create_widgets()
        self.center_window()
        
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill="both", expand=True)
        
        # Imię
        ttk.Label(main_frame, text="Imię:*").grid(row=0, column=0, sticky="w", pady=5)
        self.imie_entry = ttk.Entry(main_frame, width=30)
        self.imie_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=(10, 0))
        
        # Nazwisko
        ttk.Label(main_frame, text="Nazwisko:*").grid(row=1, column=0, sticky="w", pady=5)
        self.nazwisko_entry = ttk.Entry(main_frame, width=30)
        self.nazwisko_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=(10, 0))
        
        # Stanowisko
        ttk.Label(main_frame, text="Stanowisko:").grid(row=2, column=0, sticky="w", pady=5)
        self.stanowisko_var = tk.StringVar()
        self.stanowisko_combo = ttk.Combobox(main_frame, textvariable=self.stanowisko_var,
                                           values=self.emp_manager.get_setting('stanowiska'),
                                           state="readonly")
        self.stanowisko_combo.grid(row=2, column=1, sticky="ew", pady=5, padx=(10, 0))
        
        # Wydział
        ttk.Label(main_frame, text="Wydział:").grid(row=3, column=0, sticky="w", pady=5)
        self.wydzial_var = tk.StringVar()
        self.wydzial_combo = ttk.Combobox(main_frame, textvariable=self.wydzial_var,
                                        values=self.emp_manager.get_setting('wydzialy'),
                                        state="readonly")
        self.wydzial_combo.grid(row=3, column=1, sticky="ew", pady=5, padx=(10, 0))
        
        # Zmiana
        ttk.Label(main_frame, text="Zmiana:").grid(row=4, column=0, sticky="w", pady=5)
        self.zmiana_var = tk.StringVar()
        self.zmiana_combo = ttk.Combobox(main_frame, textvariable=self.zmiana_var,
                                       values=[s[0] for s in self.emp_manager.get_shifts_config()],
                                       state="readonly")
        self.zmiana_combo.grid(row=4, column=1, sticky="ew", pady=5, padx=(10, 0))
        
        # Status
        ttk.Label(main_frame, text="Status:").grid(row=5, column=0, sticky="w", pady=5)
        self.status_var = tk.StringVar()
        self.status_combo = ttk.Combobox(main_frame, textvariable=self.status_var,
                                       values=[s[0] for s in self.emp_manager.get_statuses_config()],
                                       state="readonly")
        self.status_combo.grid(row=5, column=1, sticky="ew", pady=5, padx=(10, 0))
        
        # Maszyna/Urządzenie
        ttk.Label(main_frame, text="Maszyna/Urządzenie:").grid(row=6, column=0, sticky="w", pady=5)
        self.maszyna_var = tk.StringVar()
        self.maszyna_combo = ttk.Combobox(main_frame, textvariable=self.maszyna_var,
                                        values=self.emp_manager.get_setting('maszyny'),
                                        state="readonly")
        self.maszyna_combo.grid(row=6, column=1, sticky="ew", pady=5, padx=(10, 0))
        
        # Przyciski
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Zapisz", command=self.save_employee, 
                  style='Accent.TButton').pack(side="left", padx=5)
        ttk.Button(button_frame, text="Anuluj", command=self.destroy).pack(side="left", padx=5)
        
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Wypełnij danymi jeśli edycja
        if self.employee_data:
            self.fill_employee_data()

    def fill_employee_data(self):
        self.imie_entry.insert(0, self.employee_data[1])
        self.nazwisko_entry.insert(0, self.employee_data[2])
        self.stanowisko_var.set(self.employee_data[3])
        self.wydzial_var.set(self.employee_data[4])
        self.zmiana_var.set(self.employee_data[5])
        self.status_var.set(self.employee_data[6])
        self.maszyna_var.set(self.employee_data[7])

    def save_employee(self):
        # Pobierz dane z formularza
        imie = self.imie_entry.get().strip()
        nazwisko = self.nazwisko_entry.get().strip()
        stanowisko = self.stanowisko_var.get()
        wydzial = self.wydzial_var.get()
        zmiana = self.zmiana_var.get()
        status = self.status_var.get()
        maszyna = self.maszyna_var.get()

        # Walidacja
        if not imie or not nazwisko:
            messagebox.showerror("Błąd", "Imię i nazwisko są wymagane.")
            return

        # SPRAWDZENIE OBSADY PRZED ZAPISEM
        if zmiana and "Wolne" not in zmiana and status == "W Pracy":
            staffing_info = self.emp_manager.get_staffing_info(wydzial, zmiana)
            
            if staffing_info['overflow']:
                # Pytaj użytkownika czy na pewno chce dodać/zmienić
                response = messagebox.askyesno(
                    "⚠️ Przekroczenie obsady",
                    f"Wydział: {wydzial}, Zmiana: {zmiana}\n"
                    f"Wymagana obsada: {staffing_info['required']}\n"
                    f"Aktualnie pracujących: {staffing_info['current']}\n"
                    f"Po tej zmianie: {staffing_info['current'] + 1} (+{staffing_info['excess'] + 1})\n\n"
                    f"Czy na pewno chcesz zapisać tego pracownika?\n\n"
                    f"UWAGA: Spowoduje to przekroczenie wymaganej obsady!"
                )
                if not response:
                    return  # Anuluj zapis

        # Zapisz pracownika
        if self.employee_data:
            # Edycja istniejącego pracownika
            result = self.emp_manager.update_employee(
                self.employee_data[0], imie, nazwisko, stanowisko, 
                wydzial, zmiana, status, maszyna
            )
        else:
            # Dodawanie nowego pracownika
            result = self.emp_manager.add_employee(
                imie, nazwisko, stanowisko, wydzial, zmiana, status, maszyna
            )
        
        if result.get('success'):
            messagebox.showinfo("Sukces", "Pracownik zapisany pomyślnie!")
            self.master.refresh_employee_list()
            self.destroy()
        else:
            if result.get('overflow'):
                # To nie powinno się zdarzyć, bo już sprawdziliśmy wyżej
                messagebox.showerror("Błąd", "Przekroczenie obsady - pracownik nie został zapisany.")
            else:
                messagebox.showerror("Błąd", "Nie udało się zapisać pracownika.")
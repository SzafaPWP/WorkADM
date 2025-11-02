import tkinter as tk
from tkinter import ttk, messagebox

class EmployeeDialog(tk.Toplevel):
    def __init__(self, master, emp_manager, employee_data=None):
        super().__init__(master)
        self.master = master
        self.emp_manager = emp_manager
        self.employee_data = employee_data
        self.emp_id = employee_data[0] if employee_data else None
        
        if employee_data:
            self.title("Edytuj Pracownika")
        else:
            self.title("Dodaj Nowego Pracownika")
            
        self.geometry("500x550")
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
        
        # Sekcja zarządzania urlopami i L4 (tylko dla edycji)
        if self.employee_data:
            self.create_vacation_l4_section(main_frame)
        
        # Przyciski
        button_frame = ttk.Frame(main_frame)
        if self.employee_data:
            button_frame.grid(row=9, column=0, columnspan=2, pady=20)
        else:
            button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Zapisz", command=self.save_employee, 
                  style='Accent.TButton').pack(side="left", padx=5)
        ttk.Button(button_frame, text="Anuluj", command=self.destroy).pack(side="left", padx=5)
        
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Wypełnij danymi jeśli edycja
        if self.employee_data:
            self.fill_employee_data()

    def create_vacation_l4_section(self, main_frame):
        """Tworzy sekcję do zarządzania urlopami i L4"""
        # Ramka dla zarządzania urlopami i L4
        management_frame = ttk.LabelFrame(main_frame, text="Zarządzanie urlopami i L4", padding="10")
        management_frame.grid(row=7, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Pobierz aktualne dane o urlopach i L4
        self.current_vacation = self.emp_manager.get_active_vacation(self.emp_id)
        self.current_l4 = self.emp_manager.get_active_l4(self.emp_id)
        
        # Informacje o urlopie
        vacation_info = "Brak aktywnego urlopu"
        if self.current_vacation:
            start_date = self.current_vacation[0]
            end_date = self.current_vacation[1]
            vacation_info = f"Urlop: {start_date} - {end_date}"
        
        ttk.Label(management_frame, text=vacation_info, font=('Arial', 9)).grid(row=0, column=0, sticky="w", pady=5)
        
        # Informacje o L4
        l4_info = "Brak aktywnego L4"
        if self.current_l4:
            start_date = self.current_l4[0]
            end_date = self.current_l4[1]
            l4_info = f"L4: {start_date} - {end_date}"
        
        ttk.Label(management_frame, text=l4_info, font=('Arial', 9)).grid(row=1, column=0, sticky="w", pady=5)
        
        # Przyciski zarządzania
        btn_frame = ttk.Frame(management_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Usuń urlop", 
                  command=self.delete_vacation,
                  state="normal" if self.current_vacation else "disabled",
                  width=12).pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="Usuń L4", 
                  command=self.delete_l4,
                  state="normal" if self.current_l4 else "disabled",
                  width=12).pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="Usuń wszystko", 
                  command=self.delete_all_absences,
                  state="normal" if (self.current_vacation or self.current_l4) else "disabled",
                  width=12).pack(side="left", padx=5)

    def delete_vacation(self):
        """Usuwa aktywny urlop pracownika"""
        if messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz usunąć urlop tego pracownika?"):
            try:
                # Usuń urlop z bazy danych
                self.emp_manager.db.execute_query(
                    "DELETE FROM vacations WHERE employee_id = ?", 
                    (self.emp_id,)
                )
                
                # Zmień status na "W Pracy" jeśli był na urlopie
                if self.employee_data[6] == "Urlop":
                    self.emp_manager.update_employee_status(self.emp_id, "W Pracy")
                
                messagebox.showinfo("Sukces", "Urlop został usunięty.")
                self.master.refresh_employee_list()
                self.destroy()
                
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie udało się usunąć urlopu: {e}")

    def delete_l4(self):
        """Usuwa aktywne L4 pracownika"""
        if messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz usunąć L4 tego pracownika?"):
            try:
                # Usuń L4 z bazy danych
                self.emp_manager.db.execute_query(
                    "DELETE FROM l4_records WHERE employee_id = ?", 
                    (self.emp_id,)
                )
                
                # Zmień status na "W Pracy" jeśli był na L4
                if self.employee_data[6] == "L4":
                    self.emp_manager.update_employee_status(self.emp_id, "W Pracy")
                
                messagebox.showinfo("Sukces", "L4 zostało usunięte.")
                self.master.refresh_employee_list()
                self.destroy()
                
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie udało się usunąć L4: {e}")

    def delete_all_absences(self):
        """Usuwa wszystkie nieobecności pracownika (urlop i L4)"""
        if messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz usunąć wszystkie nieobecności tego pracownika?"):
            try:
                # Usuń urlop z bazy danych
                self.emp_manager.db.execute_query(
                    "DELETE FROM vacations WHERE employee_id = ?", 
                    (self.emp_id,)
                )
                
                # Usuń L4 z bazy danych
                self.emp_manager.db.execute_query(
                    "DELETE FROM l4_records WHERE employee_id = ?", 
                    (self.emp_id,)
                )
                
                # Zmień status na "W Pracy" jeśli był na urlopie lub L4
                if self.employee_data[6] in ["Urlop", "L4"]:
                    self.emp_manager.update_employee_status(self.emp_id, "W Pracy")
                
                messagebox.showinfo("Sukces", "Wszystkie nieobecności zostały usunięte.")
                self.master.refresh_employee_list()
                self.destroy()
                
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie udało się usunąć nieobecności: {e}")

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
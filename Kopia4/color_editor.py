import tkinter as tk
from tkinter import ttk, colorchooser, messagebox

class ColorEditor(tk.Toplevel):
    def __init__(self, master, emp_manager):
        super().__init__(master)
        self.master = master
        self.emp_manager = emp_manager
        self.title("Edytor Kolorów Statusów")
        self.geometry("450x400")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        
        self.create_widgets()
        self.load_current_colors()
        self.center_window()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Nagłówek
        ttk.Label(main_frame, text="🎨 Edytor Kolorów Statusów", 
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        ttk.Label(main_frame, text="Kliknij 'Wybierz' aby zmienić kolor dla każdego statusu", 
                 font=('Arial', 10)).pack(pady=(0, 20))
        
        # Ramka z listą statusów
        list_frame = ttk.LabelFrame(main_frame, text="Statusy", padding="15")
        list_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        self.color_entries = {}
        
        statuses = self.emp_manager.get_statuses_config()
        
        for i, (status_name, current_color) in enumerate(statuses):
            frame = ttk.Frame(list_frame)
            frame.pack(fill='x', pady=8)
            
            # Nazwa statusu
            ttk.Label(frame, text=status_name, width=15, font=('Arial', 10)).pack(side='left')
            
            # Pole z kodem koloru
            entry = ttk.Entry(frame, width=10, font=('Arial', 9))
            entry.insert(0, current_color)
            entry.pack(side='left', padx=5)
            
            # Przycisk wyboru koloru
            btn = ttk.Button(frame, text="Wybierz kolor", width=12,
                           command=lambda e=entry, s=status_name: self.choose_color(e, s))
            btn.pack(side='left', padx=5)
            
            # Podgląd koloru
            preview = tk.Label(frame, text="       ", background=current_color, 
                             relief='solid', borderwidth=2, width=8, font=('Arial', 8))
            preview.pack(side='left', padx=5)
            
            self.color_entries[status_name] = {'entry': entry, 'preview': preview}

        # Przyciski akcji
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="💾 Zapisz zmiany", 
                  command=self.save_colors, style='Accent.TButton', width=15).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="↩️ Przywróć domyślne", 
                  command=self.reset_to_default, width=18).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="❌ Anuluj", 
                  command=self.destroy, width=12).pack(side='left', padx=5)

    def choose_color(self, entry, status_name):
        color_code = colorchooser.askcolor(
            initialcolor=entry.get(), 
            title=f"Wybierz kolor dla: {status_name}"
        )
        if color_code and color_code[1]:
            entry.delete(0, tk.END)
            entry.insert(0, color_code[1])
            self.color_entries[status_name]['preview'].config(background=color_code[1])

    def load_current_colors(self):
        statuses = self.emp_manager.get_statuses_config()
        for status_name, color in statuses:
            if status_name in self.color_entries:
                self.color_entries[status_name]['entry'].delete(0, tk.END)
                self.color_entries[status_name]['entry'].insert(0, color)
                self.color_entries[status_name]['preview'].config(background=color)

    def reset_to_default(self):
        default_colors = {
            "W Pracy": "#3CB371",
            "Urlop": "#FFA500", 
            "L4": "#FF4500",
            "Wolne": "#98FB98"
        }
        
        for status_name, default_color in default_colors.items():
            if status_name in self.color_entries:
                self.color_entries[status_name]['entry'].delete(0, tk.END)
                self.color_entries[status_name]['entry'].insert(0, default_color)
                self.color_entries[status_name]['preview'].config(background=default_color)

    def save_colors(self):
        try:
            for status_name, widgets in self.color_entries.items():
                new_color = widgets['entry'].get()
                # Walidacja koloru
                if not new_color.startswith('#') or len(new_color) != 7:
                    messagebox.showerror("Błąd", f"Nieprawidłowy format koloru dla {status_name}. Użyj formatu #RRGGBB")
                    return
                
                # Aktualizuj w bazie danych
                self.emp_manager.db.execute_query(
                    "UPDATE statuses SET color = ? WHERE name = ?",
                    (new_color, status_name)
                )
            
            self.emp_manager.log_history("Edycja Kolorów", "Zaktualizowano kolory statusów")
            messagebox.showinfo("Sukces", "Kolory zostały zapisane!\nAplikacja zostanie odświeżona.")
            
            # Odśwież główne okno
            if hasattr(self.master, 'refresh_employee_list'):
                self.master.refresh_employee_list()
                
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się zapisać kolorów: {e}")

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')
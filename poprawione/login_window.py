import tkinter as tk
from tkinter import ttk, messagebox
from db_manager import DBManager
from PIL import Image, ImageTk
import os

class LoginWindow(tk.Toplevel):
    def __init__(self, master, db_manager: DBManager, login_callback):
        super().__init__(master)
        self.master = master
        self.db = db_manager
        self.login_callback = login_callback
        self.title("Logowanie")
        self.geometry("400x500")
        self.resizable(False, False)
        
        self.center_window()
        self.create_widgets()

    def center_window(self):
        self.update_idletasks()
        width = 400
        height = 500
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        # Główna ramka
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Logo
        try:
            if os.path.exists("logo.png"):
                image = Image.open("logo.png")
                image = image.resize((100, 100), Image.Resampling.LANCZOS)
                self.logo = ImageTk.PhotoImage(image)
                ttk.Label(main_frame, image=self.logo).pack(pady=20)
        except:
            ttk.Label(main_frame, text="🔐 LOGOWANIE", font=('Arial', 16, 'bold')).pack(pady=20)
        
        # Formularz
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill="x", pady=20)
        
        # Użytkownik
        ttk.Label(form_frame, text="Użytkownik:").grid(row=0, column=0, sticky="w", pady=10)
        users = self.db.fetch_all("SELECT username FROM users")
        user_names = [user[0] for user in users] if users else []
        self.username_var = tk.StringVar()
        self.user_combo = ttk.Combobox(form_frame, textvariable=self.username_var, values=user_names, state="readonly")
        self.user_combo.grid(row=0, column=1, sticky="ew", pady=10, padx=(10, 0))
        
        # AUTOMATYCZNE PRZEJŚCIE DO HASŁA
        self.user_combo.bind('<<ComboboxSelected>>', self.on_user_selected)
        # ENTER W COMBOBOX = PRZEJŚCIE DO HASŁA
        self.user_combo.bind('<Return>', self.on_user_enter)
        
        # Hasło
        ttk.Label(form_frame, text="Hasło:").grid(row=1, column=0, sticky="w", pady=10)
        self.password_entry = ttk.Entry(form_frame, show="*")
        self.password_entry.grid(row=1, column=1, sticky="ew", pady=10, padx=(10, 0))
        
        # ENTER W HASLE = LOGOWANIE
        self.password_entry.bind('<Return>', lambda event: self.login())
        
        # Przyciski
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=30)
        
        self.login_btn = ttk.Button(btn_frame, text="Zaloguj", command=self.login, width=12)
        self.login_btn.pack(side="left", padx=10)
        
        ttk.Button(btn_frame, text="Anuluj", command=self.cancel, width=12).pack(side="left", padx=10)
        
        # ENTER W CALYM OKNIE = LOGOWANIE (jeśli hasło jest wypełnione)
        self.bind('<Return>', self.on_global_enter)
        
        form_frame.columnconfigure(1, weight=1)
        self.user_combo.focus()

    def on_user_selected(self, event):
        """Automatyczne przejście do pola hasła po wybraniu użytkownika z listy"""
        self.password_entry.focus_set()
        self.password_entry.select_range(0, tk.END)

    def on_user_enter(self, event):
        """Enter w combobox - przejście do hasła"""
        self.password_entry.focus_set()
        self.password_entry.select_range(0, tk.END)
        return "break"  # Zapobiega domyślnej akcji

    def on_global_enter(self, event):
        """Enter w dowolnym miejscu okna - logowanie jeśli hasło jest wypełnione"""
        if self.password_entry.get():
            self.login()
        return "break"

    def login(self):
        username = self.username_var.get()
        password = self.password_entry.get()
        
        if not username:
            messagebox.showerror("Błąd", "Wybierz użytkownika z listy")
            self.user_combo.focus_set()
            return
            
        if not password:
            messagebox.showerror("Błąd", "Wprowadź hasło")
            self.password_entry.focus_set()
            return
            
        user_data = self.db.fetch_one("SELECT username, role FROM users WHERE username=? AND password=?", (username, password))
        if user_data:
            self.login_callback({'username': user_data[0], 'role': user_data[1]})
            self.destroy()
        else:
            messagebox.showerror("Błąd", "Nieprawidłowe hasło")
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus_set()

    def cancel(self):
        if messagebox.askyesno("Wyjście", "Zamknąć aplikację?"):
            self.master.destroy()

    def destroy(self):
        super().destroy()
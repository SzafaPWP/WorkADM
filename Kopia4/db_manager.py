import sqlite3
import shutil
import os
from datetime import datetime

class DBManager:
    def __init__(self, db_name="hr_system.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Tabela Użytkowników
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT -- 'admin', 'manager', 'operator'
            )
        """)
        # Tabela Pracowników
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                imie TEXT,
                nazwisko TEXT,
                stanowisko TEXT,
                wydzial TEXT,
                zmiana TEXT,
                status TEXT, -- 'W Pracy', 'Urlop', 'L4', 'Wolne'
                maszyna TEXT
            )
        """)
        # Tabela Ustawień
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        # Tabela Historii
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                operator TEXT,
                action TEXT,
                details TEXT
            )
        """)
        # Tabela Ustawień Zmian
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS shifts (
                name TEXT PRIMARY KEY,
                start_time TEXT, -- HH:MM
                end_time TEXT,   -- HH:MM
                color TEXT
            )
        """)
        # Tabela Ustawień Statusów
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS statuses (
                name TEXT PRIMARY KEY,
                color TEXT
            )
        """)
        # Tabela Wymaganej Obsady
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS required_staff (
                wydzial TEXT,
                zmiana TEXT,
                required_count INTEGER,
                PRIMARY KEY (wydzial, zmiana)
            )
        """)
        # NOWA TABELA: Urlopy
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS vacations (
                id INTEGER PRIMARY KEY,
                employee_id INTEGER,
                start_date DATE,
                end_date DATE,
                total_days INTEGER,
                vacation_type TEXT,
                status TEXT DEFAULT 'Zaplanowany',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            )
        """)
        
        # NOWA TABELA: L4
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS l4_records (
                id INTEGER PRIMARY KEY,
                employee_id INTEGER,
                start_date DATE,
                end_date DATE,
                total_days INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            )
        """)
        
        self.conn.commit()
        self.initialize_default_data()

    def initialize_default_data(self):
        # Dodanie domyślnego admina
        self.cursor.execute("SELECT * FROM users WHERE username='admin'")
        if not self.cursor.fetchone():
            self.cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                                ("admin", "admin123", "admin"))

        # Dodanie domyślnych Zmian
        self.cursor.execute("SELECT COUNT(*) FROM shifts")
        shift_count = self.cursor.fetchone()[0]
        
        if shift_count == 0:
            default_shifts = [
                ("A - Rano (6-14)", "06:00", "14:00", "#ADD8E6"),
                ("B - Południe (14-22)", "14:00", "22:00", "#F08080"),
                ("C - Noc (22-6)", "22:00", "06:00", "#20B2AA"),
                ("D - Wolne", "00:00", "00:00", "#90EE90")
            ]
            for name, start, end, color in default_shifts:
                self.cursor.execute("INSERT OR IGNORE INTO shifts (name, start_time, end_time, color) VALUES (?, ?, ?, ?)",
                                    (name, start, end, color))

        # Dodanie domyślnych Statusów
        self.cursor.execute("SELECT COUNT(*) FROM statuses")
        status_count = self.cursor.fetchone()[0]
        
        if status_count == 0:
            default_statuses = [
                ("W Pracy", "#3CB371"),
                ("Urlop", "#FFA500"),
                ("L4", "#FF4500"),
                ("Wolne", "#98FB98")
            ]
            for name, color in default_statuses:
                self.cursor.execute("INSERT OR IGNORE INTO statuses (name, color) VALUES (?, ?)",
                                    (name, color))
        
        self.conn.commit()

    def backup_database(self, backup_dir="backups"):
        """Tworzy backup bazy danych"""
        try:
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"hr_backup_{timestamp}.db")
            
            # Zamknij połączenie przed kopiowaniem
            self.conn.close()
            
            # Skopiuj plik bazy danych
            shutil.copy2(self.db_name, backup_file)
            
            # Otwórz ponownie połączenie
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            
            # Zapisz w historii
            self.execute_query(
                "INSERT INTO history (operator, action, details) VALUES (?, ?, ?)",
                ("SYSTEM", "Backup bazy", f"Utworzono backup: {backup_file}")
            )
            
            return backup_file
        except Exception as e:
            print(f"Błąd podczas backupu: {e}")
            # Przywróć połączenie w przypadku błędu
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            return None

    def get_connection(self):
        return self.conn

    def execute_query(self, query, params=()):
        self.cursor.execute(query, params)
        self.conn.commit()

    def fetch_all(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def fetch_one(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()
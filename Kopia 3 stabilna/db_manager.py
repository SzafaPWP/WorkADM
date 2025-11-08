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
        self.migrate_shift_data()  # NOWA MIGRACJA

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
                zmiana TEXT,  -- TERAZ TYLKO LITERA: A, B, C, D
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
        # Tabela Historii - ROZSZERZONA O EMPLOYEE_ID
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                operator TEXT,
                action TEXT,
                details TEXT,
                employee_id INTEGER  -- NOWA KOLUMNA
            )
        """)
        
        # Sprawdź czy kolumna employee_id istnieje, jeśli nie - dodaj
        self.cursor.execute("PRAGMA table_info(history)")
        columns = [col[1] for col in self.cursor.fetchall()]
        if 'employee_id' not in columns:
            self.cursor.execute("ALTER TABLE history ADD COLUMN employee_id INTEGER")
        
        # Tabela Ustawień Zmian
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS shifts (
                name TEXT PRIMARY KEY,  -- TERAZ TYLKO LITERY: A, B, C, D
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
                zmiana TEXT,  -- LITERA ZMIANY
                required_count INTEGER,
                PRIMARY KEY (wydzial, zmiana)
            )
        """)
        # TABELA: Urlopy
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
        
        # TABELA: L4
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

    def migrate_shift_data(self):
        """Migracja starych pełnych nazw zmian na same litery"""
        try:
            # Sprawdź czy migracja już została wykonana
            self.cursor.execute("SELECT value FROM settings WHERE key='shift_migration_done'")
            if self.cursor.fetchone():
                return  # Migracja już wykonana
            
            print("🔄 Rozpoczynam migrację danych zmian...")
            
            # Mapowanie starych nazw na nowe litery
            shift_mapping = {
                'A - Rano (6-14)': 'A',
                'A - Poludnie (14-22)': 'A',
                'A - Noc (22-6)': 'A',
                'B - Rano (6-14)': 'B',
                'B - Poludnie (14-22)': 'B',
                'B - Noc (22-6)': 'B',
                'C - Rano (6-14)': 'C',
                'C - Poludnie (14-22)': 'C',
                'C - Noc (22-6)': 'C',
                'D - Wolne': 'D'
            }
            
            # 1. Migracja pracowników - zamień pełne nazwy na litery
            self.cursor.execute("SELECT id, zmiana FROM employees")
            employees = self.cursor.fetchall()
            
            for emp_id, old_shift in employees:
                if old_shift:
                    # Spróbuj znaleźć mapowanie
                    new_shift = shift_mapping.get(old_shift)
                    
                    # Jeśli nie znaleziono dokładnego mapowania, wyciągnij literę
                    if not new_shift:
                        if old_shift.startswith('A'):
                            new_shift = 'A'
                        elif old_shift.startswith('B'):
                            new_shift = 'B'
                        elif old_shift.startswith('C'):
                            new_shift = 'C'
                        elif old_shift.startswith('D'):
                            new_shift = 'D'
                        else:
                            new_shift = 'D'  # Domyślnie wolne
                    
                    self.cursor.execute("UPDATE employees SET zmiana=? WHERE id=?", (new_shift, emp_id))
            
            # 2. Migracja tabeli shifts - zamień na litery
            self.cursor.execute("SELECT name, start_time, end_time, color FROM shifts")
            old_shifts = self.cursor.fetchall()
            
            # Usuń stare wpisy
            self.cursor.execute("DELETE FROM shifts")
            
            # Dodaj nowe definicje zmian (tylko litery)
            default_shifts = [
                ("A", "06:00", "14:00", "#ADD8E6"),
                ("B", "14:00", "22:00", "#F08080"),
                ("C", "22:00", "06:00", "#20B2AA"),
                ("D", "00:00", "00:00", "#90EE90")
            ]
            
            # Jeśli były stare definicje, użyj pierwszej znalezionej dla każdej litery
            shift_times = {}
            for old_name, start, end, color in old_shifts:
                letter = old_name[0] if old_name else 'D'
                if letter not in shift_times:
                    shift_times[letter] = (start, end, color)
            
            # Wstaw nowe definicje
            for letter, start, end, color in default_shifts:
                if letter in shift_times:
                    start, end, color = shift_times[letter]
                self.cursor.execute("INSERT OR REPLACE INTO shifts (name, start_time, end_time, color) VALUES (?, ?, ?, ?)",
                                  (letter, start, end, color))
            
            # 3. Migracja required_staff
            self.cursor.execute("SELECT wydzial, zmiana, required_count FROM required_staff")
            required = self.cursor.fetchall()
            
            self.cursor.execute("DELETE FROM required_staff")
            
            for wydzial, old_shift, count in required:
                new_shift = shift_mapping.get(old_shift)
                if not new_shift:
                    if old_shift and old_shift[0] in ['A', 'B', 'C', 'D']:
                        new_shift = old_shift[0]
                    else:
                        new_shift = 'D'
                
                self.cursor.execute("INSERT OR REPLACE INTO required_staff (wydzial, zmiana, required_count) VALUES (?, ?, ?)",
                                  (wydzial, new_shift, count))
            
            # Oznacz migrację jako wykonaną
            self.cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('shift_migration_done', '1')")
            self.conn.commit()
            
            print("✅ Migracja danych zmian zakończona pomyślnie!")
            
        except Exception as e:
            print(f"⚠️ Błąd migracji (może już była wykonana): {e}")
            self.conn.rollback()

    def initialize_default_data(self):
        # Dodanie domyślnego admina
        self.cursor.execute("SELECT * FROM users WHERE username='admin'")
        if not self.cursor.fetchone():
            self.cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                                ("admin", "admin123", "admin"))

        # Dodanie domyślnych Zmian (TYLKO LITERY)
        self.cursor.execute("SELECT COUNT(*) FROM shifts")
        shift_count = self.cursor.fetchone()[0]
        
        if shift_count == 0:
            default_shifts = [
                ("A", "06:00", "14:00", "#ADD8E6"),
                ("B", "14:00", "22:00", "#F08080"),
                ("C", "22:00", "06:00", "#20B2AA"),
                ("D", "00:00", "00:00", "#90EE90")
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
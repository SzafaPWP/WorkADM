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
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                imie TEXT,
                nazwisko TEXT,
                stanowisko TEXT,
                wydzial TEXT,
                zmiana TEXT,
                status TEXT,
                maszyna TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                operator TEXT,
                action TEXT,
                details TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS employee_history (
                id INTEGER PRIMARY KEY,
                employee_id INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                operator TEXT,
                action TEXT,
                details TEXT,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS shifts (
                name TEXT PRIMARY KEY,
                start_time TEXT,
                end_time TEXT,
                color TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS statuses (
                name TEXT PRIMARY KEY,
                color TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS required_staff (
                wydzial TEXT,
                zmiana TEXT,
                required_count INTEGER,
                PRIMARY KEY (wydzial, zmiana)
            )
        """)
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

    def backup_database(self, backup_dir="backups"):
        try:
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"hr_backup_{timestamp}.db")
            self.conn.close()
            shutil.copy2(self.db_name, backup_file)
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            self.execute_query("INSERT INTO history (operator, action, details) VALUES (?, ?, ?)", ("SYSTEM", "Backup bazy", f"Utworzono backup: {backup_file}" ))
            return backup_file
        except Exception as e:
            print(f"Błąd podczas backupu: {e}")
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

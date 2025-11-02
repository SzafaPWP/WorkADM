from db_manager import DBManager
import datetime

class EmployeeManagement:
    def __init__(self, db_manager: DBManager, current_user=None):
        self.db = db_manager
        self.current_user = current_user  # POPRAWIONE: current_user zamiast user

    def set_current_user(self, user):
        self.current_user = user

    # --- Pracownicy (CRUD) ---
    def add_employee(self, imie, nazwisko, stanowisko, wydzial, zmiana, status, maszyna):
        try:
            # SPRAWDZENIE OBSADY PRZED DODANIEM NOWEGO PRACOWNIKA
            if zmiana and "Wolne" not in zmiana and status == "W Pracy":
                staffing_info = self.get_staffing_info(wydzial, zmiana)
                if staffing_info['overflow']:
                    # Zwróć specjalny status zamiast wyświetlać alert
                    return {'success': False, 'overflow': True, 'staffing_info': staffing_info}

            # AUTOMATYCZNE USTAWIANIE STATUSU WEDŁUG ZMIANY
            if zmiana == "D - Wolne" or "Wolne" in zmiana:
                status = "Wolne"
            elif zmiana in ["A - Rano (6-14)", "B - Południe (14-22)", "C - Noc (22-6)"]:
                status = "W Pracy"
                
            self.db.execute_query("""
                INSERT INTO employees (imie, nazwisko, stanowisko, wydzial, zmiana, status, maszyna)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (imie, nazwisko, stanowisko, wydzial, zmiana, status, maszyna))
            self.log_history("Dodanie Pracownika", f"Dodano pracownika: {imie} {nazwisko}")
            return {'success': True, 'overflow': False}
        except Exception as e:
            print(f"Błąd dodawania pracownika: {e}")
            return {'success': False, 'overflow': False}

    def update_employee(self, emp_id, imie, nazwisko, stanowisko, wydzial, zmiana, status, maszyna):
        old_emp = self.db.fetch_one("SELECT * FROM employees WHERE id=?", (emp_id,))
        if not old_emp:
            return {'success': False, 'overflow': False}

        try:
            # SPRAWDZENIE OBSADY PRZED AKTUALIZACJĄ
            if zmiana and "Wolne" not in zmiana and status == "W Pracy":
                staffing_info = self.get_staffing_info(wydzial, zmiana)
                # Jeśli pracownik nie był wcześniej na tej zmianie, sprawdź przekroczenie
                if old_emp[5] != zmiana and staffing_info['overflow']:
                    return {'success': False, 'overflow': True, 'staffing_info': staffing_info}

            # AUTOMATYCZNE USTAWIANIE STATUSU WEDŁUG ZMIANY
            if zmiana == "D - Wolne" or "Wolne" in zmiana:
                status = "Wolne"
            elif zmiana in ["A - Rano (6-14)", "B - Południe (14-22)", "C - Noc (22-6)"]:
                status = "W Pracy"
                
            self.db.execute_query("""
                UPDATE employees SET imie=?, nazwisko=?, stanowisko=?, wydzial=?, zmiana=?, status=?, maszyna=?
                WHERE id=?
            """, (imie, nazwisko, stanowisko, wydzial, zmiana, status, maszyna, emp_id))

            details = f"Zmieniono dane pracownika ID {emp_id}: {old_emp[1]} {old_emp[2]}"
            self.log_history("Edycja Pracownika", details)
            return {'success': True, 'overflow': False}
        except Exception as e:
            print(f"Błąd aktualizacji pracownika: {e}")
            return {'success': False, 'overflow': False}

    def delete_employee(self, emp_id):
        emp_name = self.db.fetch_one("SELECT imie, nazwisko FROM employees WHERE id=?", (emp_id,))
        try:
            self.db.execute_query("DELETE FROM employees WHERE id=?", (emp_id,))
            if emp_name:
                self.log_history("Usunięcie Pracownika", f"Usunięto pracownika: {emp_name[0]} {emp_name[1]}")
            return True
        except Exception as e:
            print(f"Błąd usuwania pracownika: {e}")
            return False

    def get_all_employees(self):
        return self.db.fetch_all("SELECT * FROM employees ORDER BY nazwisko, imie")

    # --- NOWE METODY DO SPRAWDZANIA OBSADY ---
    def get_staffing_info(self, wydzial, zmiana):
        """Zwraca informacje o obsadzie dla wydziału i zmiany"""
        required = self.get_required_staff_by_wydzial_shift(wydzial, zmiana)
        current_count = len(self.db.fetch_all(
            "SELECT id FROM employees WHERE wydzial=? AND zmiana=? AND status='W Pracy'",
            (wydzial, zmiana)
        ))
        
        return {
            'required': required,
            'current': current_count,
            'free_slots': required - current_count if required > 0 else 999,
            'overflow': current_count >= required if required > 0 else False,
            'excess': current_count - required if required > 0 and current_count > required else 0
        }

    def check_staffing_overflow(self, wydzial, zmiana, current_count):
        """Sprawdza czy nie przekraczamy wymaganej obsady"""
        required = self.get_required_staff_by_wydzial_shift(wydzial, zmiana)
        if required > 0 and current_count >= required:
            return {
                'overflow': True,
                'required': required,
                'current': current_count,
                'excess': current_count - required
            }
        return {'overflow': False}

    def find_available_shifts(self, wydzial):
        """Znajduje zmiany z wolnymi miejscami dla danego wydziału"""
        shifts = [s[0] for s in self.get_shifts_config() if "Wolne" not in s[0]]
        available_shifts = []
        
        for shift in shifts:
            required = self.get_required_staff_by_wydzial_shift(wydzial, shift)
            if required > 0:
                current_count = len(self.db.fetch_all(
                    "SELECT id FROM employees WHERE wydzial=? AND zmiana=? AND status='W Pracy'",
                    (wydzial, shift)
                ))
                if current_count < required:
                    available_shifts.append({
                        'shift': shift,
                        'required': required,
                        'current': current_count,
                        'free_slots': required - current_count
                    })
        
        # Sortuj według liczby wolnych miejsc (malejąco)
        return sorted(available_shifts, key=lambda x: x['free_slots'], reverse=True)

    def auto_adjust_overflow(self, wydzial, zmiana):
        """Automatycznie przenosi nadmiarowych pracowników do innych zmian"""
        employees = self.db.fetch_all(
            "SELECT id, imie, nazwisko FROM employees WHERE wydzial=? AND zmiana=? AND status='W Pracy' ORDER BY id",
            (wydzial, zmiana)
        )
        
        required = self.get_required_staff_by_wydzial_shift(wydzial, zmiana)
        if required <= 0:
            return []  # Brak wymagań - nie ma przekroczenia
        
        excess = len(employees) - required
        if excess <= 0:
            return []  # Brak nadmiaru
        
        available_shifts = self.find_available_shifts(wydzial)
        moved_employees = []
        
        for i in range(min(excess, len(available_shifts))):
            emp_id, imie, nazwisko = employees[required + i]
            new_shift = available_shifts[i]['shift']
            
            # Przenieś pracownika
            if self.move_employee(emp_id, None, new_shift, None):
                moved_employees.append({
                    'emp_id': emp_id,
                    'name': f"{imie} {nazwisko}",
                    'from_shift': zmiana,
                    'to_shift': new_shift
                })
        
        return moved_employees

    def get_overflow_alerts(self):
        """Zwraca listę wszystkich przekroczeń obsady"""
        alerts = []
        wydzialy = self.get_setting('wydzialy')
        shifts = [s[0] for s in self.get_shifts_config() if "Wolne" not in s[0]]
        
        for wydzial in wydzialy:
            for shift in shifts:
                required = self.get_required_staff_by_wydzial_shift(wydzial, shift)
                if required > 0:
                    current_count = len(self.db.fetch_all(
                        "SELECT id FROM employees WHERE wydzial=? AND zmiana=? AND status='W Pracy'",
                        (wydzial, shift)
                    ))
                    if current_count > required:
                        alerts.append({
                            'wydzial': wydzial,
                            'zmiana': shift,
                            'wymagane': required,
                            'aktualne': current_count,
                            'nadmiar': current_count - required
                        })
        
        return alerts

    def get_overflow_policy(self):
        """Pobiera zapisaną politykę przekroczeń"""
        try:
            result = self.db.fetch_one("SELECT value FROM settings WHERE key='overflow_policy'")
            return result[0] if result else "warning"
        except:
            return "warning"

    def save_overflow_policy(self, policy):
        """Zapisuje politykę przekroczeń"""
        self.db.execute_query("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", 
                            ("overflow_policy", policy))

    # --- Zarządzanie Stanem Pracownika ---
    def move_employee(self, emp_id, new_wydzial=None, new_zmiana=None, new_stanowisko=None):
        old_data = self.db.fetch_one("SELECT wydzial, zmiana, stanowisko FROM employees WHERE id=?", (emp_id,))
        updates = []
        params = []
        details = []

        if new_wydzial and new_wydzial != old_data[0]:
            updates.append("wydzial=?")
            params.append(new_wydzial)
            details.append(f"wydział z {old_data[0]} na {new_wydzial}")
        
        if new_zmiana and new_zmiana != old_data[1]:
            updates.append("zmiana=?")
            params.append(new_zmiana)
            details.append(f"zmiana z {old_data[1]} na {new_zmiana}")
            
            # AUTOMATYCZNA ZMIANA STATUSU WEDŁUG ZMIANY
            if new_zmiana == "D - Wolne" or "Wolne" in new_zmiana:
                updates.append("status=?")
                params.append("Wolne")
                details.append("status na 'Wolne' (automatycznie)")
            elif new_zmiana in ["A - Rano (6-14)", "B - Południe (14-22)", "C - Noc (22-6)"]:
                updates.append("status=?")
                params.append("W Pracy")
                details.append("status na 'W Pracy' (automatycznie)")

        if new_stanowisko and new_stanowisko != old_data[2]:
            updates.append("stanowisko=?")
            params.append(new_stanowisko)
            details.append(f"stanowisko z {old_data[2]} na {new_stanowisko}")

        if not updates:
            return True

        query = f"UPDATE employees SET {', '.join(updates)} WHERE id=?"
        params.append(emp_id)

        try:
            self.db.execute_query(query, params)
            emp_name = self.db.fetch_one("SELECT imie, nazwisko FROM employees WHERE id=?", (emp_id,))
            self.log_history("Przeniesienie Pracownika", f"Przeniesiono {emp_name[0]} {emp_name[1]}: {', '.join(details)}")
            return True
        except Exception as e:
            print(f"Błąd przeniesienia pracownika: {e}")
            return False

    def update_employee_status(self, emp_id, new_status):
        old_status = self.db.fetch_one("SELECT status FROM employees WHERE id=?", (emp_id,))[0]
        if old_status == new_status: return True

        try:
            self.db.execute_query("UPDATE employees SET status=? WHERE id=?", (new_status, emp_id))
            emp_name = self.db.fetch_one("SELECT imie, nazwisko FROM employees WHERE id=?", (emp_id,))
            self.log_history("Zmiana Statusu", f"Zmieniono status {emp_name[0]} {emp_name[1]} z '{old_status}' na '{new_status}'")
            return True
        except Exception as e:
            print(f"Błąd zmiany statusu: {e}")
            return False

    def update_employee_machine(self, emp_id, new_machine):
        old_machine = self.db.fetch_one("SELECT maszyna FROM employees WHERE id=?", (emp_id,))[0]
        if old_machine == new_machine: return True

        try:
            self.db.execute_query("UPDATE employees SET maszyna=? WHERE id=?", (new_machine, emp_id))
            emp_name = self.db.fetch_one("SELECT imie, nazwisko FROM employees WHERE id=?", (emp_id,))
            self.log_history("Zmiana Maszyny", f"Zmieniono maszynę {emp_name[0]} {emp_name[1]} z '{old_machine}' na '{new_machine}'")
            return True
        except Exception as e:
            print(f"Błąd zmiany maszyny: {e}")
            return False

    # --- Logowanie Historii ---
    def log_history(self, action, details):
        operator = self.current_user.get('username', 'SYSTEM') if self.current_user else 'SYSTEM'
        self.db.execute_query("""
            INSERT INTO history (operator, action, details) VALUES (?, ?, ?)
        """, (operator, action, details))

    def get_history(self):
        return self.db.fetch_all("SELECT * FROM history ORDER BY timestamp DESC")

    # --- Ustawienia ---
    def get_settings_list(self, table_name):
        return self.db.fetch_all(f"SELECT * FROM {table_name}")

    def add_setting(self, table_name, data):
        if table_name == 'users':
            if not data.get('password') or not data.get('role'): return False
            self.db.execute_query("INSERT OR REPLACE INTO users (username, password, role) VALUES (?, ?, ?)",
                                  (data['username'], data['password'], data['role']))
        elif table_name == 'shifts':
             self.db.execute_query("INSERT OR REPLACE INTO shifts (name, start_time, end_time, color) VALUES (?, ?, ?, ?)",
                                  (data['name'], data['start_time'], data['end_time'], data['color']))
        elif table_name == 'statuses':
            self.db.execute_query("INSERT OR REPLACE INTO statuses (name, color) VALUES (?, ?)",
                                  (data['name'], data['color']))
        elif table_name in ['wydzialy', 'stanowiska', 'maszyny']:
            current_list = self.get_setting(table_name)
            if data['name'] not in current_list:
                current_list.append(data['name'])
                self.save_setting(table_name, current_list)
                return True
            return False
        
        self.log_history("Ustawienia", f"Dodano/Edytowano w {table_name}: {data.get('name') or data.get('username')}")
        return True

    def delete_setting(self, table_name, name):
        if table_name == 'users':
            self.db.execute_query("DELETE FROM users WHERE username=?", (name,))
        elif table_name == 'shifts':
            self.db.execute_query("DELETE FROM shifts WHERE name=?", (name,))
        elif table_name == 'statuses':
            self.db.execute_query("DELETE FROM statuses WHERE name=?", (name,))
        elif table_name in ['wydzialy', 'stanowiska', 'maszyny']:
            current_list = self.get_setting(table_name)
            if name in current_list:
                current_list.remove(name)
                self.save_setting(table_name, current_list)
                return True
            return False
        
        self.log_history("Ustawienia", f"Usunięto z {table_name}: {name}")
        return True

    def get_setting(self, key):
        """Pobiera ustawienie jako listę z bazy danych"""
        result = self.db.fetch_one("SELECT value FROM settings WHERE key=?", (key,))
        if result:
            return result[0].split(',') if result[0] else []
        return []

    def save_setting(self, key, value_list):
        value_str = ','.join(value_list)
        self.db.execute_query("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value_str))
        self.log_history("Ustawienia", f"Zapisano ustawienia dla klucza: {key}")
        
    def get_shifts_config(self):
        """Pobiera konfigurację zmian"""
        try:
            return self.db.fetch_all("SELECT name, start_time, end_time, color FROM shifts")
        except Exception as e:
            print(f"Błąd pobierania konfiguracji zmian: {e}")
            return []

    def get_statuses_config(self):
        """Pobiera konfigurację statusów"""
        try:
            return self.db.fetch_all("SELECT name, color FROM statuses")
        except Exception as e:
            print(f"Błąd pobierania konfiguracji statusów: {e}")
            return []

    def get_shift_color(self, shift_name):
        """Pobiera kolor dla konkretnej zmiany"""
        try:
            result = self.db.fetch_one("SELECT color FROM shifts WHERE name=?", (shift_name,))
            return result[0] if result else 'white'
        except Exception as e:
            print(f"Błąd pobierania koloru zmiany: {e}")
            return 'white'

    def get_status_color(self, status_name):
        """Pobiera kolor dla konkretnego statusu"""
        try:
            result = self.db.fetch_one("SELECT color FROM statuses WHERE name=?", (status_name,))
            return result[0] if result else 'white'
        except Exception as e:
            print(f"Błąd pobierania koloru statusu: {e}")
            return 'white'

    def get_required_staff_by_wydzial_shift(self, wydzial, shift):
        """Pobiera wymaganą obsadę dla wydziału i zmiany"""
        try:
            result = self.db.fetch_one("SELECT required_count FROM required_staff WHERE wydzial=? AND zmiana=?", (wydzial, shift))
            return result[0] if result else 0
        except Exception as e:
            print(f"Błąd pobierania wymaganej obsady: {e}")
            return 0

    def save_required_staff(self, wydzial, shift, count):
        """Zapisuje wymaganą obsadę"""
        self.db.execute_query("""
            INSERT OR REPLACE INTO required_staff (wydzial, zmiana, required_count)
            VALUES (?, ?, ?)
        """, (wydzial, shift, count))
        self.log_history("Ustawienia", f"Ustawiono wymaganą obsadę: {wydzial}, {shift} na {count} os.")

    # NOWA FUNKCJA: Sprawdzanie alertów o brakach kadrowych
    def check_staffing_alerts(self):
        """Sprawdza alerty o brakach kadrowych"""
        alerts = []
        
        wydzialy = self.get_setting('wydzialy')
        shifts = [s[0] for s in self.get_shifts_config()]
        
        for wydzial in wydzialy:
            for shift in shifts:
                required = self.get_required_staff_by_wydzial_shift(wydzial, shift)
                if required > 0:
                    # Policz pracowników na tej zmianie z statusem "W Pracy"
                    current_count = len(self.db.fetch_all(
                        "SELECT id FROM employees WHERE wydzial=? AND zmiana=? AND status='W Pracy'",
                        (wydzial, shift)
                    ))
                    
                    if current_count < required:
                        alerts.append({
                            'wydzial': wydzial,
                            'zmiana': shift,
                            'wymagane': required,
                            'aktualne': current_count,
                            'brakuje': required - current_count
                        })
        
        return alerts

    # NOWA FUNKCJA: Pobieranie urlopów
    def get_vacations(self):
        """Pobiera listę urlopów"""
        return self.db.fetch_all("""
            SELECT v.*, e.imie, e.nazwisko 
            FROM vacations v 
            JOIN employees e ON v.employee_id = e.id 
            ORDER BY v.start_date DESC
        """)

    # NOWE FUNKCJE: Pobieranie L4
    def get_l4_records(self):
        """Pobiera listę zwolnień L4"""
        return self.db.fetch_all("""
            SELECT l.*, e.imie, e.nazwisko 
            FROM l4_records l 
            JOIN employees e ON l.employee_id = e.id 
            ORDER BY l.start_date DESC
        """)

    def get_active_vacation(self, emp_id):
        """Pobiera aktywny urlop pracownika"""
        today = datetime.datetime.now().date()
        return self.db.fetch_one("""
            SELECT start_date, end_date 
            FROM vacations 
            WHERE employee_id = ? AND start_date <= ? AND end_date >= ?
            ORDER BY start_date DESC LIMIT 1
        """, (emp_id, today, today))

    def get_active_l4(self, emp_id):
        """Pobiera aktywne L4 pracownika"""
        today = datetime.datetime.now().date()
        return self.db.fetch_one("""
            SELECT start_date, end_date 
            FROM l4_records 
            WHERE employee_id = ? AND start_date <= ? AND end_date >= ?
            ORDER BY start_date DESC LIMIT 1
        """, (emp_id, today, today))
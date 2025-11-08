import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
from employee_management import EmployeeManagement

# Rejestracja czcionki z polskimi znakami
pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf')) # Zakłada, że plik arial.ttf jest dostępny
pdfmetrics.registerFont(TTFont('Arial-Bold', 'arialbd.ttf'))

class ReportsWindow(tk.Toplevel):
    def __init__(self, master, emp_manager: EmployeeManagement):
        super().__init__(master)
        self.master = master
        self.emp_manager = emp_manager
        self.title("Generowanie Raportów")
        self.geometry("400x200")
        self.transient(master)
        self.grab_set()

        self.create_widgets()
        
        # Centrowanie
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')

    def create_widgets(self):
        tk.Label(self, text="Generuj Raport (Pełna Lista Pracowników)").pack(pady=10)
        
        ttk.Button(self, text="Generuj Raport PDF", command=self.generate_pdf_report).pack(fill='x', padx=20, pady=5)
        ttk.Button(self, text="Generuj Raport Excel", command=self.generate_excel_report).pack(fill='x', padx=20, pady=5)

    def get_employee_dataframe(self):
        """Pobiera dane pracowników i zwraca jako DataFrame z nowymi kolumnami."""
        # Kolumny z db_manager.py: id, imie, nazwisko, stanowisko, wydzial, zmiana, status, maszyna, data_zatrudnienia
        data = self.emp_manager.get_all_employees()
        
        # Pobierz dane urlopów i L4
        vacations = self.emp_manager.get_vacations()
        l4_records = self.emp_manager.get_l4_records()
        
        export_data = []
        for emp in data:
            emp_id, imie, nazwisko, stanowisko, wydzial, zmiana, status, maszyna = emp[:8]  # Pierwsze 8 kolumn
            
            # Znajdź urlop dla pracownika
            vacation_info = ""
            for vac in vacations:
                if vac[1] == emp_id:  # vac[1] to employee_id
                    start = vac[2]  # start_date
                    end = vac[3]    # end_date
                    vacation_info = f"{start} - {end}"
                    break
            
            # Znajdź L4 dla pracownika
            l4_info = ""
            for l4 in l4_records:
                if l4[1] == emp_id:  # l4[1] to employee_id
                    start = l4[2]  # start_date
                    end = l4[3]    # end_date
                    l4_info = f"{start} - {end}"
                    break
            
            export_data.append({
                "ID": emp_id,
                "Imię": imie,
                "Nazwisko": nazwisko,
                "Stanowisko": stanowisko,
                "Wydział": wydzial,
                "Zmiana": zmiana,
                "Status": status,
                "Maszyna/Urządzenie": maszyna,
                "Urlop od-do": vacation_info,
                "L4 od-do": l4_info
            })
        
        if not export_data:
            return pd.DataFrame(columns=["ID", "Imię", "Nazwisko", "Stanowisko", "Wydział", "Zmiana", "Status", "Maszyna/Urządzenie", "Urlop od-do", "L4 od-do"])
            
        df = pd.DataFrame(export_data)
        return df

    # --- Generowanie Excel ---

    def generate_excel_report(self):
        df = self.get_employee_dataframe()
        if df.empty:
            messagebox.showinfo("Brak Danych", "Brak pracowników do wygenerowania raportu.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")], title="Zapisz Raport Excel")
        
        if file_path:
            try:
                # Używamy pd.ExcelWriter do formatowania kolumn
                writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
                df.to_excel(writer, sheet_name='Pracownicy', index=False)
                
                # Auto-dopasowanie szerokości kolumn
                workbook = writer.book
                worksheet = writer.sheets['Pracownicy']
                
                for i, col in enumerate(df.columns):
                    max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                    worksheet.set_column(i, i, max_len)
                
                writer.close()
                self.emp_manager.log_history("Generowanie Raportu", f"Wygenerowano raport Excel do {file_path}")
                messagebox.showinfo("Sukces", f"Raport Excel został zapisany:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Błąd", f"Błąd podczas generowania raportu Excel: {e}")

    # --- Generowanie PDF ---

    def generate_pdf_report(self):
        df = self.get_employee_dataframe()
        if df.empty:
            messagebox.showinfo("Brak Danych", "Brak pracowników do wygenerowania raportu.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")], title="Zapisz Raport PDF")
        
        if file_path:
            try:
                # Konfiguracja PDF
                c = canvas.Canvas(file_path, pagesize=A4)
                width, height = A4
                styles = getSampleStyleSheet()
                
                # Styl dla polskiej czcionki
                style = ParagraphStyle(
                    'Normal',
                    fontName='Arial',
                    fontSize=10,
                    leading=12,
                )
                style_heading = ParagraphStyle(
                    'Heading',
                    fontName='Arial-Bold',
                    fontSize=12,
                    leading=14,
                    spaceAfter=6,
                )

                # Nagłówek
                c.setFont('Arial-Bold', 14)
                c.drawString(30, height - 30, "Raport Obsady Pracowników")
                
                # Dane tabeli
                table_data = [list(df.columns)] + df.values.tolist()
                
                x_start = 30
                y_pos = height - 70
                col_widths = [30, 80, 80, 80, 80, 80, 80, 80, 80, 80] # Uproszczone szerokości (do dopasowania)

                # Generowanie tabeli (uproszczone, bez biblioteki Table)
                
                # Funkcja rysująca wiersz danych
                def draw_row(row_data, y, is_header=False):
                    c.setFont('Arial-Bold' if is_header else 'Arial', 8 if is_header else 7)
                    for i, (cell, col_w) in enumerate(zip(row_data, col_widths)):
                        c.drawString(x_start + sum(col_widths[:i]) + 2, y, str(cell))
                        # Rysowanie linii kolumn
                        c.line(x_start + sum(col_widths[:i]), y - 10, x_start + sum(col_widths[:i]), y + 2)
                    # Rysowanie linii wiersza
                    c.line(x_start, y - 10, x_start + sum(col_widths), y - 10)

                # Rysowanie nagłówka tabeli
                draw_row(table_data[0], y_pos, is_header=True)
                y_pos -= 12
                
                # Rysowanie danych
                for row in table_data[1:]:
                    if y_pos < 50:
                        c.showPage() # Nowa strona
                        y_pos = height - 30
                        draw_row(table_data[0], y_pos, is_header=True) # Powtórzenie nagłówka na nowej stronie
                        y_pos -= 12

                    draw_row(row, y_pos, is_header=False)
                    y_pos -= 12

                c.save()
                self.emp_manager.log_history("Generowanie Raportu", f"Wygenerowano raport PDF do {file_path}")
                messagebox.showinfo("Sukces", f"Raport PDF został zapisany:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Błąd", f"Błąd podczas generowania raportu PDF. Sprawdź, czy masz pliki czcionek 'arial.ttf' i 'arialbd.ttf'. Szczegóły: {e}")
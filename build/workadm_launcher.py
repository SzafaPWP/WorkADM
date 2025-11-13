import sys
import subprocess
from pathlib import Path
import shutil

def find_pythonw():
    py = Path(sys.executable)
    pythonw = py.parent / "pythonw.exe"
    if pythonw.exists():
        return str(pythonw)
    pythonw_path = shutil.which("pythonw")
    if pythonw_path:
        return pythonw_path
    return None

def main():
    prog_dir = Path(r"C:\Users\SZAFA\Desktop\WorkADM\nowyprojekt\testowy")
    main_py = prog_dir / "main_window.py"

    if not main_py.exists():
        print(f"ERROR: Nie znaleziono pliku: {main_py}")
        input("Naciśnij ENTER aby zamknąć...")
        return

    pythonw = find_pythonw()

    try:
        if pythonw:
            subprocess.Popen([pythonw, str(main_py)], cwd=str(prog_dir))
        else:
            subprocess.Popen(["cmd", "/c", "start", "", "python", str(main_py)], cwd=str(prog_dir), shell=False)
    except Exception as e:
        print("Błąd uruchamiania:", e)
        input("Naciśnij ENTER aby zamknąć...")

if __name__ == "__main__":
    main()

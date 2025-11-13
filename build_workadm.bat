@echo off
REM Upewnij się, że masz zainstalowany PyInstaller (pip install pyinstaller)
REM Uruchom ten skrypt z folderu, gdzie jest workadm_launcher.py

REM Ścieżka do ikony (zmień jeśli ikona jest w innym miejscu)
set ICON=WorkADM.ico

pyinstaller --onefile --noconsole --name WorkADM --icon "%ICON%" workadm_launcher.py

echo.
echo BUILD FINISHED. Sprawdź folder "dist".
pause

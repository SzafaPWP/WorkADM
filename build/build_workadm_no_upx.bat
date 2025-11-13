@echo off
REM Build WorkADM launcher EXE using PyInstaller without UPX (helps avoid anti-virus issues)
REM Place WorkADM.ico in the same folder as this script before running.
REM Requires pyinstaller installed: pip install pyinstaller

pyinstaller --onefile --noconsole --clean --noupx --name WorkADM --icon "WorkADM.ico" workadm_launcher.py

echo.
echo BUILD FINISHED (no UPX). Check the "dist" folder for WorkADM.exe
pause

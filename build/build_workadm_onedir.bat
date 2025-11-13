@echo off
REM Build WorkADM launcher in onedir mode (easiest for distribution)
pyinstaller --onedir --console --clean --name WorkADM --icon "WorkADM.ico" workadm_launcher.py
echo Build finished. Check dist\WorkADM
pause

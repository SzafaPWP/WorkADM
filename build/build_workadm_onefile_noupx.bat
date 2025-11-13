@echo off
REM Build WorkADM launcher as onefile without UPX to avoid AV extraction issues
pyinstaller --onefile --noconsole --clean --noupx --name WorkADM --icon "WorkADM.ico" workadm_launcher.py
echo Build finished. Check dist\WorkADM.exe
pause

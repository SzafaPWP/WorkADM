@echo off
setlocal enabledelayedexpansion

REM Pobierz aktualną datę w formacie RRRR-MM-DD
for /f "tokens=2-4 delims=. " %%a in ('date /t') do (
    set today=%%c-%%b-%%a
)

REM Pobierz aktualną godzinę w formacie HH:MM
for /f "tokens=1-2 delims=: " %%a in ('time /t') do (
    set godzina=%%a:%%b
)

git add .
git commit -m "Auto: !today! !godzina!"
git push
pause
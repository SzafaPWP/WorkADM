; NSIS script for WorkADM installer
; Place WorkADM.exe (from dist\WorkADM or dist\WorkADM.exe) and LICENSE.txt next to this script before running makensis.

Name "WorkADM"
OutFile "WorkADM_Installer.exe"
InstallDir "$PROGRAMFILES\\WorkADM"
SetCompress off

Page license "LICENSE.txt"
Page directory
Page instfiles

Section "Install"
  SetOutPath "$INSTDIR"
  ; copy WorkADM.exe - if using onedir, user should place WorkADM.exe here
  File /r "dist\\WorkADM\\*.*"
  ; if onefile built, make sure WorkADM.exe is placed in this folder and uncomment below
  ; File "dist\\WorkADM.exe"
  CreateShortCut "$DESKTOP\\WorkADM.lnk" "$INSTDIR\\WorkADM.exe"
  CreateShortCut "$SMPROGRAMS\\WorkADM\\WorkADM.lnk" "$INSTDIR\\WorkADM.exe"
SectionEnd

README - WorkADM installer package
---------------------------------
1. Put your built WorkADM executable in the "dist" folder:
   - If you used --onedir: put the "WorkADM" folder (content created by PyInstaller) in the dist folder here.
   - If you used --onefile: put WorkADM.exe into dist folder.

2. Make sure LICENSE.txt is present (already included).
3. Install NSIS (https://nsis.sourceforge.io/Download) and run build_installer.bat to create the installer.
4. The generated installer will install files to C:\Program Files\WorkADM and create shortcuts.

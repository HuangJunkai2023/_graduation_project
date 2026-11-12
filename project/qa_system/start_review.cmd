@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_windows.ps1" -Review
if errorlevel 1 pause

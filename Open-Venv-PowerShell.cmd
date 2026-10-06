@echo off
set "PROJ=C:\Users\boiss\Desktop\Données distribuées\seance-02\TP_jour2"
set "ACT=%PROJ%\.venv\Scripts\Activate.ps1"
REM Ouvre une nouvelle fenêtre PowerShell, se place dans le dossier du projet et active le venv
powershell -NoExit -ExecutionPolicy Bypass -Command "Set-Location -Path '%PROJ%'; . '%ACT%'"


@echo off
set "APP_NAME=app.py"

rem Buscar y detener el proceso de app.py
for /f "tokens=2" %%a in ('tasklist /fi "imagename eq python.exe" /v ^| findstr /i %APP_NAME%') do (
    taskkill /pid %%a /f
)

rem Mostrar mensaje de confirmación al usuario
powershell -command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('Asignador apagado')"

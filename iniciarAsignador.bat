
@echo off
set "VENV_PATH=AsignadorClustersEnv\bin\activate"
set "APP_PATH=app.py"

rem Activar el entorno virtual
if exist %VENV_PATH% (
    call %VENV_PATH%
) else (
    echo No se encontró el entorno virtual. Asegúrate de que esté en la carpeta AsignadorClustersEnv.
    pause
    exit /b
)

rem Iniciar el archivo app.py en segundo plano
start "" python %APP_PATH%

rem Mostrar mensaje de confirmación al usuario
powershell -command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('Asignador iniciado')"

rem Cerrar la ventana de la terminal sin terminar app.py
exit

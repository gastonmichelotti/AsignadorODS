 @echo off
echo Activando el entorno virtual...
call AsignadorClusters\EnvScripts\activate

echo Instalando dependencias...
pip install -r requirements.txt

echo Iniciando la aplicación Flask...
start "Aplicación Flask" python app.py

echo La aplicación se ha iniciado. Puedes acceder a ella en http://localhost:5005
echo Para detener la aplicación, cierra esta ventana.
pause
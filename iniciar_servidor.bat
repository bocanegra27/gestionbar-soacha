@echo off
echo Activando entorno virtual...
call venv\Scripts\activate

echo Iniciando servidor en http://192.168.1.37:8000
echo NO CIERRES ESTA VENTANA.

waitress-serve --host=0.0.0.0 --port=8000 gestion_bar.wsgi:application
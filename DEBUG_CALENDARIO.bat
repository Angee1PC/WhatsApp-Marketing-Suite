@echo off
echo --- DIAGNOSTICO DE CALENDARIO ---
echo Ejecutando script de sincronizacion...
python sync_calendar.py
echo.
echo ------------------------------------------
echo Si ves un error arriba, probablemente falta el archivo credentials.json
echo o no has instalado las librerias.
echo.
pause

#!/bin/bash
cd "$(dirname "$0")"
echo "Instalando dependencias..."
pip3 install -r requirements.txt
echo "Dependencias instaladas. Iniciando..."
python3 app_gui.py

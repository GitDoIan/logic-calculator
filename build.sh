#!/bin/bash
# Gera um executável único da Calculadora Lógica (sem precisar de Python instalado na máquina de destino).
# Usa um ambiente virtual isolado em .venv/ para não mexer no Python global do sistema.
set -e
cd "$(dirname "$0")"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
./.venv/bin/pip install --quiet --upgrade pip pyinstaller
./.venv/bin/python -m PyInstaller --onefile --windowed --noconfirm --name "CalculadoraLogica" main.py
echo ""
echo "Pronto! Executável em: dist/CalculadoraLogica"

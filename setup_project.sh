#!/bin/bash

echo "Criando a estrutura do projeto Max-Finder..."

# Criar arquivos na raiz do projeto
echo "Criando arquivos na raiz..."
touch .gitignore
touch README.md
touch requirements.txt
touch main.py


# Criar pasta principal da aplicação e seus arquivos
echo "Criando maxfinder_app/ e seus arquivos..."
mkdir -p maxfinder_app
touch maxfinder_app/__init__.py
touch maxfinder_app/api_handler.py

# Criar subpasta da GUI e seus arquivos
echo "Criando maxfinder_app/gui/ e seus arquivos..."
mkdir -p maxfinder_app/gui
touch maxfinder_app/gui/__init__.py
touch maxfinder_app/gui/main_window.py

# Criar subpasta de assets dentro da GUI e um arquivo de exemplo
echo "Criando maxfinder_app/gui/assets/..."
mkdir -p maxfinder_app/gui/assets
touch maxfinder_app/gui/assets/icon.png # Arquivo de ícone de exemplo

echo ""
echo "Estrutura do projeto criada com sucesso!"
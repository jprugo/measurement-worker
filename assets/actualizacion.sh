#!/bin/bash

# Eliminar directorios si existen
rm -rf ~/Documentos/measurement-worker
rm -rf ~/Documentos/measurement-front

# Clonar los repositorios
git clone https://github.com/jprugo/measurement-worker.git
git clone https://github.com/jprugo/measurement-front.git

cd ~/Documentos/measurement-worker || { echo "Directorio 'app' no encontrado"; exit 1; }
git switch feature/ddd-test

# Instalar dependencias
pip install -r requirements.txt

cd ~/Documentos/measurement-front || { echo "Directorio 'app' no encontrado"; exit 1; }
git switch feat/julian
git pull origin feat/julian

cp -r ~/Documentos/measurement-worker/* /var/www/html

sudo systemctl restart apache2

echo "Proceso completado exitosamente"

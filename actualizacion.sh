#!/bin/bash

# Cambiar al directorio 'documentos'
cd ~/Documentos || { echo "Directorio 'documentos' no encontrado"; exit ;}

# Eliminar directorios si existen
rm -rf measurement-api
rm -rf measurement-worker
rm -rf app

# Clonar los repositorios
git clone https://github.com/jprugo/measurement-api.git
git clone https://github.com/jprugo/measurement-worker.git
git clone https://github.com/jprugo/app.git

# Instalar dependencias
pip install -r measurement-api/requirements.txt
pip install -r measurement-worker/requirements.txt

# Cambiar al directorio 'app' y cambiar a la rama HOTFIX
cd app || { echo "Directorio 'app' no encontrado"; exit 1; }
git switch HOTFIX

# Copiar el contenido de 'app' a '/var/www/html'
cp -r * /var/www/html

echo "Proceso completado exitosamente"

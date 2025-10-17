#!/bin/bash

# --- Script para configurar y ejecutar la aplicación Gestión de Viviendas ---

echo "--- [Paso 1/5] Creando entorno virtual 'venv'... ---"
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: No se pudo crear el entorno virtual. Asegúrate de que 'python3' y 'venv' están instalados."
    exit 1
fi

echo "--- [Paso 2/5] Activando entorno virtual e instalando dependencias... ---"
source venv/bin/activate
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: No se pudieron instalar las dependencias desde requirements.txt."
    exit 1
fi

echo "--- [Paso 3/5] Aplicando migraciones a la base de datos... ---"
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "ERROR: No se pudieron aplicar las migraciones."
    exit 1
fi

echo "--- [Paso 4/5] Creando superusuario por defecto (admin/admin)... ---"
# Creamos el superusuario de forma no interactiva y establecemos su contraseña.
# Esto evita que el script se detenga a pedir datos.
python manage.py createsuperuser --username admin --email admin@example.com --noinput
python -c "from django.contrib.auth import get_user_model; User = get_user_model(); u = User.objects.get(username='admin'); u.set_password('admin'); u.save()"
if [ $? -ne 0 ]; then
    echo "ADVERTENCIA: No se pudo crear o actualizar el superusuario. Puede que ya exista."
fi

echo "--- [Paso 5/5] Iniciando servidor de desarrollo... ---"
echo "La aplicación estará disponible en: http://127.0.0.1:8000/"
echo "El panel de administración estará en: http://127.0.0.1:8000/admin/"
echo "Puedes detener el servidor en cualquier momento con CTRL+C."
python manage.py runserver
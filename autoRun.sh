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

echo "--- [Paso 4/5] Creando superusuario por defecto (admin/1234)... ---"
# Definimos las variables de entorno para la creación no interactiva del superusuario.
export DJANGO_SUPERUSER_USERNAME=admin
export DJANGO_SUPERUSER_EMAIL=prueba@prueba.com
export DJANGO_SUPERUSER_PASSWORD=1234
python manage.py createsuperuser --noinput
if [ $? -ne 0 ]; then
    # Si el usuario ya existe, solo actualizamos su contraseña.
    echo "El superusuario 'admin' ya existe. Actualizando contraseña..."
    python -c "from django.contrib.auth import get_user_model; User = get_user_model(); u = User.objects.get(username='admin'); u.set_password('$DJANGO_SUPERUSER_PASSWORD'); u.save()"
fi
# Limpiamos las variables de entorno
unset DJANGO_SUPERUSER_USERNAME
unset DJANGO_SUPERUSER_EMAIL
unset DJANGO_SUPERUSER_PASSWORD

echo "--- [Paso 5/5] Iniciando servidor de desarrollo... ---"
echo "La aplicación estará disponible en: http://127.0.0.1:8000/"
echo "El panel de administración estará en: http://127.0.0.1:8000/admin/"
echo "Puedes detener el servidor en cualquier momento con CTRL+C."
python manage.py runserver
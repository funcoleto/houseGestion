# 🏡 Gestión de Viviendas

Aplicación web para la gestión integral de propiedades de alquiler. Este proyecto está siendo desarrollado para facilitar a los administradores todo el ciclo de vida del alquiler, desde la captación de inquilinos hasta la finalización del contrato.

---

## ✨ Características Actuales (Fase 1)

*   **Proyecto Django Inicializado**: Base del proyecto creada con una estructura robusta y escalable.
*   **Modelos de Datos**:
    *   `Vivienda`: Para almacenar toda la información de la propiedad (dirección, referencia catastral, precio, etc.).
    *   `Administrador`: Para gestionar los administradores de las viviendas.
    *   `HorarioVisita`: Para definir los horarios de visita disponibles para cada vivienda.
*   **Panel de Administración**: Interfaz de administración de Django configurada para gestionar viviendas, administradores y horarios de forma sencilla.
*   **Base de Datos**: Configuración inicial con SQLite, lista para desarrollo.

---

## 🚀 Cómo Empezar

Sigue estos pasos para poner en marcha el proyecto en tu entorno local.

### 1. Prerrequisitos

Asegúrate de tener instalados los siguientes programas:
*   [Python 3.10+](https://www.python.org/downloads/)
*   `pip` (generalmente viene con Python)

### 2. Instalación y Configuración

1.  **Clona el repositorio:**
    ```bash
    git clone <URL-DEL-REPOSITORIO>
    cd gestion-de-viviendas
    ```

2.  **Crea y activa un entorno virtual (recomendado):**
    ```bash
    # Para Unix/macOS
    python3 -m venv venv
    source venv/bin/activate

    # Para Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Instala las dependencias:**
    Por ahora, solo necesitas Django. Puedes instalarlo con el siguiente comando (más adelante crearemos un fichero `requirements.txt`):
    ```bash
    pip install django
    ```

4.  **Aplica las migraciones de la base de datos:**
    Este comando creará el fichero de base de datos `db.sqlite3` y las tablas necesarias.
    ```bash
    python manage.py migrate
    ```

5.  **Crea un superusuario:**
    Para acceder al panel de administración, necesitas un usuario con privilegios.
    ```bash
    python manage.py createsuperuser
    ```
    Sigue las instrucciones para crear tu nombre de usuario, email y contraseña.

### 3. Ejecutar el Servidor de Desarrollo

Una vez completada la configuración, inicia el servidor de desarrollo de Django:
```bash
python manage.py runserver
```
La aplicación estará disponible en `http://127.0.0.1:8000/`.

---

## 🔑 Acceder al Panel de Administración

1.  Con el servidor en marcha, abre tu navegador y ve a:
    **[http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)**

2.  Inicia sesión con las credenciales del superusuario que creaste en el paso anterior.

¡Y listo! Desde aquí puedes empezar a añadir administradores y viviendas.
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

---

## 📋 Proceso 1: Flujo del Arrendatario

Esta sección describe cómo probar el flujo de solicitud de visitas implementado.

### 1. Prepara los datos en el Panel de Administración

1.  **Accede al panel de administración:**
    [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

2.  **Crea una `Vivienda`:**
    *   Ve a la sección "Viviendas" y añade una nueva. Rellena los datos que desees.

3.  **Añade tu número de teléfono a la vivienda:**
    *   Dentro de la vivienda que acabas de crear, busca la sección "Arrendatarios Autorizados".
    *   Añade tu número de teléfono **con prefijo internacional** (ej. `+34666666666`).

4.  **Define los horarios de visita:**
    *   En la misma página de la vivienda, busca la sección "Horarios".
    *   Añade una o más franjas horarias con una **fecha futura** y horas de inicio y fin.

### 2. Prueba el Flujo como Arrendatario

1.  **Accede a la página de verificación:**
    Abre una nueva pestaña (preferiblemente en modo incógnito para tener una sesión limpia) y ve a:
    [http://127.0.0.1:8000/acceso-arrendatario/](http://127.0.0.1:8000/acceso-arrendatario/)

2.  **Introduce tu teléfono:**
    Escribe el mismo número de teléfono que autorizaste en el paso anterior.

3.  **Rellena el formulario de visita:**
    *   Si el teléfono es correcto, serás redirigido al formulario para agendar la visita.
    *   El desplegable "Selecciona un horario de visita" debería mostrarte los huecos disponibles calculados a partir de las franjas que definiste.
    *   Rellena el resto de campos y haz clic en "Confirmar Visita".

4.  **Confirma y Cancela (Opcional):**
    *   Serás redirigido a una página de confirmación.
    *   En la consola donde ejecutaste `runserver`, verás un mensaje simulando el email de confirmación, que incluye un **enlace de cancelación**.
    *   Copia y pega ese enlace en tu navegador para probar el flujo de cancelación.

### 3. Verifica los resultados en el Panel de Administración

*   Vuelve al panel de administración y ve a la sección "Visitas".
*   Verás la nueva visita que has creado, con su estado ("CONFIRMADA" o "CANCELADA").

---

## ⚙️ Configuración del Envío de Correos (Opcional)

Por defecto, la aplicación está configurada para mostrar los correos electrónicos en la consola donde ejecutas `runserver`. Esto es ideal para el desarrollo.

Si quieres que la aplicación envíe correos reales a través de un servidor SMTP (como Gmail), sigue estos pasos:

1.  **Modifica `gestion_viviendas/settings.py`:**
    *   **Comenta** la línea `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'`.
    *   **Descomenta** las líneas de configuración de `EMAIL_BACKEND` para SMTP.

2.  **Configura las Variables de Entorno:**
    Necesitarás crear un fichero `.env` en la raíz del proyecto para almacenar tus credenciales de forma segura.

    *   **Crea el fichero `.env`:**
        ```
        touch .env
        ```

    *   **Añade las siguientes variables a tu fichero `.env`** (reemplaza los valores con los tuyos):
        ```
        # Ejemplo para Gmail
        EMAIL_HOST=smtp.gmail.com
        EMAIL_PORT=587
        EMAIL_USE_TLS=True
        EMAIL_HOST_USER=tu-correo@gmail.com
        EMAIL_HOST_PASSWORD=tu-contraseña-de-aplicacion
        ```
        **Importante para Gmail:** No uses tu contraseña normal. Debes generar una "Contraseña de aplicación" desde la configuración de seguridad de tu cuenta de Google.

3.  **Instala `python-dotenv`:**
    Para que Django pueda leer el fichero `.env`, necesitas instalar una librería adicional:
    ```bash
    pip install python-dotenv
    ```

4.  **Modifica `manage.py` y `gestion_viviendas/wsgi.py`:**
    Añade las siguientes líneas al principio de ambos ficheros para que carguen las variables de entorno al iniciar la aplicación:
    ```python
    from dotenv import load_dotenv
    load_dotenv()
    ```

¡Y listo! La próxima vez que inicies el servidor, la aplicación intentará enviar correos usando las credenciales que has configurado.
# 🏡 Gestión de Viviendas (houseGestion)

Aplicación web para la gestión integral de propiedades de alquiler. Este proyecto está siendo desarrollado para facilitar a los administradores todo el ciclo de vida del alquiler.

---

## 🚀 Cómo Empezar

### 1. Prerrequisitos

Asegúrate de tener instalados los siguientes programas:
*   [Python 3.10+](https://www.python.org/downloads/)
*   `git`

### 2. Instalación y Ejecución Automática

Hemos creado un script que automatiza todo el proceso de instalación y ejecución.

1.  **Clona el repositorio:**
    ```bash
    git clone <URL-DEL-REPOSITORIO>
    cd houseGestion
    ```

2.  **Ejecuta el script de instalación:**
    ```bash
    ./autoRun.sh
    ```

El script se encargará de:
*   Crear un entorno virtual (`venv`).
*   Instalar todas las dependencias desde `requirements.txt`.
*   Configurar la base de datos (aplicar migraciones).
*   Crear un superusuario por defecto (`usuario: admin`, `contraseña: 1234`).
*   Iniciar el servidor de desarrollo.

Una vez que el script termine, la aplicación estará disponible en `http://127.0.0.1:8000/`.

---

## 🔑 Acceso al Panel de Administración

1.  Con el servidor en marcha, abre tu navegador y ve a:
    **[http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)**

2.  Inicia sesión con las credenciales del superusuario (`admin`/`1234`).

---

## 📋 Flujos de Trabajo y Pruebas

### Proceso 1: Solicitud de Visita por el Arrendatario

1.  **Prepara los datos en el Panel de Administración:**
    *   Crea una o más `Viviendas`.
    *   Para cada vivienda, añade tu número de teléfono en la sección "Arrendatarios Autorizados" (con prefijo internacional, ej: `+34...`).
    *   Añade `Horarios de Visita` con fechas futuras para las viviendas.

2.  **Prueba el Flujo como Arrendatario:**
    *   Ve a [http://127.0.0.1:8000/acceso-arrendatario/](http://127.0.0.1:8000/acceso-arrendatario/).
    *   Introduce tu teléfono.
    *   **Si tienes acceso a más de una vivienda**, serás redirigido a una página para seleccionar a cuál quieres pedir cita. Verás un botón "Solicitar Visita" para las disponibles y "Gestionar Visita" para las que ya tengas una cita confirmada.
    *   **Si ya tienes una cita**, puedes gestionarla (modificarla o cancelarla). Al modificar, el formulario se precargará con tus datos.
    *   Rellena el formulario de visita. El sistema solo mostrará los horarios realmente libres.
    *   Tras confirmar, recibirás un email (en la consola) con un resumen completo de tus datos y un botón para gestionar tu visita.

### Proceso 2: Solicitud de Documentación al Candidato

1.  **Selecciona al Candidato desde el Panel de Administración:**
    *   Asegúrate de que tienes al menos una visita creada siguiendo el Proceso 1.
    *   Ve a la sección "Visitas" en el panel de administración.
    *   Selecciona la casilla de la visita del candidato que quieres elegir.
    *   En el menú de "Acciones" en la parte superior, selecciona **"Enviar enlace para subir documentación"** y haz clic en "Ir".

2.  **El Arrendatario Recibe el Email:**
    *   El sistema enviará un email (visible en la consola) al arrendatario con un enlace único y seguro para subir su documentación.

3.  **Prueba la Subida de Documentos:**
    *   Copia y pega el enlace del email en tu navegador.
    *   Llegarás a una página que te pedirá subir los documentos necesarios (DNI, nóminas, etc.).
    *   Puedes usar el botón **"Añadir otro inquilino"** para añadir más formularios dinámicamente.
    *   Al enviar, los ficheros se guardarán y la solicitud se marcará como "Completada".

4.  **Verifica en el Panel de Administración:**
    *   Ve a la sección "Solicitudes de Documentación". Verás la nueva solicitud con el estado "Completada".

---

## ⚙️ Configuración del Envío de Correos (Opcional)

Por defecto, los correos se muestran en la consola. Para enviar correos reales (ej. con Gmail):

1.  **Modifica `gestion_viviendas/settings.py`:**
    *   Comenta la línea de `EMAIL_BACKEND` para la consola.
    *   Descomenta las líneas de configuración para SMTP.

2.  **Crea un fichero `.env`** en la raíz del proyecto con tus credenciales:
    ```
    EMAIL_HOST=smtp.gmail.com
    EMAIL_PORT=587
    EMAIL_USE_TLS=True
    EMAIL_HOST_USER=tu-correo@gmail.com
    EMAIL_HOST_PASSWORD=tu-contraseña-de-aplicacion
    ```
    **Importante:** Para Gmail, necesitas una "Contraseña de aplicación".

3.  El fichero `autoRun.sh` ya instala `python-dotenv` y los ficheros de Django están configurados para leer `.env`, así que no necesitas hacer nada más.
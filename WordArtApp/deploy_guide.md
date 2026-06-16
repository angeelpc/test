# Guía de Despliegue para WordArt Studio

Esta guía describe paso a paso cómo montar tu aplicación web **WordArt Studio** (Flask) en internet de forma pública.

---

## 1. Requisitos Previos

Para desplegar la aplicación en la mayoría de los servidores en la nube, necesitas:
1.  **Código en GitHub:** Sube tu carpeta `WordArtApp` a un repositorio público o privado en tu cuenta de GitHub.
2.  **Archivo de dependencias:** Asegúrate de tener el archivo [requirements.txt](file:///d:/Python%20Projects/WordArtApp/requirements.txt) en la raíz de tu proyecto. Este archivo ya fue creado con el siguiente contenido:
    ```text
    Flask>=3.0.0
    Pillow>=10.0.0
    gunicorn>=21.0.0
    ```

---

## 2. Opción A: Despliegue en Render (Recomendado y Gratis)

[Render](https://render.com) es una de las plataformas más fáciles y populares para hospedar aplicaciones Flask gratis.

### Pasos:
1.  **Crea una cuenta:** Regístrate en [Render](https://render.com) (puedes usar tu cuenta de GitHub).
2.  **Crea un nuevo servicio web:** Haz clic en **New +** y selecciona **Web Service**.
3.  **Conecta tu repositorio:** Enlaza tu cuenta de GitHub y selecciona el repositorio de `WordArtApp`.
4.  **Configura los detalles del despliegue:**
    *   **Name:** `wordart-studio` (o el nombre que prefieras).
    *   **Region:** Selecciona la más cercana (ej. Oregon - US West o Ohio - US East).
    *   **Branch:** `main` (o tu rama principal).
    *   **Runtime:** `Python`.
    *   **Build Command:** `pip install -r requirements.txt`
    *   **Start Command:** `gunicorn app:app`
5.  **Elige el plan:** Selecciona el plan **Free** (Gratuito).
6.  **Desplegar:** Haz clic en **Create Web Service**. Render comenzará a compilar e instalar las dependencias automáticamente. En unos minutos te dará una URL pública tipo `https://wordart-studio.onrender.com`.

---

## 3. Opción B: Despliegue en PythonAnywhere (Especializado en Python)

[PythonAnywhere](https://www.pythonanywhere.com) está optimizado específicamente para alojar Flask y Django de forma gratuita o de pago.

### Pasos:
1.  Crea una cuenta gratuita en [PythonAnywhere](https://www.pythonanywhere.com).
2.  Ve a la sección de **Consoles** y abre una consola de **Bash**.
3.  Clona tu repositorio: `git clone <URL_DE_TU_REPOSITORIO>`.
4.  Ve a la pestaña **Web** y haz clic en **Add a new web app**.
5.  Selecciona **Manual Configuration** y elige la versión de Python que estás utilizando (ej. Python 3.10 o 3.11).
6.  En la configuración de la Web App:
    *   Configura el **Source code path** apuntando a tu directorio clonado (ej. `/home/tuusuario/WordArtApp`).
    *   Crea un entorno virtual e instala los paquetes:
        ```bash
        mkvirtualenv myenv --python=python3.10
        pip install -r requirements.txt
        ```
    *   Configura la ruta de tu **Virtualenv** en la interfaz web (ej. `/home/tuusuario/.virtualenvs/myenv`).
7.  Edita el archivo de configuración **WSGI** (el enlace está en la misma pestaña Web) y configúralo para cargar tu app Flask:
    ```python
    import sys
    path = '/home/tuusuario/WordArtApp'
    if path not in sys.path:
        sys.path.append(path)
    from app import app as application
    ```
8.  Haz clic en **Reload** en la pestaña Web y tu app estará en línea en `http://tuusuario.pythonanywhere.com`.

---

## 4. Opción C: Despliegue en un VPS Propio (AWS, DigitalOcean)

Si tienes un servidor virtual privado (VPS) con Linux (Ubuntu):
1.  **Configura Gunicorn:** Usa `gunicorn --workers 3 --bind 127.0.0.1:5000 app:app` para correr el backend en segundo plano.
2.  **Configura Nginx como Proxy Inverso:** Redirecciona el puerto 80 (HTTP) y 443 (HTTPS) al puerto local 5000 donde corre Gunicorn.
    ```nginx
    server {
        listen 80;
        server_name tusitio.com;

        location / {
            proxy_pass http://127.0.0.1:5000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
    ```
3.  **SSL:** Instala un certificado de seguridad gratuito usando `Certbot` (Let's Encrypt).

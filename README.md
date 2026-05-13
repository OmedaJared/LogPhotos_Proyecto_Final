<img width="250" height="250" alt="image" src="https://github.com/user-attachments/assets/c0d03a49-ac75-427a-b40d-f951669b60ee" />

Sistema de Autenticación

Este proyecto es un sistema básico de inicio de sesión, registro y recuperación de contraseña usando Flask y MongoDB Atlas.

## Para qué sirve cada librería

- `flask`
  - Framework principal para crear la aplicación web.
  - Maneja rutas, renderizado de plantillas y servidor local.

- `flask-login`
  - Administra el inicio de sesión de usuarios.
  - Controla sesiones, protección de rutas y estados de usuario autenticado.

- `flask-wtf`
  - Proporciona integración de formularios con Flask.
  - Maneja validación de formularios y protección CSRF.

- `wtforms`
  - Define los campos de formulario y las reglas de validación.
  - Se usa para crear los formularios de login, registro y reset.

- `pymongo`
  - Conecta la aplicación a MongoDB.
  - Permite leer y escribir datos de usuarios en la base de datos.

- `bcrypt`
  - Encripta las contraseñas antes de guardarlas en la base de datos.
  - Verifica contraseñas de forma segura.

- `flask-mail`
  - Envía correos electrónicos desde Flask.
  - Se usa para enviar enlaces de recuperación de contraseña.

- `python-dotenv`
  - Carga variables de entorno desde el archivo `.env`.
  - Permite mantener claves y configuraciones fuera del código.

- `dnspython`
  - Dependencia de `pymongo` para resolver URIs `mongodb+srv`.

## Explicación de `app.py`

### Configuración inicial

- `load_dotenv()`
  - Carga las variables del archivo `.env`.

- `app = Flask(__name__)`
  - Crea la aplicación Flask.

- `app.config[...]`
  - Configura la clave secreta, correo y otros ajustes.

### Configuración de `Mail` y `LoginManager`

- `mail = Mail(app)`
  - Inicializa el envío de correos.

- `login_manager = LoginManager()`
  - Configura la lógica de login.

- `login_manager.login_view = 'login'`
  - Define la página de redirección cuando el usuario no está autenticado.

### Conexión a MongoDB

- `mongo_uri = os.getenv('MONGO_URI')`
  - Lee la cadena de conexión desde `.env`.

- `MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)`
  - Intenta conectarse a MongoDB en 5 segundos.

- `client.admin.command('ping')`
  - Verifica que la conexión esté activa.

- Si el URI es un placeholder, el código usa un fallback local:
  - `mongodb://localhost:27017/trevi3`

- `db = client['trevi3']`
  - Selecciona la base de datos `trevi3`.

- `users_collection = db['users']`
  - Colección para guardar usuarios.

- `reset_tokens_collection = db['reset_tokens']`
  - Colección para guardar tokens de recuperación.

### Clase `User`

- `class User(UserMixin):`
  - Define el usuario que usa Flask-Login.

- `self.id = str(user_data['_id'])`
  - Usa el `_id` de MongoDB como identificador.

- `self.email = user_data['email']`
  - Guarda el email para mostrarlo y verificarlo.

### Función `load_user`

- `@login_manager.user_loader`
  - Carga el usuario desde la sesión.

- Busca el usuario en MongoDB por `_id`.

### Formularios

- `LoginForm`
  - Campos: `email`, `password`, `submit`.
  - Valida que el email y la contraseña existan.

- `RegisterForm`
  - Campos: `email`, `password`, `confirm_password`, `submit`.
  - Valida contraseña mínima y coincidencia.

- `ResetForm`
  - Campo: `email`.
  - Envía la solicitud de recuperación.

- `ResetPasswordForm`
  - Campos: `password`, `confirm_password`, `submit`.
  - Permite establecer nueva contraseña.

### Rutas

- `/` - `home()`
  - Ruta protegida con `@login_required`.
  - Muestra la página principal después de iniciar sesión.

- `/login` - `login()`
  - Muestra el formulario de login.
  - Si los datos son correctos, autentica y redirige a `/`.
  - Usa `checkpw()` de `bcrypt` para verificar la contraseña.

- `/register` - `register()`
  - Muestra formulario de registro.
  - Verifica que el email no exista.
  - Hashea la contraseña con `hashpw()` y la guarda en MongoDB.

- `/reset` - `reset()`
  - Muestra el formulario de recuperación.
  - Si el email existe, crea un token único.
  - Envía un correo con el enlace de recuperación.

- `/reset/<token>` - `reset_password(token)`
  - Verifica que el token exista.
  - Permite guardar la nueva contraseña.
  - Borra el token después de usarlo.

- `/logout` - `logout()`
  - Cierra la sesión del usuario.
  - Redirige a la página de login.

## Archivos de plantillas

- `templates/base.html`
  - Plantilla base común para todas las páginas.

- `templates/login.html`
  - Formulario de inicio de sesión.

- `templates/register.html`
  - Formulario de registro de usuario.

- `templates/reset.html`
  - Formulario para pedir el enlace de recuperación.

- `templates/reset_password.html`
  - Formulario para escribir la nueva contraseña.

- `templates/home.html`
  - Página principal para usuarios autenticados.

## Cómo ejecutar

1. Abre la terminal en la carpeta del proyecto.
2. Activa el entorno virtual:
   - `& ".venv\Scripts\Activate.ps1"`
3. Ejecuta la aplicación:
   - `uv run flask run`
4. Abre `http://127.0.0.1:5000/` en el navegador.

## Variables de entorno necesarias

- `MONGO_URI` - Cadena de conexión de MongoDB Atlas.
- `SECRET_KEY` - Clave secreta para Flask.
- `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USE_TLS`, `MAIL_USERNAME`, `MAIL_PASSWORD` - Configuración de correo.

---

Si necesitas, también puedo agregar una sección de ejemplo con la sintaxis exacta para el URI de MongoDB Atlas y la configuración de Gmail.

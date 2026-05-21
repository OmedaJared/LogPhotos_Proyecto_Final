# photo-app

`photo-app` es un proyecto Python con configuración moderna basada en `pyproject.toml`.  
En su estado actual, el código fuente principal contiene un punto de entrada mínimo (`main.py`) que imprime un mensaje en consola, pero ya incluye dependencias orientadas a construir una aplicación web con Flask y MongoDB.

---

## Resumen del proyecto

Este repositorio está preparado para una aplicación que, por sus dependencias, apunta a funcionalidades como:

- aplicación web con Flask,
- validación de correos,
- persistencia con MongoDB,
- manejo de archivos,
- seguridad de contraseñas con Werkzeug.

Sin embargo, el archivo `main.py` todavía no implementa la lógica de la app web; por ahora solo sirve como entrada básica.

---

## Tecnologías y librerías instaladas

Las dependencias definidas en `photo_app/pyproject.toml` son las siguientes:

### 1. `flask>=3.1.3`
Framework web principal.

#### Para qué sirve
- Crear rutas HTTP.
- Renderizar vistas.
- Manejar solicitudes `GET`, `POST`, etc.
- Gestionar sesiones, cookies y contexto de petición.
- Construir una aplicación web tradicional o una API.

#### Uso típico en este proyecto
Aunque todavía no se usa en `main.py`, está pensada para:
- formularios de login/registro,
- páginas HTML,
- endpoints para subida de archivos,
- recuperación de contraseña,
- manejo de sesión de usuario.

---

### 2. `pymongo>=4.17.0`
Driver oficial de MongoDB para Python.

#### Para qué sirve
- Conectarse a una base de datos MongoDB.
- Insertar documentos.
- Buscar documentos.
- Actualizar registros.
- Eliminar documentos.

#### Uso típico en este proyecto
Está orientada a guardar información como:
- usuarios,
- archivos subidos,
- tokens de recuperación,
- metadatos de contenido.

---

### 3. `flask-pymongo>=3.0.1`
Integración entre Flask y MongoDB.

#### Para qué sirve
- Simplifica el uso de MongoDB dentro de una app Flask.
- Permite configurar la conexión desde la app Flask de forma más limpia.
- Facilita el acceso a colecciones desde la aplicación.

#### Ventaja
Reduce la cantidad de código de conexión manual frente a usar solo `pymongo`.

---

### 4. `werkzeug>=3.1.8`
Biblioteca base usada por Flask.

#### Para qué sirve
- Seguridad de contraseñas con `generate_password_hash` y `check_password_hash`.
- Utilidades para manejo de peticiones y respuestas.
- Manejo de archivos con `secure_filename`.
- Parte interna de la infraestructura de Flask.

#### Uso típico en este proyecto
Ideal para:
- encriptar contraseñas de usuarios,
- validar contraseñas,
- sanitizar nombres de archivo antes de guardarlos.

---

### 5. `email-validator>=2.3.0`
Librería de validación de direcciones de correo electrónico.

#### Para qué sirve
- Verificar si un email tiene formato válido.
- Evitar guardar direcciones mal escritas.
- Mejorar formularios de registro y recuperación de cuenta.

#### Uso típico en este proyecto
Se usaría en:
- registro de usuario,
- validación de correos antes de enviar emails,
- formularios de contacto o recuperación.

---

## Estructura actual del proyecto

Actualmente los archivos principales son:

```text
photo_app/
├── main.py
├── pyproject.toml
├── README.md
└── uv.lock
```

### `main.py`
Punto de entrada mínimo del proyecto.

### `pyproject.toml`
Archivo de configuración del proyecto y dependencias.

### `README.md`
Documentación del proyecto.

### `uv.lock`
Bloqueo de versiones exactas de dependencias para reproducibilidad.

---

## Archivo `main.py`

Contenido actual:

```python
def main():
    print("Hello from photo-app!")


if __name__ == "__main__":
    main()
```

### Función `main()`

#### Responsabilidad
Es la función principal del programa.

#### Qué hace
- Imprime en consola el texto `Hello from photo-app!`.

#### Observaciones técnicas
- No recibe parámetros.
- No devuelve nada explícitamente.
- Sirve como base para crecer a una app más completa.
- Hoy funciona como demostración de arranque.

---

### Bloque `if __name__ == "__main__":`

#### Responsabilidad
Permite ejecutar `main()` solo cuando el archivo se corre directamente.

#### Qué significa
- Si ejecutas `python main.py`, se llama a `main()`.
- Si importas `main.py` desde otro módulo, no se ejecuta automáticamente.

#### Beneficio
Es la forma estándar en Python para separar:
- ejecución directa del script,
- reutilización como módulo importable.

---

## Funciones y responsabilidades del código actual

Por ahora, el proyecto tiene una sola función propia:

### `main()`
- Punto de inicio.
- Imprime un mensaje simple.
- No depende de otras partes del proyecto.
- Todavía no inicia servidor web, no conecta a base de datos, y no procesa formularios.

---

## Lo que el proyecto ya está preparado para hacer

Aunque el código visible es mínimo, las dependencias muestran una intención clara de crecimiento hacia una app con estas capacidades:

### Autenticación
- registro de usuarios,
- inicio de sesión,
- hash seguro de contraseñas,
- validación de credenciales.

### Base de datos
- guardar usuarios en MongoDB,
- almacenar metadatos,
- persistir estados de recuperación de cuenta.

### Manejo de archivos
- subir archivos,
- validar nombres de archivo,
- asociar archivos a usuarios.

### Validación de formularios
- comprobar emails,
- validar entradas antes de procesarlas.

---

## Flujo esperado de una futura versión del proyecto

Un flujo lógico para esta base podría ser:

1. El usuario abre la aplicación web.
2. Se muestra una pantalla de registro o login.
3. El sistema valida el correo con `email-validator`.
4. La contraseña se guarda con hash usando `werkzeug`.
5. Los datos del usuario se almacenan en MongoDB.
6. El usuario inicia sesión.
7. Se pueden subir archivos y guardar sus metadatos.
8. La app usa Flask para servir rutas y páginas.

---

## Instalación

### Requisitos
- Python 3.13 o superior
- Acceso a MongoDB si se va a implementar la parte de persistencia
- `uv` o `pip` para gestionar dependencias

### Instalar dependencias
Si usas `uv`:

```bash
uv sync
```

Si usas `pip`:

```bash
pip install flask flask-pymongo pymongo werkzeug email-validator
```

---

## Ejecución

Actualmente, el proyecto solo imprime un mensaje desde consola.

### Ejecutar el script actual
```bash
python main.py
```

### Salida esperada
```text
Hello from photo-app!
```

---

## Convenciones y buenas prácticas observables

### Punto de entrada claro
`main.py` usa el patrón estándar de Python para ejecución directa.

### Configuración centralizada de dependencias
Las librerías se definen en `pyproject.toml`, lo que facilita reproducibilidad.

### Preparación para escalar
Las dependencias instaladas sugieren que el proyecto está pensado para evolucionar hacia una aplicación completa con backend web y base de datos.

---

## Estado actual del código

### Implementado
- Archivo principal con función `main()`
- Gestión moderna de dependencias en `pyproject.toml`
- Dependencias listas para una app Flask + MongoDB

### Aún no implementado
- rutas web,
- plantillas HTML,
- conexión real a MongoDB en el código visible,
- autenticación,
- subida de archivos,
- validación de formularios,
- sistema de emails,
- manejo de sesiones web.

---

## Próximos pasos recomendados

Si quieres que el README refleje una app más madura, el siguiente paso sería documentar también:

- estructura real de carpetas de la aplicación,
- rutas y funciones de cada módulo,
- variables de entorno necesarias,
- endpoints disponibles,
- ejemplo de uso de MongoDB,
- flujo de autenticación y recuperación de contraseña.

---

## Licencia

Aún no se ha definido una licencia en el contenido actual del proyecto.

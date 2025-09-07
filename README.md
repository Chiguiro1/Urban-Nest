# Urban Nest

## Instalación

1. Clona el repositorio y entra a la carpeta:
   ```sh
   git clone <URL-del-repositorio>
   cd Urban-Nest
   ```
2. Crea un entorno virtual (opcional pero recomendado):
   ```sh
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```
3. Instala las dependencias:
   ```sh
   pip install -r requirements.txt
   ```

## Variables de entorno

- Para el envío de emails, configura las variables de entorno:
  - `EMAIL_REMITENTE` (correo Gmail)
  - `EMAIL_PASSWORD` (contraseña de aplicación Gmail)

## Ejecución

```sh
python src/main.py
```

## Cómo probar

- Puedes iniciar sesión con el usuario de prueba:
  - Email: `test@local`
  - Contraseña: `test123`
- Prueba registrar un usuario nuevo, verificarlo y agendar/cancelar citas.
- Prueba el formulario de soporte técnico y revisa los logs en la carpeta `logs/`.

## Estructura del proyecto

- `src/database/models.py`: Definición de tablas y seed de datos.
- `src/database/crud.py`: Operaciones CRUD y validaciones.
- `src/interfaces/gui.py`: Interfaz gráfica y lógica de usuario.
- `src/auth/email_utils.py`: Envío de emails y soporte.
- `logs/`: Carpeta de logs de soporte, citas y errores.
- `static/placeholders/`: Imágenes de ejemplo para proyectos.

## Notas

- Las contraseñas se almacenan con SHA-256 (en producción usar sal y PBKDF2/Bcrypt).
- No subas tus credenciales de correo al repositorio público.
- Para pruebas automáticas, puedes crear un archivo en `tests/` y usar `pytest`.

---

**Urban Nest** — App escolar de bienes raíces (visualización y agendamiento de citas)

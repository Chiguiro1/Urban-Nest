# Urban Nest

## Instalación

1. Clone el repositorio y entra a la carpeta:
   ```sh
   git clone <URL-del-repositorio>
   cd Urban-Nest
   ```
2. Cree un entorno virtual :
   ```sh
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```
3. Instale las dependencias:
   ```sh
   pip install -r requirements.txt
   ```

## Variables de entorno

- Para el envío de emails, configure las variables de entorno:
  - `EMAIL_REMITENTE` (correo Gmail)
  - `EMAIL_PASSWORD` (contraseña de aplicación Gmail)

## Ejecución

```sh
python src/main.py
```

## Cómo probar

- Puede iniciar sesión con el usuario de prueba:
  - Email: `test@local`
  - Contraseña: `test123`
- Pruebe registrar un usuario nuevo, verificarlo y agendar/cancelar citas.
- Pruebe el formulario de soporte técnico y revisa los logs en la carpeta `logs/`.

## Estructura del proyecto

- `src/database/models.py`: Definición de tablas y seed de datos.
- `src/database/crud.py`: Operaciones CRUD y validaciones.
- `src/interfaces/gui.py`: Interfaz gráfica y lógica de usuario.
- `src/auth/email_utils.py`: Envío de emails y soporte.
- `logs/`: Carpeta de logs de soporte, citas y errores.

## Notas

- Las contraseñas se almacenan con SHA-256 (en producción usar sal y PBKDF2/Bcrypt).
- No suba sus credenciales de correo al repositorio público.
- Para pruebas automáticas, puedes crear un archivo en `tests/` y usar `pytest`.

## PostData

Soy una puta bestia
---

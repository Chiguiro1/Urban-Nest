import smtplib
import random
import ssl
from email.message import EmailMessage
import datetime

# =========================
# INFORMACION DEL EMAIL DE ENVIO
# =========================
EMAIL_REMITENTE = 'auth.urbannest@gmail.com'
CONTRASEÑA_EMAIL = 'wvyw ebow bjok neet'

# =========================
# GENERACION DEL CODIGO 
# =========================

def generar_codigo():
    """Genera un código de verificación de 6 dígitos"""
    return str(random.randint(100000, 999999))

# =========================
# FUNCION PARA ENVIAR EL CODIGO
# =========================

def enviar_codigo(destinatario, nombre_usuario):
    """Envía un código de verificación al email del usuario"""
    codigo = generar_codigo()
    mensaje = EmailMessage()
    mensaje['From'] = EMAIL_REMITENTE
    mensaje['To'] = destinatario
    mensaje['Subject'] = f'Código de verificación para {nombre_usuario}'
    
    
# =========================
# HTML DEL EMAIL DE VERFIFICACION
# =========================

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background-color: #4a6fa5;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                padding: 20px;
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 0 0 5px 5px;
            }}
            .code {{
                font-size: 24px;
                font-weight: bold;
                color: #4a6fa5;
                text-align: center;
                margin: 20px 0;
                padding: 10px;
                background-color: #e7eff9;
                border-radius: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Verificación de cuenta</h1>
        </div>
        <div class="content">
            <p>Hola <strong>{nombre_usuario}</strong>,</p>
            <p>Tu código de verificación es:</p>
            <div class="code">{codigo}</div>
            <p>Este código expira en 10 minutos.</p>
        </div>
    </body>
    </html>
    """
    
    mensaje.set_content(f"""
    Hola {nombre_usuario},
    
    Tu código de verificación es: {codigo}
    
    Este código expira en 10 minutos.
    """)
    
    mensaje.add_alternative(html_content, subtype='html')

# =========================
# ENVIO DEL MENSAJE
# =========================

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=ssl.create_default_context()) as server:
            server.login(EMAIL_REMITENTE, CONTRASEÑA_EMAIL)
            server.send_message(mensaje)
            return codigo
    except Exception as e:
        print(f"Error al enviar email: {e}")
        return None

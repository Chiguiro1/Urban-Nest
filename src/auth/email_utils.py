import smtplib
import random
import ssl
from email.message import EmailMessage
import datetime
import requests
import socket

# =========================
# INFORMACION DEL EMAIL DE ENVIO
# =========================
EMAIL_REMITENTE = 'auth.urbannest@gmail.com'
CONTRASEÑA_EMAIL = 'grtx fuom lkah fbod'

EMAIL_SOORTE_TECNICO = [
    "luis.rua@tecnicopascualbravo.edu.co",
    "juan.jimenezm@tecnicopascualbravo.edu.co",
    "quinterorojoemanuel@gmail.com"
]
# =========================
# GENERACION DEL CODIGO 
# =========================

def generar_codigo():
    """Genera un código de verificación de 6 dígitos"""
    return str(random.randint(100000, 999999))

# =========================
#  OBTENCION DE IP PUBLICA Y LOCAL
# =========================

def obtener_ip_publica():
    try:
        ip = requests.get("https://api.ipify.org").text
        return ip
    except Exception as e:
        return f"Error al obtener IP pública: {e}"

def obtener_ip_local():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_local = s.getsockname()[0]
        s.close()
        return ip_local
    except Exception as e:
        return f"Error al obtener IP local: {e}"




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


def enviar_soporte_tecnico(nombre_usuario, correo_usuario, asunto, mensaje):
    """Envía un mensaje al soporte técnico con nombre y correo del usuario"""
    email = EmailMessage()
    email['From'] = EMAIL_REMITENTE
    email['To'] = ", ".join(EMAIL_SOORTE_TECNICO)
    email['Subject'] = f"[Soporte Técnico] {asunto}"
    email.set_content(f"""
    Nombre del usuario: {nombre_usuario}
    Correo del usuario: {correo_usuario}
    Asunto: {asunto}

    Mensaje:
    {mensaje}
    """)
    
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
            .field {{
                margin-bottom: 10px;
            }}
            .label {{
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Solicitud de Soporte Técnico</h1>
        </div>
        <div class="content">
            <div class="field">
                <span class="label">Nombre del usuario:</span> {nombre_usuario}
            </div>
            <div class="field">
                <span class="label">Correo del usuario:</span> {correo_usuario}
            </div>
            <div class="field">
                <span class="label">IP Local:</span> {obtener_ip_local()}
            </div>
            <div class="field">
                <span class="label">IP Pública:</span> {obtener_ip_publica()}
            </div>
            <div class="field">
                <span class="label">Asunto:</span> {asunto}
            </div>
            <div class="field">
                <span class="label">Mensaje:</span><br>
                <p>{mensaje}</p>
            </div>
            <p><em>Enviado el {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
        </div>
    </body>
    </html>
    """

    email.add_alternative(html_content, subtype='html')

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=ssl.create_default_context()) as server:
            server.login(EMAIL_REMITENTE, CONTRASEÑA_EMAIL)
            server.send_message(email)
            return True
    except Exception as e:
        print(f"Error al enviar soporte técnico: {e}")
        return False


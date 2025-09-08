import os
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
EMAIL_REMITENTE = os.environ.get('EMAIL_REMITENTE', 'auth.urbannest@gmail.com')
CONTRASEÑA_EMAIL = os.environ.get('EMAIL_PASSWORD', 'grtx fuom lkah fbod')

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
        logs_dir = os.path.join(os.path.dirname(__file__), '../../logs')
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        with open(os.path.join(logs_dir, 'errores.log'), 'a') as f:
            f.write(f"[{datetime.datetime.now().isoformat()}] Error email verificación: {destinatario} - {e}\n")
        return None


def enviar_notificacion_cita(email_usuario, nombre_usuario, proyecto_nombre, fecha, hora, tipo='creada'):
    """
    Envía notificación de cita tanto al usuario como a los 3 asesores.
    """
    asesores = [
        "luis.rua@tecnicopascualbravo.edu.co",
        "juan.jimenezm@tecnicopascualbravo.edu.co",
        "quinterorojoemanuel@gmail.com"
    ]
    asunto = 'Cita Urban Nest confirmada' if tipo=='creada' else 'Cita Urban Nest cancelada'
    cuerpo_usuario = f"Hola {nombre_usuario},\n\nTu cita para el proyecto '{proyecto_nombre}' el {fecha} a las {hora} ha sido {'agendada' if tipo=='creada' else 'cancelada'}.\n\nUrban Nest"
    cuerpo_asesor = f"Nueva cita de usuario: {nombre_usuario} ({email_usuario})\nProyecto: {proyecto_nombre}\nFecha: {fecha}\nHora: {hora}\nEstado: {'Agendada' if tipo=='creada' else 'Cancelada'}\n\nUrban Nest"
    mensaje_usuario = EmailMessage()
    mensaje_usuario['From'] = EMAIL_REMITENTE
    mensaje_usuario['To'] = email_usuario
    mensaje_usuario['Subject'] = asunto
    mensaje_usuario.set_content(cuerpo_usuario)
    mensajes_asesores = []
    for asesor in asesores:
        mensaje_asesor = EmailMessage()
        mensaje_asesor['From'] = EMAIL_REMITENTE
        mensaje_asesor['To'] = asesor
        mensaje_asesor['Subject'] = f"[Asesoría] {asunto}"
        mensaje_asesor.set_content(cuerpo_asesor)
        mensajes_asesores.append(mensaje_asesor)
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_REMITENTE, CONTRASEÑA_EMAIL)
            smtp.send_message(mensaje_usuario)
            for mensaje_asesor in mensajes_asesores:
                smtp.send_message(mensaje_asesor)
        return True
    except Exception as e:
        logs_dir = os.path.join(os.path.dirname(__file__), '../../logs')
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        with open(os.path.join(logs_dir, 'errores.log'), 'a') as f:
            f.write(f"[{datetime.datetime.now().isoformat()}] Error email cita: {email_usuario} y asesores - {e}\n")
        return False

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
        logs_dir = os.path.join(os.path.dirname(__file__), '../../logs')
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        with open(os.path.join(logs_dir, 'errores.log'), 'a') as f:
            f.write(f"[{datetime.datetime.now().isoformat()}] Error email soporte: {correo_usuario} - {e}\n")
        return False


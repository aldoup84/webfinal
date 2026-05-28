import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()


def enviar_correo_contacto(nombre, correo, mensaje):
    """Envía un correo simple desde el backend.

    Puede usarse para contacto, confirmación de cita, solicitud de servicio,
    aviso al administrador, etc.
    """
    email = EmailMessage()
    email["Subject"] = "Nuevo mensaje desde el sistema"
    email["From"] = os.getenv("MAIL_USER")
    email["To"] = os.getenv("MAIL_TO", os.getenv("MAIL_USER"))

    email.set_content(f"""
Nuevo mensaje recibido:

Nombre: {nombre}
Correo: {correo}

Mensaje:
{mensaje}
""")

    with smtplib.SMTP(os.getenv("MAIL_SERVER"), int(os.getenv("MAIL_PORT", 587))) as smtp:
        smtp.starttls()
        smtp.login(os.getenv("MAIL_USER"), os.getenv("MAIL_PASSWORD"))
        smtp.send_message(email)

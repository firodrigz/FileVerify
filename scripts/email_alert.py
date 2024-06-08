import os
import logging
import smtplib
from email.mime.text import MIMEText

def send_email_alert(file_path):
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = os.getenv('SMTP_PORT')
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    from_email = os.getenv('FROM_EMAIL')
    to_email = os.getenv('TO_EMAIL')

    if not all([smtp_server, smtp_port, smtp_user, smtp_password, from_email, to_email]):
        logging.error("Faltan variables de entorno para la configuración del correo electrónico.")
        return

    subject = "Alerta de Integridad de Archivo"
    body = f"Se ha detectado un problema de integridad en el archivo: {file_path}"
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(from_email, to_email, msg.as_string())
            logging.info(f"Correo electrónico enviado a {to_email} sobre el archivo: {file_path}")
    except Exception as e:
        logging.error(f"Error al enviar el correo electrónico: {str(e)}")

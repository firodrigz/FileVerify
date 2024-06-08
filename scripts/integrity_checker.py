import os
import hashlib
import sqlite3
import json
import logging
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

def get_file_hash(file_path):
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as file:
        buffer = file.read()
        hasher.update(buffer)
    return hasher.hexdigest()

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

def check_integrity(directories, db_path, log_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        logging.basicConfig(filename=log_path, level=logging.INFO)
        
        cursor.execute('SELECT path FROM file_hashes')
        db_files = cursor.fetchall()
        db_files = {file[0] for file in db_files}
        
        current_files = set()

        for path in directories:
            if os.path.isdir(path):
                print(f"Verificando el directorio: {path}")
                for root, _, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        current_files.add(file_path)
                        current_hash = get_file_hash(file_path)
                        
                        cursor.execute('SELECT hash FROM file_hashes WHERE path = ?', (file_path,))
                        result = cursor.fetchone()
                        if result:
                            original_hash = result[0]
                            if current_hash != original_hash:
                                log_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                logging.critical(f'[{log_time}] File integrity issue detected: {file_path}')
                                print(f"¡Cambios detectados en el archivo!: {file_path}")
                                send_email_alert(file_path)
                        else:
                            cursor.execute('INSERT INTO file_hashes (path, hash) VALUES (?, ?)', (file_path, current_hash))
                            conn.commit()
            elif os.path.isfile(path):
                print(f"Verificando el archivo: {path}")
                file_path = path
                current_files.add(file_path)
                current_hash = get_file_hash(file_path)
                
                cursor.execute('SELECT hash FROM file_hashes WHERE path = ?', (file_path,))
                result = cursor.fetchone()
                if result:
                    original_hash = result[0]
                    if current_hash != original_hash:
                        log_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        logging.critical(f'[{log_time}] File integrity issue detected: {file_path}')
                        print(f"¡Cambios detectados en el archivo!: {file_path}")
                        send_email_alert(file_path)
                else:
                    cursor.execute('INSERT INTO file_hashes (path, hash) VALUES (?, ?)', (file_path, current_hash))
                    conn.commit()

        deleted_files = db_files - current_files
        for deleted_file in deleted_files:
            log_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logging.critical(f'[{log_time}] File deleted: {deleted_file}')
            print(f"¡Archivo eliminado!: {deleted_file}")
            send_email_alert(deleted_file)
            cursor.execute('DELETE FROM file_hashes WHERE path = ?', (deleted_file,))
            conn.commit()

        print("Verificación de integridad completada.")
    except Exception as e:
        print("Error durante la verificación de integridad:", str(e))
    finally:
        conn.close()

if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_path, '../config/config.json')

    try:
        with open(config_path) as config_file:
            config = json.load(config_file)
        
        db_path = os.path.join(base_path, '../', config['database_path'])
        directories_to_monitor = config['directories_to_monitor']
        log_path = os.path.join(base_path, '../', config['log_path'])

        print(f"Ruta de la base de datos: {db_path}")
        print(f"Directorios a monitorear: {directories_to_monitor}")
        print(f"Ruta del archivo de log: {log_path}")

        check_integrity(directories_to_monitor, db_path, log_path)
    except Exception as e:
        print("Error:", str(e))

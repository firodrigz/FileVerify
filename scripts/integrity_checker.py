import os
import hashlib
import sqlite3
import json
import logging
from datetime import datetime
from email_alert import send_email_alert

def get_file_hash(file_path):
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as file:
        buffer = file.read()
        hasher.update(buffer)
    return hasher.hexdigest()

def check_integrity(directories, db_path, log_path):
    logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
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
        logging.error(f"Error durante la verificación de integridad: {str(e)}")
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
        logging.error(f"Error: {str(e)}")
        print("Error:", str(e))

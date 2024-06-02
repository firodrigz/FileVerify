import os
import hashlib
import sqlite3
import json
import logging
from datetime import datetime
# from email_alert import send_email_alert  # Descomenta si tienes email_alert.py implementado

def get_file_hash(file_path):
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as file:
        buffer = file.read()
        hasher.update(buffer)
    return hasher.hexdigest()

def check_integrity(directories, db_path, log_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    logging.basicConfig(filename=log_path, level=logging.INFO)

    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                current_hash = get_file_hash(file_path)
                
                cursor.execute('SELECT hash FROM file_hashes WHERE path = ?', (file_path,))
                result = cursor.fetchone()
                if result:
                    original_hash = result[0]
                    if current_hash != original_hash:
                        logging.info(f'[{datetime.now()}] File integrity issue detected: {file_path}')
                        print("Cambios!")
                        # send_email_alert(file_path)  # Descomenta si tienes email_alert.py implementado
                else:
                    cursor.execute('INSERT INTO file_hashes (path, hash) VALUES (?, ?)', (file_path, current_hash))
                    conn.commit()

    conn.close()

if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_path, '../config/config.json')

    with open(config_path) as config_file:
        config = json.load(config_file)
    
    db_path = os.path.join(base_path, '../', config['database_path'])
    directories_to_monitor = config['directories_to_monitor']
    log_path = os.path.join(base_path, '../', config['log_path'])

    check_integrity(directories_to_monitor, db_path, log_path)

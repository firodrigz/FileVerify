import os
import hashlib
import sqlite3
import json

def get_file_hash(file_path):
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as file:
        buffer = file.read()
        hasher.update(buffer)
    return hasher.hexdigest()

def initialize_db(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS file_hashes (
                            path TEXT PRIMARY KEY,
                            hash TEXT
                          )''')
        conn.commit()
        print("Base de datos inicializada correctamente.")
    except Exception as e:
        print("Error al inicializar la base de datos:", str(e))
    finally:
        conn.close()

def store_initial_hashes(directories, db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        for directory in directories:
            if os.path.isdir(directory):
                for root, _, files in os.walk(directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            file_hash = get_file_hash(file_path)
                            cursor.execute('INSERT OR REPLACE INTO file_hashes (path, hash) VALUES (?, ?)', (file_path, file_hash))
                        except Exception as e:
                            print("Error al procesar el archivo:", file_path, str(e))
        conn.commit()
        print("Hashes almacenados correctamente.")
    except Exception as e:
        print("Error al almacenar los hashes:", str(e))
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

        initialize_db(db_path)
        store_initial_hashes(directories_to_monitor, db_path)
    except Exception as e:
        print("Error:", str(e))

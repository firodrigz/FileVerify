import os
import hashlib
import sqlite3
import json
import logging

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
        logging.info("Base de datos inicializada correctamente.")
    except Exception as e:
        logging.error("Error al inicializar la base de datos:", str(e))
    finally:
        conn.close()

def store_initial_hashes(directories, db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        all_hashes_stored = True  # Indicador de que todos los hashes se almacenaron correctamente
        for path in directories:
            if os.path.isdir(path):
                logging.info(f"Procesando el directorio: {path}")
                for root, _, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            file_hash = get_file_hash(file_path)
                            cursor.execute('INSERT OR REPLACE INTO file_hashes (path, hash) VALUES (?, ?)', (file_path, file_hash))
                            logging.info(f"Archivo procesado: {file_path}")
                        except Exception as e:
                            logging.error(f"Error al procesar el archivo: {file_path}, {str(e)}")
                            all_hashes_stored = False
            elif os.path.isfile(path):
                logging.info(f"Procesando el archivo: {path}")
                try:
                    file_hash = get_file_hash(path)
                    cursor.execute('INSERT OR REPLACE INTO file_hashes (path, hash) VALUES (?, ?)', (path, file_hash))
                    logging.info(f"Archivo procesado: {path}")
                except Exception as e:
                    logging.error(f"Error al procesar el archivo: {path}, {str(e)}")
                    all_hashes_stored = False
            else:
                logging.error(f"El archivo o directorio no existe: {path}")
                all_hashes_stored = False

        if all_hashes_stored:
            conn.commit()
            logging.info("Hashes almacenados correctamente.")
        else:
            logging.error("Hubo errores en el almacenamiento de algunos hashes.")

    except Exception as e:
        logging.error(f"Error al almacenar los hashes: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_path, '../config/config.json')

    try:
        with open(config_path) as config_file:
            config = json.load(config_file)
        logging.basicConfig(filename=os.path.join(base_path, '../', config['log_path_auto']), level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

        db_path = os.path.join(base_path, '../', config['database_path'])
        directories_to_monitor = config['directories_to_monitor']

        print(f"Ruta de la base de datos: {db_path}")
        print(f"Directorios a monitorear: {directories_to_monitor}")

        initialize_db(db_path)
        store_initial_hashes(directories_to_monitor, db_path)
    except Exception as e:
        logging.error("Error:", str(e))
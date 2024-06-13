
import os
import subprocess
import json
import logging

def load_config(config_path):
    with open(config_path) as config_file:
        config = json.load(config_file)
    return config

def run_script(script_path):
    try:
        subprocess.run(['python', script_path], check=True)
        logging.info(f"Ejecución de script correcta: {script_path}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Error al ejecutar el script {script_path}: {str(e)}")
        return False

def check_env_vars(required_vars):
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logging.error(f"Variables de entorno faltantes: {', '.join(missing_vars)}")
        return False
    return True

if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_path, '../config/config.json')
    
    try:
        config = load_config(config_path)
        logging.basicConfig(
            filename=os.path.join(base_path, '../', config['log_path_auto']),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        set_env_vars_script = os.path.join(base_path, 'set_env_vars.py')
        initialize_hashes_script = os.path.join(base_path, 'initialize_hashes.py')

        # set_env_vars.py
        if run_script(set_env_vars_script):
            # Check variables de entorno
            required_env_vars = [
                'SMTP_SERVER', 'SMTP_PORT', 'SMTP_USER', 'SMTP_PASSWORD',
                'FROM_EMAIL', 'TO_EMAIL'
            ]
            if check_env_vars(required_env_vars):
                # initialize_hashes.py solo se ejecuta si todas las variables de entorno existen
                if run_script(initialize_hashes_script):
                    print("Configuración inicial completa.")
                    logging.info("Configuración inicial completa.")
                else:
                    logging.error("Error al ejecutar initialize_hashes.py debido a un error.")
            else:
                logging.error("No se establecen todas las variables de entorno necesarias.")
        else:
            logging.error("Error al ejecutar set_env_vars.py debido a un error.")
    
    except Exception as e:
        logging.error(f"Error en script: {str(e)}")
        print(f"Error: {str(e)}")
        
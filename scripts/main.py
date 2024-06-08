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
        logging.info(f"Successfully ran script: {script_path}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running script {script_path}: {str(e)}")

if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_path, '../config/config.json')
    
    config = load_config(config_path)
    logging.basicConfig(filename=os.path.join(base_path, '../', config['log_path_auto']), level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        
        set_env_vars_script = os.path.join(base_path, 'set_env_vars.py')
        initialize_hashes_script = os.path.join(base_path, 'initialize_hashes.py')

        # Run set_env_vars.py and initialize_hashes.py once at the beginning
        #run_script(set_env_vars_script)
        run_script(initialize_hashes_script)

        print("Initial setup completed successfully.")
        logging.info("Initial setup completed successfully.")

    except Exception as e:
        logging.error(f"Error in main automation script: {str(e)}")
        print(f"Error: {str(e)}")

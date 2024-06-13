import os
import platform
import getpass

def set_env_vars():
    smtp_server = input("Ingrese SMTP Server (smtp.gmail.com - Gmail): ")
    smtp_port = input("Ingrese SMTP Port (587 - Gmail): ")
    email_username = input("Ingrese Email origen: ")
    email_password = getpass.getpass(f"Ingrese password para {email_username}: ")
    from_email = email_username
    to_email = input("Ingrese Email de destino: ")

    env_vars = {
        'SMTP_SERVER': smtp_server,
        'SMTP_PORT': smtp_port,
        'SMTP_USER': email_username,
        'SMTP_PASSWORD': email_password,
        'FROM_EMAIL': from_email,
        'TO_EMAIL': to_email
    }

    if platform.system() == 'Windows':
        for key, value in env_vars.items():
            os.system(f'setx {key} "{value}"')
    else:
        bash_profile = os.path.expanduser("~/.bashrc")
        zsh_profile = os.path.expanduser("~/.zshrc")
        profile_path = bash_profile if os.path.exists(bash_profile) else zsh_profile
        with open(profile_path, "a") as profile:
            for key, value in env_vars.items():
                profile.write(f'export {key}="{value}"\n')

    print("Se han establecido variables de entorno. Reinicie su terminal o ejecute 'source ~/.bashrc' o 'source ~/.zshrc' para que los cambios surtan efecto.")

if __name__ == "__main__":
    set_env_vars()

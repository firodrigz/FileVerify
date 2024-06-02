# Sistema de Monitoreo de Integridad de Archivos

## Descripción
Este proyecto monitorea la integridad de archivos críticos y envía alertas en caso de detectar cambios no autorizados.

## Requisitos
- Python 3
- Librerías: hashlib, sqlite3, smtplib

## Instalación
1. Clona este repositorio:

``` bash 
git clone https://github.com/firodrigz/FileVerify.git
```

2. Instala las dependencias:

``` bash 
pip install -r requirements.txt
```
3. Configura el archivo `config/config.json` con los directorios a monitorear y las opciones de alerta por correo electrónico.

## Uso
1. Genera los hashes iniciales:

``` bash 
cd scripts
python3 scripts/initialize_hashes.py
```

2. Programa la verificación de integridad (por ejemplo, usando `cron` en sistemas Unix).

``` bash 
crontab -e
```

Añade la siguiente línea para ejecutar el script cada hora:

``` bash 
0 * * * * /usr/bin/python3 /path/to/FileVerify/scripts/integrity_checker.py
```

## Contribuciones
Las contribuciones son bienvenidas. Por favor, abre un `issue` o envía un `pull request`.



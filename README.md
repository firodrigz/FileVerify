# Verificador de Integridad de Archivos/Directorios

## Descripción
Este proyecto monitorea la integridad de archivos críticos y envía alertas por correo electrónico en caso de detectar cambios no autorizados. Funciona tanto en archivos individuales como en directorios. Detecta eliminación de archivo original.

## Requisitos
- Python 3
- Librerías: hashlib, sqlite3, smtplib, json, logging, os

## Instalación
1. Clona este repositorio:

``` bash 
git clone https://github.com/firodrigz/FileVerify.git
```

2. Configura el archivo `config/config.json` con los directorios a monitorear.

## Uso
1. Ingresa las credenciales para en envío de la alerta por correo electrónico y genera los hashes iniciales:

``` bash 
cd scripts
python3 set_env_vars.py
```

2. Inicializar hashes de las rutas a monitorear.

``` bash 
python3 initialize_hashes.py
```

3. Programa la verificación de integridad (por ejemplo, usando `cron` en sistemas Unix).

``` bash 
crontab -e
```

Añade la siguiente línea para ejecutar el script cada hora:

``` bash 
0 * * * * /usr/bin/python3 /path/to/FileVerify/scripts/integrity_checker.py
```

## Contribuciones
Las contribuciones son bienvenidas. Por favor, abre un `issue` o envía un `pull request`.



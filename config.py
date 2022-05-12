import os

from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")  # Забираем значение типа str
ADMINS = env.list("ADMINS")  # Тут у нас будет список из админов
RAPID_API_KEY = env.str("RAPID_API_KEY")  # АПИ ключ
ip = env.str("ip")

# webhook settings
WEBHOOK_HOST = f'https://{ip}'
WEBHOOK_PORT = 8443
WEBHOOK_PATH = f'/bot/{BOT_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}:{WEBHOOK_PORT}{WEBHOOK_PATH}'

# webserver settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.getenv("WEBAPP_PORT")

WEBHOOK_SSL_CERT = 'webhook_cert.pem'
WEBHOOK_SSL_PRIV = 'webhook_pkey.pem'

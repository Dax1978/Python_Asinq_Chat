"""Константы"""

import os
import logging
import socket

# Порт поумолчанию для сетевого ваимодействия
DEFAULT_PORT = 7777
# IP адрес по умолчанию для подключения клиента
DEFAULT_IP_ADDRESS = '127.0.0.1'
# Максимальная очередь подключений
MAX_CONNECTIONS = 5
# Максимальная длинна сообщения в байтах
MAX_PACKAGE_LENGTH = 1024
# Кодировка проекта
ENCODING = 'utf-8'
# Текущий уровень логирования
LOGGING_LEVEL = logging.DEBUG

# Прококол JIM основные ключи:
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'sender'

# Прочие ключи, используемые в протоколе
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
MESSAGE = 'message'
MESSAGE_TEXT = 'mess_text'

# ЛОГИРОВАНИЕ
# Директория логов
root, chat_utils = os.path.split(os.path.dirname(os.path.abspath(__file__)))
storage_name = os.path.join(root, 'logs/log-storage')
if not os.path.exists(storage_name):
    os.mkdir(storage_name)
LOG_FILE_CLIENT = os.path.join(storage_name, 'client.log')
LOG_FILE_SERVER = os.path.join(storage_name, 'server.log')
print(storage_name)
# Форматирование логов
FORMATTER = logging.Formatter("%(asctime)s - %(levelname)-8s - %(module)-8s - %(message)s ")
TRANSPORT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
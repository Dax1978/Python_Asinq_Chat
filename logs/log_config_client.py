"""Кофнфиг клиентского логгера"""

import sys
import os
import logging

from chat_utils.variables import LOGGING_LEVEL, ENCODING, FORMATTER, LOG_FILE_CLIENT

sys.path.append('../')


# потоки вывода логов
STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(FORMATTER)
STREAM_HANDLER.setLevel(LOGGING_LEVEL)
FILE_HANDLER = logging.FileHandler(LOG_FILE_CLIENT, encoding=ENCODING)
FILE_HANDLER.setFormatter(FORMATTER)

# создаём регистратор и настраиваем его
LOGGER = logging.getLogger('client')
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(FILE_HANDLER)
LOGGER.setLevel(LOGGING_LEVEL)

if __name__ == '__main__':
    console = logging.StreamHandler()
    console.setLevel(LOGGING_LEVEL)
    console.setFormatter(FORMATTER)
    LOGGER.addHandler(console)
    LOGGER.info('Тестовый запуск логирования')
    LOGGER.critical('Критическая ошибка')
    LOGGER.error('Ошибка')
    LOGGER.debug('Отладочная информация')
    LOGGER.info('Информационное сообщение')

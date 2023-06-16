"""Кофнфиг серверного логгера"""

import sys
import os
import logging
import logging.handlers

from chat_utils.variables import LOGGING_LEVEL, ENCODING, FORMATTER, LOG_FILE_SERVER

sys.path.append('../')


# потоки вывода логов
STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(FORMATTER)
STREAM_HANDLER.setLevel(LOGGING_LEVEL)
FILE_HANDLER = logging.handlers.TimedRotatingFileHandler(LOG_FILE_SERVER, encoding=ENCODING, interval=1, when='midnight')
# FILE_HANDLER = logging.handlers.TimedRotatingFileHandler(filename, encoding='utf8', interval=1, when='D')
# FILE_HANDLER = logging.FileHandler(filename, encoding='utf-8', interval=1, when='D', backupCount=7)
FILE_HANDLER.setFormatter(FORMATTER)

# создаём регистратор и настраиваем его
LOGGER = logging.getLogger('server')
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(FILE_HANDLER)
LOGGER.setLevel(LOGGING_LEVEL)


if __name__ == '__main__':
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(FORMATTER)
    LOGGER.addHandler(console)
    LOGGER.info('Тестовый запуск логирования')
    LOGGER.critical('Критическая ошибка')
    LOGGER.error('Ошибка')
    LOGGER.debug('Отладочная информация')
    LOGGER.info('Информационное сообщение')

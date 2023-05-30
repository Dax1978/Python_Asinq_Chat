import sys
import logging
import logging.handlers
import os.path


# Форматирование логов
FORMATTER = logging.Formatter(
    "%(asctime)s - %(levelname)-8s - %(module)-8s - %(message)s ")

# Имя файла лога server.log в директории log-storage
storage_name = 'log/log-storage'
if not os.path.exists(storage_name):
    os.mkdir(storage_name)
filename = os.path.join(storage_name, 'server.log')

# потоки вывода логов
STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(FORMATTER)
STREAM_HANDLER.setLevel(logging.ERROR)

FILE_HANDLER = logging.handlers.TimedRotatingFileHandler(filename, encoding='utf8', interval=1, when='midnight')
# FILE_HANDLER = logging.handlers.TimedRotatingFileHandler(filename, encoding='utf8', interval=1, when='D')
# FILE_HANDLER = logging.FileHandler(filename, encoding='utf-8', interval=1, when='D', backupCount=7)
FILE_HANDLER.setFormatter(FORMATTER)

# создаём регистратор и настраиваем его
LOGGER = logging.getLogger('server')
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(FILE_HANDLER)
LOGGER.setLevel(logging.DEBUG)


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

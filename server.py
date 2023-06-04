"""Программа-сервер"""

import sys
import logging
import socket
import json

from chat_utils import utils as chat_utils
from chat_utils.errors import IncorrectDataRecivedError
from chat_utils.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, MAX_CONNECTIONS, TRANSPORT
from logs.log_decos import log
import logs.log_config_server


client_name = ''

LOGGER = logging.getLogger('server')

@log
def process_client_message(message):
    """
    Обработчик сообщений от клиентов, принимает словарь - сообщение от клинта,
    проверяет корректность, возвращает словарь-ответ для клиента
    :param message:
    :return:
    """
    LOGGER.debug(f'Разбор сообщения от клиента : {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message and \
            USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    return {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }

def main():
    """Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию"""
    listen_address, listen_port, port_corr = chat_utils.get_addr_port()

    # проверка получения корретного номера порта для работы сервера.
    if not port_corr: sys.exit(1)

    # Готовим сокет
    TRANSPORT.bind((listen_address, listen_port))
    # Слушаем порт
    TRANSPORT.listen(MAX_CONNECTIONS)

    while True:
        client, client_address = TRANSPORT.accept()
        LOGGER.info(f'Установлено соедение с ПК {client_address}')
        try:
            message_from_cient = chat_utils.get_message(client)
            LOGGER.debug(f'Получено сообщение {message_from_cient}')
            print(message_from_cient)
            response = process_client_message(message_from_cient)
            LOGGER.info(f'Cформирован ответ клиенту {response}')
            chat_utils.send_message(client, response)
            LOGGER.debug(f'Соединение с клиентом {client_address} закрывается.')
            client.close()
        except json.JSONDecodeError:
            LOGGER.error(f'Не удалось декодировать Json строку, '
                         f'полученную от клиента {client_address}. Соединение закрывается.')
            client.close()
        except IncorrectDataRecivedError:
            LOGGER.error(f'От клиента {client_address} приняты некорректные данные. '
                         f'Соединение закрывается.')
            client.close()


if __name__ == '__main__':
    main()

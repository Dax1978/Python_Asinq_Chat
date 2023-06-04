"""Программа-клиент"""

import sys
import json
import socket
import time
import argparse
import logging

import logs.log_config_client
from chat_utils import utils as chat_utils
from chat_utils.variables import ACTION, TIME, USER, ACCOUNT_NAME, RESPONSE, \
    DEFAULT_IP_ADDRESS, DEFAULT_PORT, ERROR, PRESENCE, TRANSPORT
from chat_utils.errors import ReqFieldMissingError
from logs.log_decos import log


LOGGER = logging.getLogger('client')

@log
def create_presence(account_name='Guest'):
    """Функция генерирует запрос о присутствии клиента"""
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out

@log
def process_ans(message):
    """Функция разбирает ответ сервера"""
    LOGGER.debug(f'Разбор сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        return f'400 : {message[ERROR]}'
    raise ReqFieldMissingError(RESPONSE)

def main():
    """Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию"""
    server_address, server_port, port_corr = chat_utils.get_addr_port(False)

    # проверка получения корретного номера порта для работы сервера.
    if not port_corr: sys.exit(1)

    # Инициализация сокета и обмен
    try:
        TRANSPORT.connect((server_address, server_port))
        message_to_server = create_presence()
        chat_utils.send_message(TRANSPORT, message_to_server)
        answer = process_ans(chat_utils.get_message(TRANSPORT))
        LOGGER.info(f'Принят ответ от сервера {answer}')
    except json.JSONDecodeError:
        LOGGER.error('Не удалось декодировать полученную Json строку.')
    except ReqFieldMissingError as missing_error:
        LOGGER.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
    except ConnectionRefusedError:
        LOGGER.critical(f'Не удалось подключиться к серверу {server_address}:{server_port}, '
                        f'конечный компьютер отверг запрос на подключение.')

if __name__ == '__main__':
    main()
"""Утилиты"""

import json
import sys
import argparse
import logging

from chat_utils.variables import MAX_PACKAGE_LENGTH, ENCODING, DEFAULT_IP_ADDRESS, DEFAULT_PORT
from chat_utils.errors import IncorrectDataRecivedError, NonDictInputError
from logs.log_decos import log
import logs.log_config_server
import logs.log_config_client

sys.path.append('../')
LOGGER_SERVER = logging.getLogger('server')
LOGGER_CLIENT = logging.getLogger('client')


@log
def get_message(client):
    """
    Утилита приёма и декодирования сообщения принимает байты выдаёт словарь,
    если принято что-то другое отдаёт ошибку значения
    :param client:
    :return:
    """
    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise IncorrectDataRecivedError
    raise IncorrectDataRecivedError


@log
def send_message(sock, message):
    """
    Утилита кодирования и отправки сообщения
    принимает словарь и отправляет его
    :param sock:
    :param message:
    :return:
    """
    if not isinstance(message, dict):
        raise NonDictInputError
    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    sock.send(encoded_message)


@log
def create_arg_parser(isServer):
    """Парсер аргументов коммандной строки"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', default='', nargs='?') if isServer else parser.add_argument('-a', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    print(parser)

    return parser

@log
def get_addr_port(isServer = True):
    namespace = create_arg_parser(isServer).parse_args(sys.argv[1:])
    print('-----namespace------', namespace)
    port_corr = True

    # проверка получения корретного номера порта для работы сервера и клиента.
    if not 1023 < namespace.p < 65536:
        if isServer:
            LOGGER_SERVER.critical(f'Попытка запуска сервера с указанием неподходящего порта {namespace.p}. '
                f'Допустимы адреса с 1024 до 65535.')
        else:
            LOGGER_CLIENT.critical(f'Попытка запуска клиента с неподходящим номером порта: {namespace.p}. '
                f'Допустимы адреса с 1024 до 65535. Клиент завершается.')
        port_corr = False
    else:
        if isServer:
            LOGGER_SERVER.info(f'Запущен сервер, порт для подключений: {namespace.p}, адрес,'
                        f' с которого принимаются подключения: {namespace.a}. '
                        f'Если адрес не указан, принимаются соединения с любых адресов.')
        else:
            LOGGER_CLIENT.info(f'Запущен клиент с парамертами: адрес сервера: '
                        f'{namespace.a}, порт: {namespace.p}')

    return namespace.a, namespace.p, port_corr

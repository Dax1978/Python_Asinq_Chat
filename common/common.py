"""Утилиты"""

import json
import sys
import argparse
import logging
import socket

from chat_utils.variables import MAX_PACKAGE_LENGTH, ENCODING, DEFAULT_IP_ADDRESS, DEFAULT_PORT
from chat_utils.errors import IncorrectDataRecivedError, NonDictInputError
from logs.log_decos import log
import logs.log_config_server
import logs.log_config_client


sys.path.append('../')


class ChatUtils():
    def __init__(self):
        self.LOGGER_SERVER = logging.getLogger('server')
        self.LOGGER_CLIENT = logging.getLogger('client')

    @log
    def get_message(self, client: socket):
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
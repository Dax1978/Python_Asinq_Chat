import sys
import socket
import argparse
import logging
import time
import json

from common.variables import DEFAULT_PORT, MAX_CONNECTIONS, ACTION, SENDER, TIME, MESSAGE_TEXT, MESSAGE, \
    MAX_PACKAGE_LENGTH, ENCODING, PRESENCE, USER, ACCOUNT_NAME, RESPONSE, ERROR, DEFAULT_IP_ADDRESS
from chat_utils.errors import IncorrectDataRecivedError, NonDictInputError, ReqFieldMissingError, ServerError
from logs.log_decos import log
import logs.log_config_server


sys.path.append('../')


class Client():
    def __init__(self):
        self.TRANSPORT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.LOGGER_CLIENT = logging.getLogger('client')

        self.run()

    @log
    def create_presence(self, account_name='Guest'):
        """Функция генерирует запрос о присутствии клиента"""
        out = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: account_name
            }
        }
        self.LOGGER_CLIENT.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
        return out

    @log
    def process_response_ans(self, message: dict):
        """
        Функция разбирает ответ сервера на сообщение о присутствии,
        возращает 200 если все ОК или генерирует исключение при ошибке
        """
        self.LOGGER_CLIENT.debug(f'Разбор приветственного сообщения от сервера: {message}')
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return '200 : OK'
            elif message[RESPONSE] == 400:
                raise ServerError(f'400 : {message[ERROR]}')
        raise ReqFieldMissingError(RESPONSE)

    @log
    def process_ans(self, message: dict):
        """Функция разбирает ответ сервера"""
        self.LOGGER_CLIENT.debug(f'Разбор сообщения от сервера: {message}')
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return '200 : OK'
            return f'400 : {message[ERROR]}'
        raise ReqFieldMissingError(RESPONSE)

    @log
    def message_from_server(self, message: dict):
        """Функция - обработчик сообщений других пользователей, поступающих с сервера"""
        if ACTION in message and message[ACTION] == MESSAGE and \
                SENDER in message and MESSAGE_TEXT in message:
            print(f'Получено сообщение от пользователя '
                  f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
            self.LOGGER_CLIENT.info(f'Получено сообщение от пользователя '
                        f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
        else:
            self.LOGGER_CLIENT.error(f'Получено некорректное сообщение с сервера: {message}')

    @log
    def get_args_parser(self):
        """
        Парсер аргументов коммандной строки
        """
        parser = argparse.ArgumentParser(description='Client script')
        parser.add_argument('-a', default=DEFAULT_IP_ADDRESS, type=str, nargs='?',
                            help='Параметр -a позволяет указать IP-адрес сервера (по умолчанию localhost')
        parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?',
                            help='Параметр -p позволяет указать порт сервера (по умолчанию 7777)')
        parser.add_argument('-m', default='listen', type=str, nargs='?',
                            help='Параметр -m позволяет указать режим работы клиента listen или send (по умолчанию listen)')
        return parser

    @log
    def get_addr_port(self):
        """
        Определяем порт, на котором будет работать сервер, и адрес с которого будут поступать запросы на сервер.
        По умолчанию сервер будет принимать со всех адресов.
        """
        parser = self.get_args_parser()
        args = parser.parse_args()
        self.ADDR = args.a
        self.PORT = args.p
        self.MODE = args.m
        if not 1023 < self.PORT < 65536:
            self.LOGGER_CLIENT.critical(f'Попытка запуска клиента с неподходящим номером порта сервера: {self.PORT}. '
                f'Допустимы адреса с 1024 до 65535. Для клиента будет установлен порт сервера: {DEFAULT_PORT}')
            print(f'Попытка запуска клиента с неподходящим номером порта сервера: {self.PORT}. '
                f'Допустимы адреса с 1024 до 65535. Для клиента будет установлен порт сервера: {DEFAULT_PORT}')
            self.PORT = DEFAULT_PORT
        else:
            # Проверим допустим ли выбранный режим работы клиента
            if self.MODE not in ('listen', 'send'):
                self.LOGGER_CLIENT.critical(f'Указан недопустимый режим работы {self.MODE}, '
                    f'допустимые режимы: listen , send\nБудет установлен режим по умолчанию listen')
                print(f'Указан недопустимый режим работы {self.MODE}, допустимые режимы: listen , send\n'
                    f'Будет установлен режим по умолчанию listen')
                self.MODE = 'listen'
            self.LOGGER_CLIENT.info(f'Запущен клиент с парамертами:\n'
                f'   адрес сервера: {self.ADDR}, порт: {self.PORT}, режим: {self.MODE}')
            print(f'Запущен клиент с парамертами:\n'
                f'   адрес сервера: {self.ADDR}, порт: {self.PORT}, режим: {self.MODE}')

    @log
    def get_message(self, client):
        """
            Утилита приёма и декодирования сообщения принимает байты выдаёт словарь,
            если принято что-то другое отдаёт ошибку значения
            :param client:
            :return:
            """
        encoded_response = client.recv(MAX_PACKAGE_LENGTH)
        if isinstance(encoded_response, bytes):
            # print('encoded_response', encoded_response)
            json_response = encoded_response.decode(ENCODING)
            # print('json_response', json_response)
            response = json.loads(json_response)
            # print('response', response)
            if isinstance(response, dict):
                return response
            raise IncorrectDataRecivedError
        raise IncorrectDataRecivedError

    @log
    def send_message(self, sock, message):
        """
        Утилита кодирования и отправки сообщения принимает словарь и отправляет его
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
    def create_message(self, sock, account_name='Guest'):
        """Функция запрашивает текст сообщения и возвращает его.
        Так же завершает работу при вводе подобной комманды
        """
        message = input('Введите сообщение для отправки или \'exit\' для завершения работы: ')
        if message == 'exit':
            sock.close()
            self.LOGGER_CLIENT.info('Завершение работы по команде пользователя.')
            print('Спасибо за использование нашего сервиса!')
            sys.exit(0)
        message_dict = {
            ACTION: MESSAGE,
            TIME: time.time(),
            ACCOUNT_NAME: account_name,
            MESSAGE_TEXT: message
        }
        self.LOGGER_CLIENT.debug(f'Сформирован словарь сообщения: {message_dict}')
        return message_dict

    @log
    def start_client(self):
        """
        Запуск клиента
        """
        self.get_addr_port()
        # Инициализация сокета и сообщение серверу о нашем появлении
        try:
            self.TRANSPORT.connect((self.ADDR, self.PORT))
            self.send_message(self.TRANSPORT, self.create_presence())
            answer = self.process_response_ans(self.get_message(self.TRANSPORT))
            self.LOGGER_CLIENT.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
            print(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        except json.JSONDecodeError:
            self.LOGGER_CLIENT.error('Не удалось декодировать полученную Json строку.')
            print(f'Не удалось декодировать полученную Json строку.')
            sys.exit(1)
        except ServerError as error:
            self.LOGGER_CLIENT.error(f'При установке соединения сервер вернул ошибку: {error.text}')
            print(f'При установке соединения сервер вернул ошибку: {error.text}')
            sys.exit(1)
        except ReqFieldMissingError as missing_error:
            self.LOGGER_CLIENT.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
            print(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
            sys.exit(1)
        except ConnectionRefusedError:
            self.LOGGER_CLIENT.critical(f'Не удалось подключиться к серверу {self.ADDR}:{self.PORT}, '
                            f'конечный компьютер отверг запрос на подключение.')
            print(f'Не удалось подключиться к серверу {self.ADDR}:{self.PORT}, '
                            f'конечный компьютер отверг запрос на подключение.')
            sys.exit(1)
        else:
            # Если соединение с сервером установлено корректно, начинаем обмен с ним, согласно требуемому режиму
            # основной цикл прогрммы:
            if self.MODE == 'send':
                print('Режим работы - отправка сообщений.')
            else:
                print('Режим работы - приём сообщений.')
            while True:
                # режим работы - отправка сообщений
                if self.MODE == 'send':
                    try:
                        self.send_message(self.TRANSPORT, self.create_message(self.TRANSPORT))
                    except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                        self.LOGGER_CLIENT.error(f'Соединение с сервером {self.ADDR} было потеряно.')
                        sys.exit(1)

                # Режим работы приём:
                if self.MODE == 'listen':
                    try:
                        self.message_from_server(self.get_message(self.TRANSPORT))
                    except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                        self.LOGGER_CLIENT.error(f'Соединение с сервером {self.ADDR} было потеряно.')
                        sys.exit(1)

    def run(self):
        self.start_client()


if __name__ == '__main__':
    client = Client()
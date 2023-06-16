import sys
import socket
import argparse
import logging
import time
import json
import threading

from common.variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, ACTION, TIME, USER, ACCOUNT_NAME, SENDER, \
    PRESENCE, RESPONSE, ERROR, MESSAGE, MESSAGE_TEXT, MAX_PACKAGE_LENGTH, ENCODING, DESTINATION, EXIT
from chat_utils.errors import IncorrectDataRecivedError, NonDictInputError, ReqFieldMissingError, ServerError
from logs.log_decos import log
import logs.log_config_server
from metaclasses import ClientMaker


sys.path.append('../')


class Client(metaclass=ClientMaker):
    def __init__(self):
        self.TRANSPORT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.LOGGER_CLIENT = logging.getLogger('client')

        self.run()

    @log
    def create_presence_message(self, account_name):
        """Метод генерирует запрос о присутствии клиента"""
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
    def create_message(self, sock, account_name='Guest'):
        """Метод запрашивает текст сообщения и возвращает его.
        Так же завершает работу при вводе подобной комманды
        :param sock:
        :param account_name:
        :return:
        """
        # message = input('Введите сообщение для отправки или \'exit\' для завершения работы: ')
        # if message == 'exit':
        #     sock.close()
        #     self.LOGGER_CLIENT.info('Завершение работы по команде пользователя.')
        #     print('Спасибо за использование нашего сервиса!')
        #     sys.exit(0)
        # message_dict = {
        #     ACTION: MESSAGE,
        #     TIME: time.time(),
        #     ACCOUNT_NAME: account_name,
        #     MESSAGE_TEXT: message
        # }
        # self.LOGGER_CLIENT.debug(f'Сформирован словарь сообщения: {message_dict}')
        # return message_dict
        to_user = input('Введите имя получателя сообщения: ')
        message = input('Введите сообщение для отправки: ')
        message_dict = {
            ACTION: MESSAGE,
            SENDER: account_name,
            DESTINATION: to_user,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        self.LOGGER_CLIENT.debug(f'Сформирован словарь сообщения: {message_dict}')
        try:
            self.send_message(sock, message_dict)
            self.LOGGER_CLIENT.info(f'Отправлено сообщение для пользователя {to_user}')
        except:
            self.LOGGER_CLIENT.critical('Потеряно соединение с сервером.')
            sys.exit(1)

    @log
    def user_interactive(self, sock, username):
        """Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения"""
        self.print_help()
        while True:
            command = input('Введите команду ( message / help / exit ): ')
            if command == 'message':
                self.create_message(sock, username)
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                self.send_message(sock, self.create_exit_message(username))
                print('Завершение соединения.')
                self.LOGGER_CLIENT.info('Завершение работы по команде пользователя.')
                # Задержка неоходима, чтобы успело уйти сообщение о выходе
                time.sleep(0.5)
                break
            else:
                print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')

    @log
    def print_help(self):
        """Метод вывода справки по использованию"""
        print('Поддерживаемые команды:')
        print('message - отправить сообщение. "Кому" и "текст сообщения" будет запрошены отдельно.')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')

    @log
    def create_exit_message(self, account_name):
        """Метод создаёт словарь с сообщением о выходе"""
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: account_name
        }

    @log
    def process_response_ans(self, message: dict):
        """
        Метод разбирает ответ сервера на сообщение о присутствии,
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
        """Метод разбирает ответ сервера"""
        self.LOGGER_CLIENT.debug(f'Разбор сообщения от сервера: {message}')
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return '200 : OK'
            return f'400 : {message[ERROR]}'
        raise ReqFieldMissingError(RESPONSE)

    # def message_from_server(self, message: dict):
    @log
    def message_from_server(self, sock, my_username):
        """Метод - обработчик сообщений других пользователей, поступающих с сервера"""
        # if ACTION in message and message[ACTION] == MESSAGE and \
        #         SENDER in message and MESSAGE_TEXT in message:
        #     print(f'Получено сообщение от пользователя '
        #           f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
        #     self.LOGGER_CLIENT.info(f'Получено сообщение от пользователя '
        #                 f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
        # else:
        #     self.LOGGER_CLIENT.error(f'Получено некорректное сообщение с сервера: {message}')
        while True:
            try:
                message = self.get_message(sock)
                if ACTION in message and message[ACTION] == MESSAGE and \
                        SENDER in message and DESTINATION in message \
                        and MESSAGE_TEXT in message and message[DESTINATION] == my_username:
                    print(f'\nПолучено сообщение от пользователя {message[SENDER]}:'
                          f'\n{message[MESSAGE_TEXT]}')
                    self.LOGGER_CLIENT.info(f'Получено сообщение от пользователя {message[SENDER]}:'
                                f'\n{message[MESSAGE_TEXT]}')
                else:
                    self.LOGGER_CLIENT.error(f'Получено некорректное сообщение с сервера: {message}')
            except IncorrectDataRecivedError:
                self.LOGGER_CLIENT.error(f'Не удалось декодировать полученное сообщение.')
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError, json.JSONDecodeError):
                self.LOGGER_CLIENT.critical(f'Потеряно соединение с сервером.')
                break

    @log
    def get_args_parser(self):
        """
        Метод - парсер аргументов коммандной строки
        """
        parser = argparse.ArgumentParser(description='Client script')
        parser.add_argument('-a', default=DEFAULT_IP_ADDRESS, type=str, nargs='?',
                            help='Параметр -a позволяет указать IP-адрес сервера (по умолчанию localhost')
        parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?',
                            help='Параметр -p позволяет указать порт сервера (по умолчанию 7777)')
        parser.add_argument('-n', default=None, type=str, nargs='?',
                            help='Параметр -n позволяет указать имя пользователя')
        return parser

    @log
    def get_addr_port(self):
        """
        Определяем порт, на котором будет работать сервер, и адрес с которого будут поступать запросы на сервер.
        По умолчанию сервер будет принимать со всех адресов.
        """
        parser = self.get_args_parser()
        args = parser.parse_args(sys.argv[1:])
        self.ADDR = args.a
        self.PORT = args.p
        self.NAME = args.n
        if not 1023 < self.PORT < 65536:
            self.LOGGER_CLIENT.critical(f'Попытка запуска клиента с неподходящим номером порта сервера: {self.PORT}. '
                f'Допустимы адреса с 1024 до 65535. Для клиента будет установлен порт сервера: {DEFAULT_PORT}')
            print(f'Попытка запуска клиента с неподходящим номером порта сервера: {self.PORT}. '
                f'Допустимы адреса с 1024 до 65535. Для клиента будет установлен порт сервера: {DEFAULT_PORT}')
            self.PORT = DEFAULT_PORT

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
    def start_client(self):
        """
        Запуск клиента
        """

        # Сообщаем о запуске
        print('Консольный месседжер. Клиентский модуль.')
        # Получаем параметры подключения
        self.get_addr_port()
        # Если имя пользователя не было задано, необходимо запросить пользователя.
        if not self.NAME:
            self.NAME = input('Введите имя пользователя: ')

        self.LOGGER_CLIENT.info(f'Запущен клиент с парамертами: адрес сервера: {self.ADDR}, '
            f'порт: {self.PORT}, имя пользователя: {self.NAME}')

        # Инициализация сокета и сообщение серверу о нашем появлении
        try:
            self.TRANSPORT.connect((self.ADDR, self.PORT))
            self.send_message(self.TRANSPORT, self.create_presence_message(self.NAME))
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
            # Если соединение с сервером установлено корректно:

            # Запускаем клиенский процесс приёма сообщний
            receiver = threading.Thread(target=self.message_from_server, args=(self.TRANSPORT, self.NAME))
            receiver.daemon = True
            receiver.start()

            # Запускаем отправку сообщений и взаимодействие с пользователем
            user_interface = threading.Thread(target=self.user_interactive, args=(self.TRANSPORT, self.NAME))
            user_interface.daemon = True
            user_interface.start()
            self.LOGGER_CLIENT.debug('Запущены процессы')

            # Watchdog основной цикл, если один из потоков завершён, то значит или потеряно соединение или
            # пользователь ввёл exit
            # Поскольку все события обработываются в потоках, достаточно просто завершить цикл
            while True:
                time.sleep(1)
                if receiver.is_alive() and user_interface.is_alive():
                    continue
                break

    def run(self):
        self.start_client()


if __name__ == '__main__':
    client = Client()
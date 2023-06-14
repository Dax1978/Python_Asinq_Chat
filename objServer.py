import sys
import socket
import argparse
import logging
import select
import time
import json

from common.variables import DEFAULT_PORT, MAX_CONNECTIONS, ACTION, TIME, USER, ACCOUNT_NAME, SENDER, PRESENCE, \
    ERROR, MESSAGE, MESSAGE_TEXT, MAX_PACKAGE_LENGTH, ENCODING, RESPONSE_400, DESTINATION, RESPONSE_200, EXIT
from chat_utils.errors import IncorrectDataRecivedError, NonDictInputError
from logs.log_decos import log
import logs.log_config_server


sys.path.append('../')


class Server():
    def __init__(self):
        self.TRANSPORT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.LOGGER_SERVER = logging.getLogger('server')
        # Очередь ожидающих клиентов
        self.clients = []
        # Очередь сообщений
        self.messages = []
        # Словарь, содержащий имена пользователей и соответствующие им сокеты
        self.names = {}

        self.run()

    @log
    def get_args_parser(self):
        """
        Парсер аргументов коммандной строки
        """
        parser = argparse.ArgumentParser(description='Server script')
        parser.add_argument('-a', default='', type=str, nargs='?', help='Параметр -a позволяет указать IP-адрес, с которого будут приниматься соединения. (по умолчанию адрес не указан, ')
        parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?', help='Параметр -p позволяет указать порт сервера (по умолчанию 7777)')
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
        if not 1023 < self.PORT < 65536:
            self.LOGGER_SERVER.critical(f'Попытка запуска сервера с указанием неподходящего порта {self.PORT}. '
                f'Допустимы адреса с 1024 до 65535. Сервер будет запущен с порта по умолчанию {DEFAULT_PORT}')
            print(f'Попытка запуска сервера с указанием неподходящего порта {self.PORT}. '
                f'Допустимы адреса с 1024 до 65535. Сервер запущен с порта по умолчанию {DEFAULT_PORT}')
            self.PORT = DEFAULT_PORT
        else:
            self.LOGGER_SERVER.info(f'Запущен сервер, порт для подключений: {self.PORT}, адрес, с которого принимаются'
                f' подключения: {self.ADDR}. Если адрес не указан, принимаются соединения с любых адресов.')
            print(f'Запущен сервер...\nПорт для подключений: {self.PORT}, адрес с которого принимаются'
                f' подключения: {self.ADDR}. Если адрес не указан, принимаются соединения с любых адресов.')

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
    def process_client_message(self, message, client):
        """
        Обработчик сообщений от клиентов, принимает словарь - сообщение от клинта, проверяет корректность,
        отправляет словарь-ответ для клиента с результатом приёма
        :param message:
        :param messages_list:
        :param client:
        :return:
        """
        self.LOGGER_SERVER.debug(f'Разбор сообщения от клиента : {message}')
        # Если это сообщение о присутствии, принимаем и отвечаем, если успех
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
            # Если такой пользователь ещё не зарегистрирован,
            # регистрируем, иначе отправляем ответ и завершаем соединение
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                self.send_message(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя уже занято.'
                self.send_message(client, response)
                self.clients.remove(client)
                client.close()
            return
        # Если это сообщение, то добавляем его в очередь сообщений. Ответ не требуется.
        elif ACTION in message and message[ACTION] == MESSAGE and DESTINATION in message and TIME in message \
             and SENDER in message and MESSAGE_TEXT in message:
            self.messages.append(message)
            return
        # Если клиент выходит
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            self.clients.remove(self.names[message[ACCOUNT_NAME]])
            self.names[message[ACCOUNT_NAME]].close()
            del self.names[message[ACCOUNT_NAME]]
            return
        # Иначе отдаём Bad request
        else:
            response = RESPONSE_400
            response[ERROR] = 'Запрос некорректен.'
            self.send_message(client, response)
            return

    @log
    def process_message(self, message, names, listen_socks):
        """
        Метод адресной отправки сообщения определённому клиенту
        Принимает словарь сообщение, список зарегистрированых пользователей и слушающие сокеты
        Ничего не возвращает
        :param message:
        :param names:
        :param listen_socks:
        :return:
        """
        if message[DESTINATION] in names and names[message[DESTINATION]] in listen_socks:
            self.send_message(names[message[DESTINATION]], message)
            self.LOGGER_SERVER.info(f'Отправлено сообщение пользователю {message[DESTINATION]} '
                        f'от пользователя {message[SENDER]}.')
        elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
            raise ConnectionError
        else:
            self.LOGGER_SERVER.error( f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, '
                f'отправка сообщения невозможна.')

    @log
    def start_server(self):
        """
        Запуск сервера
        """
        self.get_addr_port()
        # Готовим сокет
        self.TRANSPORT.bind((self.ADDR, self.PORT))
        self.TRANSPORT.settimeout(0.7)
        self.TRANSPORT.listen(MAX_CONNECTIONS)

        # Основной цикл программы сервера
        while True:
            # Ждём подключения, если таймаут вышел, ловим исключение
            try:
                client, client_address = self.TRANSPORT.accept()
            except OSError:
                pass
            else:
                self.LOGGER_SERVER.info(f'Установлено соедение с ПК {client_address}')
                self.clients.append(client)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []

            # Проверяем на наличие ждущих клиентов
            try:
                if self.clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass

            # принимаем сообщения и если там есть сообщения, кладём в словарь, если ошибка, исключаем клиента.
            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        # print('client_with_message', client_with_message)
                        self.process_client_message(self.get_message(client_with_message), client_with_message)
                    except Exception:
                        self.LOGGER_SERVER.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                        self.clients.remove(client_with_message)

            # Если есть сообщения, обрабатываем каждое.
            for i in self.messages:
                try:
                    self.process_message(i, self.names, send_data_lst)
                except Exception:
                    self.LOGGER_SERVER.info(f'Связь с клиентом с именем {i[DESTINATION]} была потеряна')
                    self.clients.remove(self.names[i[DESTINATION]])
                    del self.names[i[DESTINATION]]
            self.messages.clear()

            # Если есть сообщения для отправки и ожидающие клиенты, отправляем им сообщение.
            # if self.messages and send_data_lst:
            #     message = {
            #         ACTION: MESSAGE,
            #         SENDER: self.messages[0][0],
            #         TIME: time.time(),
            #         MESSAGE_TEXT: self.messages[0][1]
            #     }
            #     del self.messages[0]
            #     for waiting_client in send_data_lst:
            #         try:
            #             self.send_message(waiting_client, message)
            #         except:
            #             self.LOGGER_SERVER.info(f'Клиент {waiting_client.getpeername()} отключился от сервера.')
            #             print(f'Клиент {waiting_client.getpeername()} отключился от сервера.')
            #             self.clients.remove(waiting_client)

    def run(self):
        self.start_server()


if __name__ == '__main__':
    server = Server()
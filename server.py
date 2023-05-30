import logging
from chat_utils import utils as chat_utils
from chat_utils import jim
import log.server_log_config


client_name = ''

logger = logging.getLogger('server')

if __name__ == '__main__':
    # initialize list/set of all connected client's sockets
    client_sockets = set()

    logger.debug('Сервер запущен...')

    parser = chat_utils.create_parser()
    namespace = parser.parse_args()

    sock = chat_utils.get_server_socket(namespace.addr, namespace.port)

    server_addr = sock.getsockname()
    start_info = f'Сервер запущен на {server_addr[0]}:{server_addr[1]}'
    print(start_info)
    logger.info(start_info)

    # Чисто теоретически это уже д.б. в while True:
    client, client_addr = sock.accept()
    client_info = f'Подключен клиент {client_addr[0]}:{client_addr[1]}'
    print(client_info)
    logger.info(client_info)

    while True:

        try:
            data_in = chat_utils.get_data(client)
            logger.info(
                f'Получены данные от клиента {client_addr} : {data_in}')
        except ConnectionResetError as e:
            logger.error(e)
            break

        if client_name == '':
            if data_in['action'] == 'presence' and data_in['user']['account_name'] != '':
                client_name = data_in['user']['account_name']
                jim.RESPONSE['response'], jim.RESPONSE['alert'] = jim.SERV_RESP[0]
                print(
                    f'{data_in["time"]} - {data_in["user"]["account_name"]}: {data_in["user"]["status"]}')
            else:
                jim.RESPONSE['response'], jim.RESPONSE['alert'] = jim.SERV_RESP[1]

        if client_name != '' and data_in['action'] == 'msg':
            print(f'{data_in["time"]} - {client_name}: {data_in["message"]}')
            jim.RESPONSE['response'], jim.RESPONSE['alert'] = jim.SERV_RESP[0]

            if data_in["message"] == 'exit':
                jim.RESPONSE['response'], jim.RESPONSE['alert'] = jim.SERV_RESP[2]

        data_out = jim.RESPONSE

        try:
            chat_utils.send_data(client, data_out)
            logger.info(
                f'Данные отправлены на клиент {client_addr} : {data_out}')
        except ConnectionResetError as e:
            logger.error(e)
            break

        if data_out['response'] != '200':
            client.close()
            break

    logger.debug('Сервер завершил работу...')

    sock.close()

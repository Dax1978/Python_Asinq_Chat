import logging
import chat_utils.utils as utils
import chat_utils.jim as jim
import log.client_log_config


logger = logging.getLogger('client')

if __name__ == '__main__':
    logger.debug('Клиент запущен...')
    client_name = input('Введите имя: ')

    parser = utils.create_parser()
    namespace = parser.parse_args()

    sock = utils.get_client_socket(namespace.addr, namespace.port)

    serv_addr = sock.getpeername()
    start_info = f'Подключение к серверу: {serv_addr[0]}:{serv_addr[1]}'
    print(start_info)
    logger.info(start_info)

    jim.PRESENCE['user']['account_name'] = client_name
    try:
        utils.send_data(sock, jim.PRESENCE)
        logger.info(
            f'Сообщение отправлено на сервер: {serv_addr} : {jim.PRESENCE}')
    except ConnectionResetError as e:
        logger.error(e)
        sock.close()
        exit(1)

    while True:
        try:
            data = utils.get_data(sock)
            logger.info(
                f'Получены данные с сервера: {serv_addr} : {data}')
        except ConnectionResetError as e:
            logger.error(e)
            break

        if data['response'] != '200':
            break

        msg = input(
            'Введите сообщение ("exit" для выхода): ')
        jim.MESSAGE['message'] = msg

        try:
            utils.send_data(sock, jim.MESSAGE)
            logger.info(
                f'Данные отправлены на сервер: {serv_addr} : {jim.MESSAGE}')
        except ConnectionResetError as e:
            logger.error(e)
            break

    logger.debug('Клиент завершил работу...')

    sock.close()

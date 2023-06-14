from ipaddress import ip_address
from subprocess import Popen, PIPE
from tabulate import tabulate


class MyPing():
    def __init__(self):
        self.__timeout = 500
        self.__requests = 1

    def setTimeout(self, timeout):
        self.__timeout = timeout

    def setRequests(self, n):
        self.__requests = n

    def host_ping(self, list_ip_addresses):
        """
        Метод, проверяющий доступность сетевых узлов.
        Параметры команды ping:
            -w интервал. Определяет в миллисекундах время ожидания получения сообщения с эхо-ответом, которое
            соответствует сообщению с эхо-запросом. Если сообщение с эхо-ответом не получено в пределах заданного
            интервала, то выдается сообщение об ошибке "Request timed out". Интервал по умолчанию равен 4000 (4 секунды)
            -n счетчик. Задает число отправляемых сообщений с эхо-запросом
        """
        results = {'Доступные узлы': "", 'Недоступные узлы': ""}  # словарь с результатами
        for address in list_ip_addresses:
            results = self.__ping(results, address)
        return results

    def __ping(self, results, ip):
        try:
            ip = ip_address(ip)
        # обойдем такие исключения
        # ValueError: 'yandex.ru' does not appear to be an IPv4 or IPv6 address хотя можно преобразовать доменное имя к ip-адресу
        except ValueError:
            print(f'Error: некорректное значение ip = {ip}')
        proc = Popen(f"ping {ip} -w {self.__timeout} -n {self.__requests}", shell=False, stdout=PIPE)
        proc.wait()
        # проверяем код завершения подпроцесса
        if proc.returncode == 0:
            results['Доступные узлы'] += f"{str(ip)}\n"
            res_string = f'{ip} - Узел доступен'
        else:
            results['Недоступные узлы'] += f"{str(ip)}\n"
            res_string = f'{ip} - Узел недоступен'
        print(res_string)
        return results

    def host_range_ping(self):
        while True:
            # запрос адреса
            start_ip = input('Введите ip адрес: ')
            try:
                # последний октет
                las_oct = int(start_ip.split('.')[3])
                break
            except Exception as e:
                print(e)

        while True:
            # запрос количества проверяемых адресов
            end_ip = input('Сколько адресов проверить?: ')
            if not end_ip.isnumeric():
                print('Необходимо ввести число: ')
            else:
                # по условию меняется только последний октет
                if (las_oct + int(end_ip)) > 254:
                    print(f"Можем менять только последний октет, т.е. "
                          f"максимальное число хостов для проверки: {254 - las_oct}")
                else:
                    break

        host_list = []
        # формируем список ip адресов
        [host_list.append(str(ip_address(start_ip) + x)) for x in range(int(end_ip))]
        # передаем список в функцию из задания 1 для проверки доступности
        results = self.host_ping(host_list)

        return results

    def host_range_ping_tab(self):
        # запрашиваем хосты, проверяем доступность, получаем словарь результатов
        res_dict = self.host_range_ping()
        print()
        # выводим в табличном виде
        print(tabulate([res_dict], headers='keys', tablefmt="pipe", stralign="center"))


if __name__ == '__main__':
    ip_addresses = ['yandex.ru', '2.2.2.2', '178.248.232.209', '192.168.0.101']
    my_ping = MyPing()
    print('Задание 1:')
    my_ping.host_ping(ip_addresses)
    print('---------------------------------------------------------------------------------------------------------\n')
    print('Задание 2:')
    my_ping.host_range_ping()
    print('---------------------------------------------------------------------------------------------------------\n')
    print('Задание 3:')
    my_ping.host_range_ping_tab()

import subprocess


def main():
    """Функция консольного меню запуска в отдельных процессах сервера и клиентов"""
    process = []

    while True:
        action = input('Выберите действие:\n'
            ' q - выход\n'
            ' s - запустить сервер\n'
            ' k - запустить клиенты\n'
            ' x - закрыть все окна\n'
            ' -> ')
        if action == 'q':
            break
        elif action == 's':
            # Запускаем сервер!
            process.append(
                subprocess.Popen(
                    ["venv/Scripts/python", "server.py"],
                    creationflags=subprocess.CREATE_NEW_CONSOLE))
            # process.append(subprocess.Popen('python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))
        elif action == 'k':
            print('Убедитесь, что на сервере зарегистрировано необходимо количество клиентов с паролем 123456')
            print('Первый запуск может быть достаточно долгим из-за генерации ключей!')
            clients_count = int(input('Введите количество тестовых клиентов для запуска: '))
            # Запускаем клиентов:
            for i in range(clients_count):
                process.append(
                    subprocess.Popen(
                        ["venv/Scripts/python", "client.py",  "-n", f"test{i + 1}", "-p", "123456"],
                        creationflags=subprocess.CREATE_NEW_CONSOLE))
                # process.append(subprocess.Popen(["venv/Scripts/python", f"client.py -n test{i + 1} -p 123456"], creationflags=subprocess.CREATE_NEW_CONSOLE))
                # process.append(subprocess.Popen(f'python client.py -n test{i + 1} -p 123456', creationflags=subprocess.CREATE_NEW_CONSOLE))
        elif action == 'x':
            while process:
                process.pop().kill()


if __name__ == '__main__':
    main()
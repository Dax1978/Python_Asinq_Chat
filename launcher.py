import subprocess

process = []

while True:
    action = input('Выберите действие: q - выход , s - запустить сервер , k - запустить клиенты, x - закрыть все окна: ')
    if action == 'q':
        break
    elif action == 's':
        # Запускаем сервер!
        # https://stackoverflow.com/questions/8052926/running-subprocess-within-different-virtualenv-with-python
        process.append(subprocess.Popen(["venv/Scripts/python", "server.py"], creationflags=subprocess.CREATE_NEW_CONSOLE))
        # process.append(subprocess.Popen('python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif action == 'k':
        clients_count = int(input('Введите количество тестовых клиентов для запуска: '))
        # Запускаем клиентов:
        for i in range(clients_count):
            process.append(subprocess.Popen(["venv/Scripts/python", "client.py"], creationflags=subprocess.CREATE_NEW_CONSOLE))
            # process.append(subprocess.Popen(f'["venv/Scripts/python", "client.py -n test{i + 1}"]', creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif action == 'x':
        while process:
            process.pop().kill()
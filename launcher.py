import subprocess

PROCESS = []

while True:
    ANSWER = input('Выберите действие: q - выход, '
                   's - запустить сервер и клиенты, x - закрыть все окна: ')

    if ANSWER == 'q':
        break
    elif ANSWER == 's':
        PROCESS.append(subprocess.Popen('python objServer.py',
                                        creationflags=subprocess.CREATE_NEW_CONSOLE))
        for i in range(2):
            PROCESS.append(subprocess.Popen('python objClient.py -m send',
                                            creationflags=subprocess.CREATE_NEW_CONSOLE))
        for i in range(5):
            PROCESS.append(subprocess.Popen('python objClient.py -m listen',
                                            creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif ANSWER == 'x':
        while PROCESS:
            VICTIM = PROCESS.pop()
            VICTIM.kill()

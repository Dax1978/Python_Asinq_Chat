# Выполнить пинг веб-ресурсов yandex.ru, youtube.com и преобразовать
# результаты из байтовового в строковый тип на кириллице

import subprocess


result: str = ''

ping = ['ping', 'yandex.ru']
subproc_ping = subprocess.Popen(ping, stdout=subprocess.PIPE)

for line in subproc_ping.stdout:
    result += line.decode('cp866')

ping = ['ping', 'youtube.com']
subproc_ping = subprocess.Popen(ping, stdout=subprocess.PIPE)
for line in subproc_ping.stdout:
    result += line.decode('cp866')

print(result.encode('utf-8').decode('utf-8'))

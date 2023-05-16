# Задание на закрепление знаний по модулю yaml.
# Написать скрипт, автоматизирующий сохранение данных в файле YAML-формата.
# Для этого:
#
# a. Подготовить данные для записи в виде словаря, в котором первому ключу
# соответствует список, второму — целое число, третьему — вложенный словарь,
# где значение каждого ключа — это целое число с юникод-символом,
# отсутствующим в кодировке ASCII (например, €);
#
# b. Реализовать сохранение данных в файл формата YAML — например, в файл file.yaml.
# При этом обеспечить стилизацию файла с помощью параметра default_flow_style,
# а также установить возможность работы с юникодом: allow_unicode = True;
#
# c. Реализовать считывание данных из созданного файла и проверить, совпадают
# ли они с исходными.

import os
import yaml


CURR_DIR = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(CURR_DIR, 'file.yaml')

data = {
    'items': ['вещь1', 'вещь2', 'вещь3'],
    'items_quantity': 7,
    'items_price': {
        'вещь1': '700₽',
        'вещь2': '700₽',
        'вещь3': '700₽'
    }
}

with open(filename, 'w', encoding='utf-8') as f:
    yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

with open(filename, encoding='utf-8') as f:
    out = yaml.load(f, Loader=yaml.SafeLoader)
    # print(out)

print('Соответствуют ли данные:', data == out)

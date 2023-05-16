# Задание на закрепление знаний по модулю json.
# Есть файл orders в формате JSON с информацией о заказах.
# Написать скрипт, автоматизирующий его заполнение данными.
# Для этого:
#
# a. Создать функцию write_order_to_json(), в которую
# передается 5 параметров — товар (item), количество (quantity),
# цена (price), покупатель (buyer), дата (date).
# Функция должна предусматривать запись данных в виде словаря в файл orders.json.
# При записи данных указать величину отступа в 4 пробельных символа;
#
# b. Проверить работу программы через вызов функции write_order_to_json()
# с передачей в нее значений каждого параметра.

import os
import json


CURR_DIR = os.path.dirname(os.path.abspath(__file__))


def write_order_to_json(item, quantity, price, buyer, date):
    filename = os.path.join(CURR_DIR, 'orders.json')
    data = {"orders": []}
    if os.path.exists(filename):
        with open(filename, encoding="utf-8") as f:
            data = json.loads(f.read())

    data['orders'].append({'item': item, 'quantity': quantity,
                           'price': price, 'buyer': buyer, 'date': date})

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, separators=(
            ',', ': '), ensure_ascii=False)


if __name__ == '__main__':
    write_order_to_json('Плита дорожная', '100',
                        '27000', 'Титаева', '17.05.2022')
    write_order_to_json('DJI Mavic 3 PRO', '1', '500000',
                        'Хохлов', '17.05.2023')

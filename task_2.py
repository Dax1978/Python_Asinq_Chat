# Каждое из слов «class», «function», «method» записать в байтовом типе
# без преобразования в последовательность кодов
# (не используя методы encode и decode) и определить тип,
# содержимое и длину соответствующих переменных

from typing import List
import binascii


l_str: List[str] = [b'class', b'function', b'method']
for st in l_str:
    print(
        f'Тип: {type(st)}, Содержимое: {binascii.hexlify(st)}, Длина: {len(st)}')

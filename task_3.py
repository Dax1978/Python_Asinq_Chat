# Определить, какие из слов «attribute», «класс», «функция», «type»
# невозможно записать в байтовом типе

st1 = b'attribute'
st2 = b'класс'
st3 = b'функция'
st4 = 'type'

#     File "...\task_3.py", line 5
#     st2 = b'класс'
#                        ^
# SyntaxError: bytes can only contain ASCII literal characters
#
#   File "...\task_3.py", line 6
#     st3 = b'функция'
#                            ^
# SyntaxError: bytes can only contain ASCII literal characters
# 
# Ошибки преобразования (стр. 13)
# 1. Отсутствие в кодировке механизма преобразования данных из одного
# формата в другой
# Преобразовать слова «разработка», «администрирование», «protocol»,
# «standard» из строкового представления в байтовое и выполнить обратное
# преобразование (используя методы encode и decode)

from typing import List
import chardet


l_str: List[str] = ['разработка', 'сокет', 'декоратор']
l_str_b = []

print('----- Часть 1 -----')
for st in l_str:
    st = st.encode('utf-8', errors='namereplace')
    l_str_b.append(st)
    print(st)

print('----- Часть 2 -----')
for bt in l_str_b:
    print(bt.decode('ascii', errors='replace'))
    print(bt.decode(chardet.detect(bt)['encoding']))

# Создать текстовый файл test_file.txt, заполнить его тремя строками:
# «сетевое программирование», «сокет», «декоратор».
# Проверить кодировку файла по умолчанию.
# Принудительно открыть файл в формате Unicode и вывести его содержимое

import locale
import chardet


print('----- Часть 1 -----')
print(locale.getpreferredencoding())
# OUT:
# cp1251

print('----- Часть 2 -----')
with open(r'test_file.txt', 'rb') as f:
    data = f.read()
    print(data)
    print(chardet.detect(data))
# OUT:
b'\xd1\x81\xd0\xb5\xd1\x82\xd0\xb5\xd0\xb2\xd0\xbe\xd0\xb5 \xd0\xbf\xd1\x80\xd0\xbe\xd0\xb3\xd1\x80\xd0\xb0\xd0\xbc\xd0\xbc\xd0\xb8\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5\r\n\xd1\x81\xd0\xbe\xd0\xba\xd0\xb5\xd1\x82\r\n\xd0\xb4\xd0\xb5\xd0\xba\xd0\xbe\xd1\x80\xd0\xb0\xd1\x82\xd0\xbe\xd1\x80'
{'encoding': 'utf-8', 'confidence': 0.99, 'language': ''}

print('----- Часть 3 -----')
with open(r'test_file.txt', encoding='utf-8', errors='replace') as f:
    print(f.read())
# OUT:
# сетевое программирование
# сокет
# декоратор

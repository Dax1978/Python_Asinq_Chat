# Задание на закрепление знаний по модулю CSV.
# Написать скрипт, осуществляющий выборку определенных данных из
# файлов info_1.txt, info_2.txt, info_3.txt и формирующий новый
# «отчетный» файл в формате CSV. Для этого:
#
# a. Создать функцию get_data(), в которой в цикле осуществляется
# перебор файлов с данными, их открытие и считывание данных.
# В этой функции из считанных данных необходимо с помощью регулярных
# выражений извлечь значения параметров «Изготовитель системы»,
# «Название ОС», «Код продукта», «Тип системы».
# Значения каждого параметра поместить в соответствующий список.
# Должно получиться четыре списка — например, os_prod_list, os_name_list,
# os_code_list, os_type_list.
# В этой же функции создать главный список для хранения данных отчета —
# например, main_data — и поместить в него названия столбцов отчета
# в виде списка:
# «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
# Значения для этих столбцов также оформить в виде списка и поместить
# в файл main_data (также для каждого файла);
# 
# b. Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл.
# В этой функции реализовать получение данных через вызов функции get_data(),
# а также сохранение подготовленных данных в соответствующий CSV-файл;
# 
# c. Проверить работу программы через вызов функции write_to_csv()

import os, re, csv


CURR_DIR = os.path.dirname(os.path.abspath(__file__))

def get_data():
    os_prod_list, os_name_list, os_code_list, os_type_list = [], [], [], []
    main_data = [['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']]
    result = []
    
    files = os.listdir(CURR_DIR)
    for i in range(1, 4):
        filename = f'info_{i}.txt'
        if (filename in files):
            full_filename = os.path.join(CURR_DIR, filename)
            # file_obj = open(full_filename)
            with open(full_filename) as f:
                for line in f.readlines():
                    result += re.findall(r'^(\w[^:]+).*:\s+([^:\n]+)\s*$', line)
    for item in result:
        os_prod_list.append(item[1]) if item[0] == main_data[0][0] else None
        os_name_list.append(item[1]) if item[0] == main_data[0][1] else None
        os_code_list.append(item[1]) if item[0] == main_data[0][2] else None
        os_type_list.append(item[1]) if item[0] == main_data[0][3] else None

    for i in range(len(os_prod_list)):
        main_data.append([os_prod_list[i], os_name_list[i], os_code_list[i], os_type_list[i]])
    
    return main_data

def write_to_csv(filename):
    data = get_data()

    with open(filename, 'w', encoding='utf-8', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
        for line in data:
            writer.writerow(line)

if __name__ == '__main__':
    filename_csv = os.path.join(CURR_DIR, 'report.csv')
    write_to_csv(filename_csv)


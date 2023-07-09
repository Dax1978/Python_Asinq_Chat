Client module documentation
=================================================

Клиентское приложение для обмена сообщениями
Поддерживает отправку сообщений пользователям которые находятся в сети, сообщения шифруются
с помощью алгоритма RSA с длинной ключа 2048 bit

Поддерживает аргументы коммандной строки:

``python client.py {имя сервера} {порт} -n или --name {имя пользователя} -p или -password {пароль}``

1. {имя сервера} - адрес сервера сообщений
2. {порт} - порт по которому принимаются подключения
3. -n или --name - имя пользователя с которым произойдёт вход в систему
4. -p или --password - пароль пользователя

Все опции командной строки являются необязательными, но имя пользователя и пароль необходимо обязательно использовать в паре

Примеры использования:

* ``python client.py``

*Запуск приложения с параметрами по умолчанию.*

* ``python client.py ip_address some_port``

*Запуск приложения с указанием подключаться к серверу по адресу ip_address:port*

* ``python -n test1 -p 123456``

*Запуск приложения с пользователем test1 и паролем 123456*

* ``python client.py ip_address some_port -n test1 -p 123456``

*Запуск приложения с пользователем test1 и паролем 123456 и указанием подключаться к серверу по адресу ip_address:port*

.. image:: ../img/client_test1.png

.. image:: ../img/client_test2.png

client.py
~~~~~~~~~

Запускаемый модуль, содержит функционал инициализации приложения, а также парсер переданных аргументов командной строки

client. **arg_parser** ()
    Парсер аргументов командной строки, возвращает кортеж из 4 элементов:

	* адрес сервера
	* порт
	* имя пользователя
	* пароль

    Выполняет проверку на корректность номера порта


database.py
~~~~~~~~~~~~~~

.. autoclass:: client.database.ClientDatabase
	:members:

transport.py
~~~~~~~~~~~~~~

.. autoclass:: client.transport.ClientTransport
	:members:

main_window.py
~~~~~~~~~~~~~~

.. autoclass:: client.ui_main_window.ClientMainWindow
	:members:

start_dialog.py
~~~~~~~~~~~~~~~

.. autoclass:: client.ui_start.UserNameDialog
	:members:


add_contact.py
~~~~~~~~~~~~~~

.. autoclass:: client.ui_add_contact.AddContactDialog
	:members:


del_contact.py
~~~~~~~~~~~~~~

.. autoclass:: client.ui_del_contact.DelContactDialog
	:members:
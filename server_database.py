import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from server_models import Base, AllUsers, ActiveUsers, LoginHistory, UsersContacts, UsersHistory
from common.variables import *


# Класс - серверная база данных:
class ServerStorage:
    def __init__(self, path):
        # Создаём движок базы данных
        # print(path)
        self.database_engine = create_engine(f'sqlite:///{path}', echo=False, pool_recycle=7200,
                                             connect_args={'check_same_thread': False})

        # Создаём таблицы
        Base.metadata.create_all(bind=self.database_engine)

        # Создаём сессию
        self.session = Session(bind=self.database_engine)

        # Если в таблице активных пользователей есть записи, то их необходимо удалить
        self.session.query(ActiveUsers).delete()
        self.session.commit()


    # Функция выполняющяяся при входе пользователя, записывает в базу факт входа
    def user_login(self, username, ip_address, port):
        # Запрос в таблицу пользователей на наличие там пользователя с таким именем
        rez = self.session.query(AllUsers).filter_by(name=username)

        # Если имя пользователя уже присутствует в таблице, обновляем время последнего входа
        if rez.count():
            user = rez.first()
            user.last_login = datetime.datetime.now()
        # Если нету, то создаздаём нового пользователя
        else:
            user = AllUsers(username)
            self.session.add(user)
            # Комит здесь нужен, чтобы присвоился ID
            self.session.commit()
            user_in_history = UsersHistory(user.id)
            self.session.add(user_in_history)

        # Теперь можно создать запись в таблицу активных пользователей о факте входа.
        new_active_user = ActiveUsers(user.id, ip_address, port, datetime.datetime.now())
        self.session.add(new_active_user)

        # и сохранить в историю входов
        history = LoginHistory(user.id, datetime.datetime.now(), ip_address, port)
        self.session.add(history)

        # Сохрраняем изменения
        self.session.commit()

    # Функция фиксирующая отключение пользователя
    def user_logout(self, username):
        # Запрашиваем пользователя, что покидает нас
        user = self.session.query(AllUsers).filter_by(name=username).first()
        # Удаляем его из таблицы активных пользователей.
        self.session.query(ActiveUsers).filter_by(user=user.id).delete()
        # Применяем изменения
        self.session.commit()

    # Функция фиксирует передачу сообщения и делает соответствующие отметки в БД
    def process_message(self, sender, recipient):
        # Получаем ID отправителя и получателя
        sender = self.session.query(AllUsers).filter_by(name=sender).first().id
        recipient = self.session.query(AllUsers).filter_by(name=recipient).first().id
        # Запрашиваем строки из истории и увеличиваем счётчики
        sender_row = self.session.query(UsersHistory).filter_by(user=sender).first()
        sender_row.sent += 1
        recipient_row = self.session.query(UsersHistory).filter_by(user=recipient).first()
        recipient_row.accepted += 1

        self.session.commit()

    # Функция добавляет контакт для пользователя.
    def add_contact(self, user, contact):
        # Получаем ID пользователей
        user = self.session.query(AllUsers).filter_by(name=user).first()
        contact = self.session.query(AllUsers).filter_by(name=contact).first()

        # Проверяем что не дубль и что контакт может существовать (полю пользователь мы доверяем)
        if not contact or self.session.query(UsersContacts).filter_by(user=user.id, contact=contact.id).count():
            return

        # Создаём объект и заносим его в базу
        contact_row = UsersContacts(user.id, contact.id)
        self.session.add(contact_row)
        self.session.commit()

    # Функция удаляет контакт из базы данных
    def remove_contact(self, user, contact):
        # Получаем ID пользователей
        user = self.session.query(AllUsers).filter_by(name=user).first()
        contact = self.session.query(AllUsers).filter_by(name=contact).first()

        # Проверяем что контакт может существовать (полю пользователь мы доверяем)
        if not contact:
            return

        # Удаляем требуемое
        print(self.session.query(UsersContacts).filter(
            UsersContacts.user == user.id,
            UsersContacts.contact == contact.id
        ).delete())
        self.session.commit()

    # Функция возвращает список известных пользователей со временем последнего входа.
    def users_list(self):
        # Запрос строк таблицы пользователей.
        query = self.session.query(
            AllUsers.name,
            AllUsers.last_login
        )
        # Возвращаем список кортежей
        return query.all()

    # Функция возвращает список активных пользователей
    def active_users_list(self):
        # Запрашиваем соединение таблиц и собираем кортежи имя, адрес, порт, время.
        query = self.session.query(
            AllUsers.name,
            ActiveUsers.ip_address,
            ActiveUsers.port,
            ActiveUsers.login_time
        ).join(AllUsers)
        # Возвращаем список кортежей
        return query.all()

    # Функция возвращающаяя историю входов по пользователю или всем пользователям
    def login_history(self, username=None):
        # Запрашиваем историю входа
        query = self.session.query(AllUsers.name,
                                   LoginHistory.date_time,
                                   LoginHistory.ip,
                                   LoginHistory.port
                                   ).join(AllUsers)
        # Если было указано имя пользователя, то фильтруем по нему
        if username:
            query = query.filter(AllUsers.name == username)
        # Возвращаем список кортежей
        return query.all()

    # Функция возвращает список контактов пользователя.
    def get_contacts(self, username):
        # Запрашивааем указанного пользователя
        user = self.session.query(AllUsers).filter_by(name=username).one()

        # Запрашиваем его список контактов
        query = self.session.query(UsersContacts, AllUsers.name).filter_by(user=user.id). \
            join(AllUsers, UsersContacts.contact == AllUsers.id)

        # выбираем только имена пользователей и возвращаем их.
        return [contact[1] for contact in query.all()]

    # Функция возвращает количество переданных и полученных сообщений
    def message_history(self):
        query = self.session.query(
            AllUsers.name,
            AllUsers.last_login,
            UsersHistory.sent,
            UsersHistory.accepted
        ).join(AllUsers)
        # Возвращаем список кортежей
        return query.all()


# Отладка
if __name__ == '__main__':
    test_db = ServerStorage('test.sqlite3')
    test_db.user_login('1111', '192.168.1.113', 8080)
    test_db.user_login('McG2', '192.168.1.113', 8081)
    print(test_db.users_list())
    print(test_db.active_users_list())
    test_db.user_logout('McG2')
    print(test_db.login_history('re'))
    test_db.add_contact('test2', 'test1')
    test_db.add_contact('test1', 'test3')
    test_db.add_contact('test1', 'test6')
    test_db.remove_contact('test1', 'test3')
    test_db.process_message('McG2', '1111')
    print(test_db.message_history())
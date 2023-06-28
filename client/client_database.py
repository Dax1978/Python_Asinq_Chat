import os
import sys
import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from common.variables import *
from client.client_models import Base, Contacts, KnownUsers, MessageHistory

sys.path.append('../')


# Класс - база данных сервера.
class ClientDatabase:
    # Конструктор класса:
    def __init__(self, name):
        # Создаём движок базы данных, поскольку разрешено несколько клиентов одновременно, каждый должен иметь свою БД
        # Поскольку клиент мультипоточный необходимо отключить проверки на подключения с разных потоков,
        # иначе sqlite3.ProgrammingError
        path = os.path.dirname(os.path.realpath(__file__))
        filename = f'client_{name}.sqlite3'
        self.database_engine = create_engine(f'sqlite:///{os.path.join(path, filename)}', echo=False, pool_recycle=7200,
                                             connect_args={'check_same_thread': False})

        # Создаём таблицы
        Base.metadata.create_all(bind=self.database_engine)

        # Создаём сессию
        self.session = Session(bind=self.database_engine)

        # Необходимо очистить таблицу контактов, т.к. при запуске они подгружаются с сервера.
        self.session.query(Contacts).delete()
        self.session.commit()

    # Функция добавления контактов
    def add_contact(self, contact):
        if not self.session.query(Contacts).filter_by(name=contact).count():
            contact_row = Contacts(contact)
            self.session.add(contact_row)
            self.session.commit()

    # Функция удаления контакта
    def del_contact(self, contact):
        self.session.query(Contacts).filter_by(name=contact).delete()

    # Функция добавления известных пользователей.
    # Пользователи получаются только с сервера, поэтому таблица очищается.
    def add_users(self, users_list):
        self.session.query(KnownUsers).delete()
        for user in users_list:
            user_row = KnownUsers(user)
            self.session.add(user_row)
        self.session.commit()

    # Функция сохраняющяя сообщения
    def save_message(self, contact, direction, message):
        message_row = MessageHistory(contact, direction, message)
        self.session.add(message_row)
        self.session.commit()

    # Функция возвращающяя контакты
    def get_contacts(self):
        return [contact[0] for contact in self.session.query(Contacts.name).all()]

    # Функция возвращающяя список известных пользователей
    def get_users(self):
        return [user[0] for user in self.session.query(KnownUsers.username).all()]

    # Функция проверяющяя наличие пользователя в известных
    def check_user(self, user):
        if self.session.query(KnownUsers).filter_by(username=user).count():
            return True
        else:
            return False

    # Функция проверяющяя наличие пользователя контактах
    def check_contact(self, contact):
        if self.session.query(Contacts).filter_by(name=contact).count():
            return True
        else:
            return False

    # Функция возвращающая историю переписки
    def get_history(self, contact):
        query = self.session.query(MessageHistory).filter_by(contact=contact)
        return [(history_row.contact, history_row.direction, history_row.message, history_row.date)
                for history_row in query.all()]


# отладка
if __name__ == '__main__':
    test_db = ClientDatabase('test1')
    for i in ['test3', 'test4', 'test5']:
       test_db.add_contact(i)
    test_db.add_contact('test4')
    test_db.add_users(['test1', 'test2', 'test3', 'test4', 'test5'])
    test_db.save_message('test2', 'in', f'Привет! я тестовое сообщение от {datetime.datetime.now()}!')
    test_db.save_message('test2', 'out', f'Привет! я другое тестовое сообщение от {datetime.datetime.now()}!')
    print(test_db.get_contacts())
    print(test_db.get_users())
    print(test_db.check_user('test1'))
    print(test_db.check_user('test10'))
    print(sorted(test_db.get_history('test2') , key=lambda item: item[3]))
    test_db.del_contact('test4')
    print(test_db.get_contacts())

    """ Test OK """

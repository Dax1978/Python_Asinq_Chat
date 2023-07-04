import os
import sys
import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from common.variables import *
from client.client_models import Base, Contacts, KnownUsers, MessageHistory

sys.path.append('../')


class ClientDatabase:
    '''
    Класс - оболочка для работы с базой данных клиента
    Использует SQLite базу данных, реализован с помощью SQLAlchemy ORM и используется классический подход
    '''
    def __init__(self, name: str):
        # Создаём движок базы данных, поскольку разрешено несколько клиентов одновременно, каждый должен иметь свою БД
        # Поскольку клиент мультипоточный необходимо отключить проверки на подключения с разных потоков,
        # иначе sqlite3.ProgrammingError
        path = os.path.dirname(os.path.realpath(__file__))
        filename = f'client_{name}.sqlite3'
        self.database_engine = create_engine(
            f'sqlite:///{os.path.join(path, filename)}',
            echo=False,
            pool_recycle=7200,
            connect_args={
                'check_same_thread': False
            }
        )

        # Создаём таблицы
        Base.metadata.create_all(bind=self.database_engine)
        # Создаём сессию
        self.session = Session(bind=self.database_engine)
        # Необходимо очистить таблицу контактов, т.к. при запуске они подгружаются с сервера
        self.session.query(Contacts).delete()
        self.session.commit()

    def add_contact(self, contact: str) -> None:
        '''Метод добавляющий контакт в базу данных'''
        if not self.session.query(Contacts).filter_by(name=contact).count():
            contact_row = Contacts(contact)
            self.session.add(contact_row)
            self.session.commit()

    def contacts_clear(self):
        '''Метод очищающий таблицу со списком контактов'''
        self.session.query(Contacts).delete()

    def del_contact(self, contact: str) -> None:
        '''Метод удаляющий определённый контакт из базы даных'''
        self.session.query(Contacts).filter_by(name=contact).delete()

    def add_users(self, users_list: list[str]) -> None:
        '''Метод заполняющий таблицу известных пользователей'''
        self.session.query(KnownUsers).delete()
        for user in users_list:
            user_row: KnownUsers = KnownUsers(user)
            self.session.add(user_row)
        self.session.commit()

    def save_message(self, contact, direction, message):
        '''Метод сохраняющий сообщение в базе данных'''
        message_row = MessageHistory(contact, direction, message)
        self.session.add(message_row)
        self.session.commit()

    def get_contacts(self):
        '''Метод возвращающий список всех контактов'''
        return [contact[0] for contact in self.session.query(Contacts.name).all()]

    def get_users(self):
        '''Метод возвращающий список всех известных пользователей'''
        return [user[0] for user in self.session.query(KnownUsers.username).all()]

    def check_user(self, user: str) -> bool:
        '''Метод проверяющий существует ли пользователь'''
        if self.session.query(KnownUsers).filter_by(username=user).count():
            return True
        else:
            return False

    def check_contact(self, contact: str) -> bool:
        '''Метод проверяющий существует ли контакт'''
        if self.session.query(Contacts).filter_by(name=contact).count():
            return True
        else:
            return False

    def get_history(self, contact: str):
        '''Метод возвращающий историю сообщений с определённым пользователем'''
        query = self.session.query(MessageHistory).filter_by(contact=contact)
        return [
            (
                history_row.contact,
                history_row.direction,
                history_row.message,
                history_row.date
            )
            for history_row in query.all()
        ]


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

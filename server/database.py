import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from server.server_models import Base, AllUsers, ActiveUsers, LoginHistory, UsersContacts, UsersHistory
from sqlalchemy.sql import default_comparator


class ServerStorage:
    '''
    Класс - оболочка для работы с базой данных сервера.
    Использует SQLite базу данных, реализован с помощью SQLAlchemy ORM и используется классический подход.
    '''
    def __init__(self, path):
        # Создаём движок базы данных
        # print(path)
        self.database_engine = create_engine(f'sqlite:///{path}', echo=False, pool_recycle=7200, connect_args={'check_same_thread': False})

        # Создаём таблицы
        Base.metadata.create_all(bind=self.database_engine)

        # Создаём сессию
        self.session = Session(bind=self.database_engine)

        # Если в таблице активных пользователей есть записи, то их необходимо удалить
        self.session.query(ActiveUsers).delete()
        self.session.commit()

    # Функция выполняющяяся при входе пользователя, записывает в базу факт входа
    def user_login(self, username, ip_address, port, key):
        '''
        Метод выполняющийся при входе пользователя, записывает в базу факт входа
        Обновляет открытый ключ пользователя при его изменении
        '''
        # Запрос в таблицу пользователей на наличие там пользователя с таким именем
        rez = self.session.query(AllUsers).filter_by(name=username)

        # Если имя пользователя уже присутствует в таблице, обновляем время последнего входа и проверяем корректность ключа
        # Если клиент прислал новый ключ, сохраняем его
        if rez.count():
            user = rez.first()
            user.last_login = datetime.datetime.now()
            if user.pubkey != key:
                user.pubkey = key
        # Если нету, то генерируем исключение
        else:
            raise ValueError('Пользователь не зарегистрирован.')

        # Теперь можно создать запись в таблицу активных пользователей о факте входа.
        new_active_user = ActiveUsers(user.id, ip_address, port, datetime.datetime.now())
        self.session.add(new_active_user)

        # и сохранить в историю входов
        history = LoginHistory(user.id, datetime.datetime.now(), ip_address, port)
        self.session.add(history)

        # Сохрраняем изменения
        self.session.commit()

    def add_user(self, name, passwd_hash):
        ''' Метод регистрации пользователя. Принимает имя и хэш пароля, создаёт запись в таблице статистики'''
        user_row = AllUsers(name, passwd_hash)
        self.session.add(user_row)
        self.session.commit()
        history_row = UsersHistory(user_row.id)
        self.session.add(history_row)
        self.session.commit()

    def remove_user(self, name):
        '''Метод удаляющий пользователя из базы.'''
        user = self.session.query(AllUsers).filter_by(name=name).first()
        self.session.query(ActiveUsers).filter_by(user=user.id).delete()
        self.session.query(LoginHistory).filter_by(name=user.id).delete()
        self.session.query(UsersContacts).filter_by(user=user.id).delete()
        self.session.query(UsersContacts).filter_by(contact=user.id).delete()
        self.session.query(UsersHistory).filter_by(user=user.id).delete()
        self.session.query(AllUsers).filter_by(name=name).delete()
        self.session.commit()

    def get_hash(self, name):
        '''Метод получения хэша пароля пользователя'''
        user = self.session.query(AllUsers).filter_by(name=name).first()
        return user.passwd_hash

    def get_pubkey(self, name):
        '''Метод получения публичного ключа пользователя'''
        user = self.session.query(AllUsers).filter_by(name=name).first()
        return user.pubkey

    def check_user(self, name):
        '''Метод проверяющий существование пользователя'''
        if self.session.query(AllUsers).filter_by(name=name).count():
            return True
        else:
            return False

    def user_logout(self, username):
        '''Метод фиксирующий отключения пользователя'''
        # Запрашиваем пользователя, что покидает нас
        user = self.session.query(AllUsers).filter_by(name=username).first()
        # Удаляем его из таблицы активных пользователей
        self.session.query(ActiveUsers).filter_by(user=user.id).delete()
        # Применяем изменения
        self.session.commit()

    def process_message(self, sender, recipient):
        '''Метод записывающий в таблицу статистики факт передачи сообщения'''
        # Получаем ID отправителя и получателя
        sender = self.session.query(AllUsers).filter_by(name=sender).first().id
        recipient = self.session.query(AllUsers).filter_by(name=recipient).first().id
        # Запрашиваем строки из истории и увеличиваем счётчики
        sender_row = self.session.query(UsersHistory).filter_by(user=sender).first()
        sender_row.sent += 1
        recipient_row = self.session.query(UsersHistory).filter_by(user=recipient).first()
        recipient_row.accepted += 1

        self.session.commit()

    def add_contact(self, user, contact):
        '''Метод добавления контакта для пользователя.'''
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

    def remove_contact(self, user, contact):
        '''Метод удаления контакта пользователя'''
        # Получаем ID пользователей
        user = self.session.query(AllUsers).filter_by(name=user).first()
        contact = self.session.query(AllUsers).filter_by(name=contact).first()

        # Проверяем что контакт может существовать (полю пользователь мы доверяем)
        if not contact:
            return

        # Удаляем требуемое
        self.session.query(UsersContacts).filter(UsersContacts.user == user.id, UsersContacts.contact == contact.id).delete()
        self.session.commit()

    def users_list(self):
        '''Метод возвращающий список известных пользователей со временем последнего входа'''
        # Запрос строк таблицы пользователей.
        query = self.session.query(AllUsers.name, AllUsers.last_login)
        # Возвращаем список кортежей
        return query.all()

    def active_users_list(self):
        '''Метод возвращающий список активных пользователей'''
        # Запрашиваем соединение таблиц и собираем кортежи имя, адрес, порт, время.
        query = self.session.query(
            AllUsers.name,
            ActiveUsers.ip_address,
            ActiveUsers.port,
            ActiveUsers.login_time
        ).join(AllUsers)
        # Возвращаем список кортежей
        return query.all()

    def login_history(self, username=None):
        '''Метод возвращающий историю входов'''
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

    def get_contacts(self, username):
        '''Метод возвращающий список контактов пользователя'''
        # Запрашивааем указанного пользователя
        user = self.session.query(AllUsers).filter_by(name=username).one()

        # Запрашиваем его список контактов
        query = self.session.query(UsersContacts, AllUsers.name).filter_by(user=user.id). \
            join(AllUsers, UsersContacts.contact == AllUsers.id)

        # выбираем только имена пользователей и возвращаем их.
        return [contact[1] for contact in query.all()]

    def message_history(self):
        '''Метод возвращающий статистику сообщений'''
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
    test_db = ServerStorage('../server_database.db3')
    test_db.user_login('test1', '192.168.1.113', 8080)
    test_db.user_login('test2', '192.168.1.113', 8081)
    print(test_db.users_list())
    # print(test_db.active_users_list())
    # test_db.user_logout('McG')
    # print(test_db.login_history('re'))
    # test_db.add_contact('test2', 'test1')
    # test_db.add_contact('test1', 'test3')
    # test_db.add_contact('test1', 'test6')
    # test_db.remove_contact('test1', 'test3')
    test_db.process_message('test1', 'test2')
    print(test_db.message_history())
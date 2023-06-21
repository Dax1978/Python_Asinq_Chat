import datetime
from typing import Iterable

from sqlalchemy import create_engine
from sqlalchemy import delete
from sqlalchemy import Delete
from sqlalchemy import Select
from sqlalchemy import select
from sqlalchemy import Row
from sqlalchemy.orm import Session

from common.variables import SQLALCHEMY_URL_SERVER, SQLALCHEMY_ECHO
from models import Base, AllUsers, ActiveUsers, LoginHistory


# Класс - серверная база данных:
class ServerStorage:
    def __init__(self):
        # Создаём движок базы данных
        # pool_recycle - По умолчанию соединение с БД через 8 часов простоя обрывается.
        # Чтобы это не случилось нужно добавить опцию pool_recycle = 7200 (переуст-ка соед-я через 2 часа)
        self.database_engine = create_engine(SQLALCHEMY_URL_SERVER, echo=SQLALCHEMY_ECHO, pool_recycle=7200)
        # Создаём таблицы
        Base.metadata.create_all(bind=self.database_engine)
        # Создаём сессию
        self.session = Session(bind=self.database_engine)
        # Если в таблице активных пользователей есть записи, то их необходимо удалить
        # Когда устанавливаем соединение, очищаем таблицу активных пользователей
        stmt: Delete = delete(ActiveUsers)
        self.session.execute(stmt)
        # stmt = delete(User).where(User.name == name)
        # self.session.query(ActiveUsers).delete()
        self.session.commit()

    def user_login(self, username, ip_address, port) -> None:
        """
        Метод, выполняющийся при входе пользователя, записывает в базу факт входа
        """
        # print("user_login:", username, ip_address, port)
        # Запрос в таблицу пользователей на наличие там пользователя с таким именем
        stmt: Select = select(AllUsers).filter_by(name=username)
        # rez = self.session.scalars(stmt).all()
        rez: Iterable[AllUsers] = self.session.scalars(stmt).all()
        # rez = self.session.scalars(stmt).all()
        # stmt = select(User).where(User.name == username)
        # rez: Iterable[AllUsers] = self.session.scalars(stmt)
        # rez = self.session.execute(stmt).all()
        # rez = self.session.query(User).filter_by(name=username)
        # print('rez', type(rez))
        # print(rez)
        # Если имя пользователя уже присутствует в таблице, обновляем время последнего входа
        if len(list(rez)):
            # user = rez.first()
            user: AllUsers = list(rez)[0]
            user.last_login = datetime.datetime.now()
        # # Если нет, то создаздаём нового пользователя
        else:
            # Создаем экземпляр класса self.AllUsers, через который передаем данные в таблицу
            user = AllUsers(name=username)
            self.session.add(user)
            # Комит здесь нужен, чтобы присвоился ID
            self.session.commit()

        # Теперь можно создать запись в таблицу активных пользователей о факте входа.
        # Создаем экземпляр класса self.ActiveUsers, через который передаем данные в таблицу
        new_active_user = ActiveUsers(
            user_id=user.id,
            ip_address=ip_address,
            port=port,
            login_time=datetime.datetime.now()
        )
        self.session.add(new_active_user)

        # и сохранить в историю входов
        # Создаем экземпляр класса self.LoginHistory, через который передаем данные в таблицу
        history = LoginHistory(user_id=user.id, date_time=datetime.datetime.now(), ip_address=ip_address, port=port)
        self.session.add(history)

        # Сохраняем изменения
        self.session.commit()

    def user_logout(self, username) -> None:
        """
        Метод, фиксирующий отключение пользователя
        """
        # Запрашиваем пользователя, что покидает нас
        # получаем запись из таблицы AllUsers
        stmt: Select = select(AllUsers).filter_by(name=username)
        user: AllUsers = self.session.scalar(stmt)
        # user: AllUsers = self.session.scalars(stmt).first()
        # user = self.session.query(AllUsers).filter_by(name=username).first()
        # получаем запись из таблицы ActiveUsers
        active_user: ActiveUsers = self.session.scalar(select(ActiveUsers).filter_by(user_id=user.id))
        self.session.delete(active_user)

        # Так тоже работает, но это "кандовый" способ, не 2.0
        # # Запрашиваем пользователя, что покидает нас
        # # получаем запись из таблицы AllUsers
        # stmt: Select = select(AllUsers).filter_by(name=username)
        # user: AllUsers = self.session.scalar(stmt)
        # # Удаляем его из таблицы активных пользователей.
        # # Удаляем запись из таблицы ActiveUsers
        # stmt: Select = delete(ActiveUsers).filter_by(user_id=user.id)
        # self.session.execute(stmt)

        # Применяем изменения
        self.session.commit()

    def users_list(self) -> Iterable[Row]:
        """
        Метод возвращает список известных пользователей со временем последнего входа
        """
        # query = self.session.query(
        #     AllUsers.name,
        #     AllUsers.last_login,
        # )
        # users: list[AllUsers] = self.session.scalars(select(AllUsers)).all()
        users: Iterable[Row] = self.session.execute(select(AllUsers.name, AllUsers.last_login)).all()
        # Возвращаем список кортежей
        return users
        # return query.all()

        # Это так работает (из примера, на память для себя):
        # with Session(engine) as session:
        #     # query for ``User`` objects
        #     statement = select(User).filter_by(name="ed")
        #
        #     # list of ``User`` objects
        #     user_obj = session.scalars(statement).all()
        #
        #     # query for individual columns
        #     statement = select(User.name, User.fullname)
        #
        #     # list of Row objects
        #     rows = session.execute(statement).all()

    def active_users_list(self) -> Iterable[Row]:
        """
        Метод возвращает список активных пользователей
        """
        # Запрашиваем соединение таблиц и собираем кортежи имя, адрес, порт, время.
        active_users: Iterable[Row] = self.session.execute(select(
            AllUsers.name,
            ActiveUsers.ip_address,
            ActiveUsers.port,
            ActiveUsers.login_time
        ).join(AllUsers)).all()
        # query = self.session.query(
        #     self.AllUsers.name,
        #     self.ActiveUsers.ip_address,
        #     self.ActiveUsers.port,
        #     self.ActiveUsers.login_time
        #     ).join(self.AllUsers)
        # Возвращаем список кортежей
        return active_users
        # return query.all()

    def login_history(self, username: str | None = None) -> Iterable[Row]:
        """
        Метод, возвращающий историю входов по пользователю или всех пользователей
        """
        # Если было указано имя пользователя, то фильтруем по нему
        # Запрашиваем историю входа
        if username:
            history: Iterable[Row] = self.session.execute(select(
                AllUsers.name,
                LoginHistory.date_time,
                LoginHistory.ip_address,
                LoginHistory.port
            ).join(AllUsers).filter(AllUsers.name == username)).all()
        else:
            history: Iterable[Row] = self.session.execute(select(
                AllUsers.name,
                LoginHistory.date_time,
                LoginHistory.ip_address,
                LoginHistory.port
            ).join(AllUsers)).all()
        return history
        # Запрашиваем историю входа
        # query = self.session.query(self.AllUsers.name,
        #                            self.LoginHistory.date_time,
        #                            self.LoginHistory.ip,
        #                            self.LoginHistory.port
        #                            ).join(self.AllUsers)
        # Если было указано имя пользователя, то фильтруем по нему
        # if username:
        #     query = query.filter(self.AllUsers.name == username)
        # return query.all()


if __name__ == "__main__":
    db = ServerStorage()
    # выполняем 'подключение' пользователя
    db.user_login('client_1', '192.168.1.4', 8888)
    db.user_login('client_2', '192.168.1.5', 7777)
    db.user_login('client_3', '192.168.1.7', 7777)
    # выводим список известных пользователей
    print('выводим список известных пользователей')
    print(db.users_list())
    # выводим список кортежей - активных пользователей
    print('выводим список кортежей - активных пользователей')
    print(db.active_users_list())
    # выполянем 'отключение' пользователя
    db.user_logout('client_1')
    # выводим список кортежей - активных пользователей
    print('выводим список кортежей - активных пользователей после отключения client_1')
    print(db.active_users_list())
    # запрашиваем историю всех входов
    print('запрашиваем историю всех входов')
    print(db.login_history())
    # запрашиваем историю входов по пользователю
    print('запрашиваем историю входов по пользователю client_1')
    print(db.login_history('client_1'))

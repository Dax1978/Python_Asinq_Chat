import datetime

from sqlalchemy import String, Text
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .Base import Base


class AllUsers(Base):
    """Модель таблицы всех пользователей чата"""
    __tablename__ = "Users"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    last_login: Mapped[datetime.datetime] = mapped_column(nullable=False, server_default=func.CURRENT_TIMESTAMP())
    passwd_hash: Mapped[str] = mapped_column(unique=True)
    pubkey: Mapped[Text] = mapped_column(Text, nullable=True)

    def __init__(self, username, passwd_hash):
        super().__init__()
        self.name = username
        self.last_login = func.CURRENT_TIMESTAMP()
        self.passwd_hash = passwd_hash
        # self.pubkey = None
        # self.last_login = func.CURRENT_TIMESTAMP()
        # self.last_login = datetime.datetime.now()
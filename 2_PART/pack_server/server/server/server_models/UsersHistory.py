from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .Base import Base


class UsersHistory(Base):
    """
    Модель таблицы контактов пользователей
    """
    __tablename__ = "History"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped[int] = mapped_column(ForeignKey("Users.id"))
    sent: Mapped[int] = mapped_column(Integer, default=0)
    accepted: Mapped[int] = mapped_column(Integer, default=0)

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.sent = 0
        self.accepted = 0
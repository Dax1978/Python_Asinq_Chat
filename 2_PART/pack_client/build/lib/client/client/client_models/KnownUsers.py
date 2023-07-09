from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String

from .Base import Base


class KnownUsers(Base):
    """
    Класс - отображение таблицы известных пользователей
    """
    __tablename__ = "known_users"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(77))

    def __init__(self, user):
        super().__init__()
        self.username = user
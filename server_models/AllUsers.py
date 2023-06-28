import datetime

from sqlalchemy import String
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from .Base import Base


class AllUsers(Base):
    """
    Модель таблицы всех пользователей чата
    """
    __tablename__ = "Users"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    last_login: Mapped[datetime.datetime] = mapped_column(nullable=False, server_default=func.CURRENT_TIMESTAMP())

    def __init__(self, username):
        super().__init__()
        self.name = username
        # self.last_login = func.CURRENT_TIMESTAMP()
        # self.last_login = datetime.datetime.now()
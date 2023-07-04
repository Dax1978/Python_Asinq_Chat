import datetime

from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import func
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .Base import Base


class LoginHistory(Base):
    """
    Модель таблицы истории входов
    """
    __tablename__ = "Login_history"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[int] = mapped_column(ForeignKey("Users.id"))
    date_time: Mapped[datetime.datetime] = mapped_column(nullable=False, server_default=func.CURRENT_TIMESTAMP())
    ip: Mapped[str] = mapped_column(String(15))
    port: Mapped[int] = mapped_column(Integer)

    def __init__(self, name, date, ip, port):
        super().__init__()
        self.name = name
        self.date_time = date
        self.ip = ip
        self.port = port
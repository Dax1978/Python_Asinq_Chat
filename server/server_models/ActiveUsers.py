import datetime

from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import func
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .Base import Base


class ActiveUsers(Base):
    """Модель таблицы текущих активных пользователей чата"""
    __tablename__ = "Active_users"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped[int] = mapped_column(ForeignKey("Users.id"), unique=True)
    ip_address: Mapped[str] = mapped_column(String(15))
    port: Mapped[int] = mapped_column(Integer)
    login_time: Mapped[datetime.datetime] = mapped_column(nullable=False, server_default=func.CURRENT_TIMESTAMP())

    def __init__(self, user_id, ip_address, port, login_time):
        super().__init__()
        self.user = user_id
        self.ip_address = ip_address
        self.port = port
        self.login_time = login_time
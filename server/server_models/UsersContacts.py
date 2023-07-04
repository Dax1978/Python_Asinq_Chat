from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .Base import Base


class UsersContacts(Base):
    """Модель таблицы контактов пользователей"""
    __tablename__ = "Contacts"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped[int] = mapped_column(ForeignKey("Users.id"))
    contact: Mapped[int] = mapped_column(ForeignKey("Users.id"))

    def __init__(self, user, contact):
        super().__init__()
        self.user = user
        self.contact = contact
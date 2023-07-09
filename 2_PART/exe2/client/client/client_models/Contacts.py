from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String

from .Base import Base


class Contacts(Base):
    """
    Класс - отображение таблицы контактов
    """
    __tablename__ = "contacts"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(77), unique=True)

    def __init__(self, contact):
        super().__init__()
        self.name = contact
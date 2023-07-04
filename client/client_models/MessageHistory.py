import datetime

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String
from sqlalchemy import Text
# from sqlalchemy import DateTime
from sqlalchemy import func

from .Base import Base


class MessageHistory(Base):
    """
    Класс - отображение таблицы истории сообщений
    """
    __tablename__ = "message_history"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    contact: Mapped[str] = mapped_column(String(77), nullable=True)
    direction: Mapped[str] = mapped_column(String(77))
    message: Mapped[Text] = mapped_column(Text)
    # date: Mapped[DateTime] = mapped_column(nullable=False, server_default=func.CURRENT_TIMESTAMP())
    date: Mapped[datetime.datetime] = mapped_column(nullable=False, server_default=func.CURRENT_TIMESTAMP())

    def __init__(self, contact, direction, message):
        super().__init__()
        self.contact = contact
        self.direction = direction
        self.message = message
        # self.date = func.CURRENT_TIMESTAMP()
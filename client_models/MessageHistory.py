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
    from_user: Mapped[str] = mapped_column(String(77))
    to_user: Mapped[str] = mapped_column(String(77))
    message: Mapped[Text] = mapped_column(Text)
    # date: Mapped[DateTime] = mapped_column(nullable=False, server_default=func.CURRENT_TIMESTAMP())
    date: Mapped[datetime.datetime] = mapped_column(nullable=False, server_default=func.CURRENT_TIMESTAMP())

    def __init__(self, from_user, to_user, message):
        super().__init__()
        self.from_user = from_user
        self.to_user = to_user
        self.message = message
        self.date = func.CURRENT_TIMESTAMP()
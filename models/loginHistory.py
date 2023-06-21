import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import func
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from .base import Base
if TYPE_CHECKING:
    from .user import AllUsers


class LoginHistory(Base):
    """
    Модель таблицы истории входов
    """
    __tablename__ = "login_history"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    date_time: Mapped[datetime.datetime] = mapped_column(nullable=False, server_default=func.CURRENT_TIMESTAMP())
    ip_address: Mapped[str] = mapped_column(String(15))
    port: Mapped[int] = mapped_column(Integer)

    user: Mapped["AllUsers"] = relationship(back_populates="history")
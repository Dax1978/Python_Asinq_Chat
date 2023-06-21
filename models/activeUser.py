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


class ActiveUsers(Base):
    """
    Модель таблицы текущих активных пользователей чата
    """
    __tablename__ = "active_users"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    ip_address: Mapped[str] = mapped_column(String(15))
    port: Mapped[int] = mapped_column(Integer)
    login_time: Mapped[datetime.datetime] = mapped_column(nullable=False, server_default=func.CURRENT_TIMESTAMP())

    user: Mapped["AllUsers"] = relationship(back_populates="active_user")
import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from .base import Base

if TYPE_CHECKING:
    from .activeUser import ActiveUsers
    from .loginHistory import LoginHistory
    # from .address import Address


class AllUsers(Base):
    """
    Модель таблицы всех пользователей чата
    """
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    last_login: Mapped[datetime.datetime] = mapped_column(nullable=False, server_default=func.CURRENT_TIMESTAMP())

    active_user: Mapped["ActiveUsers"] = relationship(back_populates="user")
    history: Mapped[list["LoginHistory"]] = relationship(back_populates="user")
    # addresses: Mapped[list["Address"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __str__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, last_login={self.last_login!r})"

    def __repr__(self) -> str:
        return str(self)
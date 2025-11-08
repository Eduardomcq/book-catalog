from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from book_catalog.models.base import table_registry


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(
        init=False, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        init=False, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        init=False,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False
    )

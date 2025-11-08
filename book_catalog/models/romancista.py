from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from book_catalog.models.base import table_registry


@table_registry.mapped_as_dataclass
class Romancista:
    __tablename__ = 'romancistas'

    id: Mapped[int] = mapped_column(
        init=False, primary_key=True, autoincrement=True
    )
    nome: Mapped[str] = mapped_column(
        unique=True
    )
    created_at: Mapped[datetime] = mapped_column(
        init=False, default=datetime.now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False
    )

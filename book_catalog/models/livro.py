from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from book_catalog.models.base import table_registry


@table_registry.mapped_as_dataclass
class Livro:
    __tablename__ = 'livros'

    id: Mapped[int] = mapped_column(init=False, primary_key=True, autoincrement=True)
    ano: Mapped[int]
    titulo: Mapped[str] = mapped_column(unique=True)
    romancista_id: Mapped[int] = mapped_column(ForeignKey('romancistas.id'))
    created_at: Mapped[datetime] = mapped_column(
        init=False, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        init=False,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False)

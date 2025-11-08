from pydantic import BaseModel, Field


class BookBase(BaseModel):
    ano: int
    titulo: str
    romancista_id: int


class BookCreated(BookBase):
    id: int


class BookPatch(BaseModel):
    ano: int


class BookDeleted(BaseModel):
    message: str


class FilterPage(BaseModel):
    offset: int = Field(0, ge=0)
    limit: int = Field(100, ge=1)


class LivroQuery(FilterPage):
    titulo: str | None = None
    ano: int | None = None


class BookList(BaseModel):
    livros: list[BookCreated]

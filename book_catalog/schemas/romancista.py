from pydantic import BaseModel, Field


class BaseRomancista(BaseModel):
    nome: str


class RomancistaCreated(BaseRomancista):
    id: int


class RomancistaDeleted(BaseModel):
    message: str


class RomancistaList(BaseModel):
    romancistas: list[RomancistaCreated]


class FilterPage(BaseModel):
    offset: int = Field(0, ge=0)
    limit: int = Field(100, ge=1)


class RomancistaQuery(FilterPage):
    nome: str

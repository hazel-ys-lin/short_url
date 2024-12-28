from sqlmodel import Field, SQLModel
from datetime import datetime


class ShortUrlBase(SQLModel):
    short_code: str = Field(index=True, unique=True)
    original_url: str
    expiration_date: datetime
    created_at: datetime = Field(default_factory=datetime.now)


class ShortUrl(ShortUrlBase, table=True):
    id: int = Field(default=None, primary_key=True)

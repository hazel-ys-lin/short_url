from pydantic import BaseModel, HttpUrl, validator
from datetime import datetime
from typing import Optional


class ShortenRequest(BaseModel):
    original_url: HttpUrl

    @validator('original_url')
    def url_length_limit(cls, v):
        if len(str(v)) > 2048:
            raise ValueError('URL too long')
        return v


class ShortenResponse(BaseModel):
    short_url: str
    expiration_date: Optional[datetime]
    success: bool
    reason: Optional[str] = None

from contextlib import asynccontextmanager
from typing import AsyncIterator
import logging
from nanoid import generate

from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from datetime import datetime, timedelta
from app.db import create_db_tables, get_db_session
from app.models import ShortUrl
from app.schemas import ShortenRequest, ShortenResponse
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="URL Shortener API",
    description="A service to create and manage short URLs",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

origins = []
if Config.BACKEND_CORS_ORIGINS:
    origins = Config.BACKEND_CORS_ORIGINS.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # startup
    await create_db_tables()
    logger.info("Database tables created successfully")
    yield
    # shutdown
    logger.info("Application shutting down")

app.router.lifespan_context = lifespan


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/shorten", response_model=ShortenResponse)
@limiter.limit(f"{Config.RATE_LIMIT_PER_MINUTE}/minute")
async def create_short_url(
    shorten_request: ShortenRequest,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    try:
        short_code = generate(size=8)
        short_url = f"{Config.BASE_URL}/{short_code}"

        expiration_date = datetime.now() + timedelta(days=30)

        short_url_obj = ShortUrl(
            short_code=short_code,
            original_url=str(shorten_request.original_url),
            expiration_date=expiration_date
        )
        db.add(short_url_obj)
        await db.commit()
        await db.refresh(short_url_obj)

        logger.info(f"Created short URL: {short_url} for {shorten_request.original_url}")
        return ShortenResponse(
            short_url=short_url,
            expiration_date=expiration_date,
            success=True
        )
    except Exception as e:
        logger.error(f"Error creating short URL: {e}")
        return ShortenResponse(
            short_url="",
            expiration_date=None,
            success=False,
            reason=str(e)
        )


@app.get("/{short_code}")
@limiter.limit(f"{Config.RATE_LIMIT_PER_MINUTE}/minute")
async def redirect_short_url(
    request: Request,
    short_code: str,
    db: AsyncSession = Depends(get_db_session)
):
    try:
        result = await db.execute(
            select(ShortUrl).where(ShortUrl.short_code == short_code)
        )
        short_url_obj = result.scalar_one_or_none()

        if not short_url_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Short URL not found"
            )

        if short_url_obj.expiration_date < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Short URL expired"
            )

        logger.info(f"Redirecting {short_code} to {short_url_obj.original_url}")
        return RedirectResponse(url=short_url_obj.original_url)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error redirecting short URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

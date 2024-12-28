from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlmodel import SQLModel
from sqlalchemy.orm import sessionmaker
from app.config import Config
import logging

logger = logging.getLogger(__name__)

engine = create_async_engine(
    Config.DATABASE_URL,
    echo=True,
    future=True
)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def create_db_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_db_session():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()

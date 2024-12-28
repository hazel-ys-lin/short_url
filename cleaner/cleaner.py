import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlmodel import select
from app.models import ShortUrl
from datetime import datetime
import logging
from app.config import Config
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = create_async_engine(Config.DATABASE_URL)


async def cleanup_expired_urls():
    async with AsyncSession(engine) as session:
        try:
            result = await session.execute(
                select(ShortUrl).where(ShortUrl.expiration_date < datetime.now())
            )
            expired_urls = result.scalars().all()

            for url in expired_urls:
                await session.delete(url)

            await session.commit()
            logger.info(f"Cleaned up {len(expired_urls)} expired URLs")
        except Exception as e:
            logger.error(f"Error cleaning up expired URLs: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    scheduler = AsyncIOScheduler()
    scheduler.add_job(cleanup_expired_urls, 'interval', hours=24)
    scheduler.start()

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass

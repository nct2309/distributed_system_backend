from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, sessionmaker

from ..config import settings


class Base(DeclarativeBase, MappedAsDataclass):
    pass


DATABASE_URI = settings.POSTGRES_URI
DATABASE_URL = f"{DATABASE_URI}"

async_engine = create_async_engine(DATABASE_URL, echo=False, future=True, pool_recycle=3600)

local_session = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)


async def async_get_db() -> AsyncSession:
    async_session = local_session
    async with async_session() as db:
        yield db

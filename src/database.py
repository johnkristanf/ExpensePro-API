from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from src.config import settings


class Base(DeclarativeBase):
    pass


class Database:
    engine = None
    async_session = None

    @classmethod
    def connect(cls):
        if not cls.engine:
            cls.engine = create_async_engine(
                settings.DATABASE_ASYNC_DSN, future=True, echo=False
            )
            cls.async_session = async_sessionmaker(
                cls.engine, expire_on_commit=False, class_=AsyncSession
            )

    @classmethod
    async def get_async_session(cls):
        if not cls.async_session:
            cls.connect()
        return cls.async_session()

    @classmethod
    async def close(cls):
        if cls.engine:
            await cls.engine.dispose()
            cls.engine = None
            cls.async_session = None

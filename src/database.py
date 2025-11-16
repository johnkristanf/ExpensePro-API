from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

class Database:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.engine = None
        self.async_session = None

    async def connect(self):
        if not self.engine:
            self.engine = create_async_engine(self.dsn, future=True, echo=False)
            self.async_session = async_sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)

    async def close(self):
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self.async_session = None

    async def get_connection(self):
        if not self.async_session:
            await self.connect()
        return self.async_session()

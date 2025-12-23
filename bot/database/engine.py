from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from bot.database.models import Base
from bot.config import *

engine = create_async_engine(DB_URL, echo=False)

session = async_sessionmaker(bind=engine, expire_on_commit=False)

async def begin_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

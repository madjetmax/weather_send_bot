from typing import Callable, Dict, Awaitable, Any 
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker
from bot.database.engine import session as db_session

class DataBaseSessionMiddleware(BaseMiddleware):
    async def __call__(
            self, 
            handler: Callable[[TelegramObject, Dict[str, Any]],  Awaitable[Any]], 
            event: TelegramObject, 
            data: Dict[str, Any]
        ):
        # set db session
        async with db_session() as session:
            data["db_session"] = session
            return await handler(event, data)
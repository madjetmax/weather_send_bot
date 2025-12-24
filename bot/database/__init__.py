from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User, WeatherLog
from .engine import session as db_session
from datetime import datetime


# * users
async def create_user(session: AsyncSession, **data: dict) -> bool:
    user = User(
        **data
    )
    session.add(user)
    await session.commit()


async def get_user(session: AsyncSession, user_id: int) -> User | None:
    query = select(User).filter_by(id=user_id)
    res = await session.execute(query)
    user = res.scalar_one_or_none()
    return user
    
async def update_user(session: AsyncSession, user_id: int, **new_data: dict):
    await session.rollback()

    query = (
        update(User)
        .filter_by(id=user_id)
        .values(**new_data)
    )
    await session.execute(query)
    await session.commit()

# * weather logs 
async def create_weather_log(session: AsyncSession, **data):
    w_log = WeatherLog(
        **data
    )
    session.add(w_log)
    await session.commit()


async def delete_old_weather_logs(session: AsyncSession, from_date: datetime):
    query = (
        delete(WeatherLog)
        .where(WeatherLog.created_at < from_date)
    )

    await session.execute(query)
    await session.commit()
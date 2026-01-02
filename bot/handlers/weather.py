from time import time
from datetime import datetime, timedelta, UTC

from aiogram import Router
from aiogram.types import Message, ContentType
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

import bot.database as db
from bot import tasks
from bot.tasks.broker import dynamic_schedule_source

from bot.states.weather import LocationSetState
from bot.middlewares import weather as middlewares

from bot import redis_client
from bot import weather_parse
from bot import texts
from bot.config import *


router = Router()

# add middleware
router.message.middleware.register(
    middlewares.DataBaseSessionMiddleware()
)

async def send_weather_message(message: Message, weather_data: dict):
    # get time
    hours, minutes, _ = weather_data["dt_txt"].split(" ")[-1].split(":")

    text = texts.weater_text.format(
        time=f"{hours}:{minutes}",
        name=weather_data["weather"][0]["main"],
        temp=weather_data["main"]["temp"],
        temp_feels_like=weather_data["main"]["feels_like"],
        max_temp=weather_data["main"]["temp_max"],
        min_temp=weather_data["main"]["temp_min"],

        humidity=weather_data["main"].get("humidity", 100),
        wind_speed=weather_data["wind"]["speed"],
        visibility=weather_data.get("visibility", "visible")
    )
    
    await message.answer(text, parse_mode="HTML")

@router.message(CommandStart())
async def get_weater(message: Message, state: FSMContext, db_session: AsyncSession):
    user_id = message.from_user.id
    # get user location
    user_location = await redis_client.get_data(f"{user_id}_location")
    
    # send weather
    if user_location is not None:
        lat = user_location["lat"]
        long = user_location["long"]

        weather_data = await weather_parse.get_future_weather(lat, long)

        return await send_weather_message(message, weather_data)        

    # ask user to send location         
    await message.answer("send me your location")
    await state.set_state(LocationSetState.location)


@router.message(LocationSetState.location)
async def get_user_location(message: Message, state: FSMContext, db_session: AsyncSession):
    user_id = message.from_user.id

    # check message is location
    if message.location is None:
        return await message.answer("failed to get location, send again")

    update_data = {
        "lat": message.location.latitude,
        "long": message.location.longitude,
    }

    # set location to redis
    expire_time = REDIS_USER_LOCATION_EXPIRE_TIME
    await redis_client.set_data(
        f"{user_id}_location", update_data,
        expire_time
    )

    # send weather
    weather_data = await weather_parse.get_future_weather(
        message.location.latitude, message.location.longitude
    )
    await send_weather_message(message, weather_data)

    await state.clear()

    start_seconds = time()

    task = await tasks.send_time_diff.schedule_by_interval(
        source=dynamic_schedule_source,
        interval=WEATHER_TASK_SEND_INTERVAL,
        start_seconds=start_seconds,
        user_id=user_id
    )


    # create or update user
    try:
        await db.create_user(
            db_session,
            id=user_id, name=message.from_user.full_name, 
            lat=message.location.latitude, long=message.location.longitude
        )
    except:
        await db.update_user(db_session, user_id, **update_data)

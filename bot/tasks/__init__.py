from typing import Annotated
from datetime import datetime, timedelta

from taskiq import TaskiqDepends, Context
from aiogram import Bot

from bot.tasks import broker as tasks_broker
import bot.database as db
from bot.database.engine import session as db_session
from bot import redis_client

from bot.weather_parse import get_future_weather
from bot import texts


@tasks_broker.broker.task
async def send_weather_to_user(user_id: int, context: Annotated[Context, TaskiqDepends()], bot: Bot = TaskiqDepends(), ):

    now = datetime.now()
    print("ran", now, context.message.labels)

    # get position data in redis
    user_location = await redis_client.get_data(f"{user_id}_location")
    
    if user_location is None:
        schedule_id = context.message.labels["schedule_id"]
        # check schedule
        schedule_exists = await tasks_broker.check_schedule(schedule_id)

        await bot.send_message(user_id, str(schedule_exists) + " " + schedule_id)

        if not schedule_exists:
            return

        # send message
        await bot.send_message(user_id, "Couldn't get you location, /start to send it again")

        # remove schedule
        await tasks_broker.delete_schedule(schedule_id)
        return

    # get weather data
    weather_data = await get_future_weather(user_location["lat"], user_location["long"])

    # get time
    hours, minutes, _ = weather_data["dt_txt"].split(" ")[-1].split(":")

    text = texts.weater_text.format(
        time=f"{hours}:{minutes}",
        name=weather_data["weather"][0]["main"],
        temp=weather_data["main"]["temp"],
        temp_feels_like=weather_data["main"]["feels_like"],
        max_temp=weather_data["main"]["temp_max"],
        min_temp=weather_data["main"]["temp_min"],
        humidity=weather_data["main"]["humidity"],
        wind_speed=weather_data["wind"]["speed"],
        visibility=weather_data["visibility"]
    )
    await bot.send_message(user_id, text, parse_mode="HTML")
    
    # create weather log 
    year, month, day = weather_data["dt_txt"].split(" ")[0].split("-")
    date = datetime(
        int(year), int(month), int(day), int(hours), int(minutes)
    )
    async with db_session() as session:
        await db.create_weather_log(
            session,
            date=date, 
            name=weather_data["weather"][0]["main"],

            temperature=weather_data["main"]["temp"],
            temp_feels_like=weather_data["main"]["feels_like"],
            max_temp=weather_data["main"]["temp_max"],
            min_temp=weather_data["main"]["temp_min"],
            
            wind_speed=weather_data["wind"]["speed"],

            humidity=weather_data["main"]["humidity"],
            visibility=weather_data["visibility"],

            lat=user_location["lat"],
            long=user_location["long"],
        )
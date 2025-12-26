from typing import Annotated
import asyncio
from datetime import datetime, timedelta

from taskiq_redis import RedisAsyncResultBackend, RedisStreamBroker, ListRedisScheduleSource, RedisScheduleSource
from taskiq import TaskiqScheduler, Context, TaskiqDepends
from taskiq.schedule_sources import LabelScheduleSource
from redis.asyncio import Redis, BlockingConnectionPool
import taskiq_aiogram

from bot import redis_client

from bot.config import REDIS_CLIENT_HOST, REDIS_CLIENT_PORT, REDIS_CLIENT_DB

redis_url = f"redis://{REDIS_CLIENT_HOST}:{REDIS_CLIENT_PORT}/{REDIS_CLIENT_DB}"

result_backend = RedisAsyncResultBackend(
    redis_url=redis_url,
)

broker = RedisStreamBroker(
    url=redis_url,
).with_result_backend(result_backend)
# ! run: taskiq worker bot.tasks.broker:broker

taskiq_aiogram.init(
    broker,
    "bot.main:dp",
    "bot.main:bot",
)

schedule_source = ListRedisScheduleSource(
    url=redis_url
)

scheduler = TaskiqScheduler(broker=broker, sources=[schedule_source])
# ! run:  taskiq scheduler bot.tasks.broker:scheduler --skip-first-run

static_tasks_scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)
# ! run:  taskiq scheduler bot.tasks.broker:static_tasks_scheduler --skip-first-run 


async def delete_schedule(id_: str):
    print(id_)
    await schedule_source.delete_schedule(id_)

async def delete_all_schedules():
    schedules = await schedule_source.get_schedules()
    for schedule in schedules:
        await delete_schedule(schedule.schedule_id)

async def get_all_schedules_ids():
    schedules = await schedule_source.get_schedules()
    return [schd.schedule_id for schd in schedules]

async def show_all_schedules():
    schedules = await schedule_source.get_schedules()
    for schedule in schedules:
        print(schedule)


async def check_schedule(schedule_id: str) -> bool:
    key = f"{schedule_source._prefix}:data:{schedule_id}"
    schedule = await redis_client.client.get(key)
    
    return schedule is not None

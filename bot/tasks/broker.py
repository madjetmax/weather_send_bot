from typing import Annotated

from taskiq_redis import (
    RedisAsyncResultBackend, RedisStreamBroker, RedisScheduleSource
)
from taskiq import TaskiqScheduler, Context, TaskiqDepends
from redis.asyncio import Redis
import taskiq_aiogram
from taskiq.events import TaskiqEvents

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

# define sources
dynamic_schedule_source = RedisScheduleSource(
    url=redis_url
)

scheduler = TaskiqScheduler(
    broker=broker,
    sources=[
        dynamic_schedule_source        
    ],
)
# ! run:  taskiq scheduler bot.tasks.broker:scheduler --skip-first-run --update-interval 5


# * I also tried to fix error with this
@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def on_worker_startup(context: Annotated[Context, TaskiqDepends()]):
    r = Redis.from_url(redis_url)

    try:
        await r.xgroup_create(
            name="taskiq",
            groupname="taskiq",
            id="$",
            mkstream=True,
        )
    except Exception as e:
        print(e)
        if "BUSYGROUP" not in str(e):
            raise

# help funcs
async def delete_schedule(id_: str):
    await dynamic_schedule_source.delete_schedule(id_)

async def delete_all_schedules():
    schedules = await dynamic_schedule_source.get_schedules()
    for schedule in schedules:
        await delete_schedule(schedule.schedule_id)

async def get_all_schedules_ids():
    schedules = await dynamic_schedule_source.get_schedules()
    return [schd.schedule_id for schd in schedules]

async def show_all_schedules():
    schedules = await dynamic_schedule_source.get_schedules()
    for schedule in schedules:
        print(schedule)


async def check_schedule(schedule_id: str) -> bool:
    key = f"{dynamic_schedule_source._prefix}:data:{schedule_id}"
    schedule = await redis_client.client.get(key)
    
    return schedule is not None

import asyncio
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from bot.redis_client import client as redis_client
from bot.config import *

from bot import handlers
from bot import database as db

import bot.tasks.broker as tasks_broker
from bot import tasks

bot = Bot(token=BOT_TOKEN)

redic_storage = RedisStorage(
    redis=redis_client
)
dp = Dispatcher(storage=redic_storage)
# add routers
dp.include_routers(
    handlers.router
)

async def main():

    # await redis_client.flushall(True)

    # tasks
    await tasks_broker.broker.startup()

    responces_send_task = await tasks.send_responces_time.schedule_by_cron(
        source=tasks_broker.schedule_source,
        cron=f"*/{RESPONCES_TIME_TASK_SEND_INTERVAL} * * * *",
    )

    # await tasks_broker.show_all_schedules()
    # await tasks_broker.delete_all_schedules()

    now = datetime.now()
    print("scheduled", now)

    # task = await tasks.send_weather_to_user.schedule_by_cron(
    #     source=tasks_broker.schedule_source,
    #     cron=f"*/{WEATHER_TASK_SEND_INTERVAL} * * * *",
    #     user_id=859261869 
    # )
    # print(task)
    
    
    await db.engine.begin_db()

    print('bot launched')
    await dp.start_polling(bot,)
    
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("bot stoped!")


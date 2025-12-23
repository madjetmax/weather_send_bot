from typing import Any
import json

from datetime import timedelta
from redis.asyncio import Redis
from bot.config import REDIS_CLIENT_HOST, REDIS_CLIENT_PORT, REDIS_CLIENT_DB

client = Redis(host=REDIS_CLIENT_HOST, port=REDIS_CLIENT_PORT, db=REDIS_CLIENT_DB)

async def get_data(key: Any) -> Any:
    data = await client.get(key)
    if data is None:
        return None
    try:
        return json.loads(data.decode('utf-8'))
    except:
        ...
    return data.decode('utf-8')


async def set_data(key: Any, data: Any, expire: timedelta | None=None):
    # encode data
    if isinstance(data, dict):
        data = json.dumps(data)
    await client.set(key, data, ex=expire)
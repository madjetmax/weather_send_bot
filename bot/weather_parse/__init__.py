from aiohttp import ClientSession
from bot.config import WEATHER_API_KEY, WEATHER_API_URL

async def get_weather_json(lat: float, long: float, units: str) -> dict:
    url = WEATHER_API_URL.format(lat=lat, long=long, units=units, api_key=WEATHER_API_KEY)

    async with ClientSession() as session:
        res = await session.get(url)

        return await res.json()

async def get_future_weather(lat: float, long: float, units: str="metric") -> dict:
    data_json = await get_weather_json(lat, long, units)

    list_data = data_json["list"]
    return list_data[1]
    
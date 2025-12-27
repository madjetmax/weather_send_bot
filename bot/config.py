from dotenv import load_dotenv
import os

load_dotenv()

# bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
RESPONCES_TIME_TASK_SEND_INTERVAL = 5 # minutes

# weather api
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={long}&units={units}&appid={api_key}"

# db
DB_USER=os.getenv("DB_USER")
DB_PASSWORD=os.getenv("DB_PASSWORD")

DB_HOST=os.getenv("DB_HOST")
DB_PORT=os.getenv("DB_PORT")

DB_NAME=os.getenv("DB_NAME")

DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# redis client
REDIS_CLIENT_HOST = os.getenv("REDIS_CLIENT_HOST")
REDIS_CLIENT_PORT = os.getenv("REDIS_CLIENT_PORT")
REDIS_CLIENT_DB = os.getenv("REDIS_CLIENT_DB")

REDIS_USER_LOCATION_EXPIRE_TIME = 1 # hours

# taskiq
WEATHER_TASK_SEND_INTERVAL = 3 # minutes
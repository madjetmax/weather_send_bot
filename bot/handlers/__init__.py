from aiogram import Router
from .weather import router as weather_router

router = Router()
router.include_routers(weather_router)
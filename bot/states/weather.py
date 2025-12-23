from aiogram.fsm.state import StatesGroup, State


class LocationSetState(StatesGroup):
    location = State()
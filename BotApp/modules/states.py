from aiogram.dispatcher.filters.state import StatesGroup, State


class LoginForm(StatesGroup):
    login = State()
    password = State()
    access_received = State()
    notification_status = State()

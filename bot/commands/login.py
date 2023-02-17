from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from requests import get


class LoginForm(StatesGroup):
    login = State()
    password = State()


async def login_command(message: types.Message, state: FSMContext) -> None:
    await message.answer('Введите логин от сайта: ')
    await state.set_state(LoginForm.login)


async def get_user_login(message: types.Message, state: FSMContext):
    if message.text == '/cancel':
        await state.clear()
        return await message.answer('Вы отменили вход в аккаунт')
    await state.update_data(login=message.text)
    await state.set_state(LoginForm.password)

    await message.answer('Введите пароль от сайта')


async def get_user_password(message: types.Message, state: FSMContext):
    if message.text == '/cancel':
        await state.clear()
        return await message.answer('Вы отменили вход в аккаунт')
    await state.update_data(password=message.text)
    data = await state.get_data()
    login = data.get('login')
    password = message.text
    print(login, password)
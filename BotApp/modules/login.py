import requests
from aiogram import types
from aiogram.dispatcher import FSMContext

from states import LoginForm


async def login_command(message: types.Message, state: FSMContext) -> None:
    """Команда для входа в аккаунт"""
    data = await state.get_data()
    if not data.get('access_received'):
        await message.answer('Введите логин от сайта: ')
        await LoginForm.login.set()
    else:
        await message.answer('Вы уже вошли в аккаунт')


async def get_user_login(message: types.Message, state: FSMContext):
    """Получение логина пользователя"""
    if message.text == '/cancel':
        await state.finish()
        return await message.answer('Вы отменили вход в аккаунт')
    await state.update_data(login=message.text)
    await LoginForm.password.set()

    await message.answer('Введите пароль от сайта')


async def get_user_password(message: types.Message, state: FSMContext):
    """Получения пароля пользователя"""
    if message.text == '/cancel':
        await state.finish()
        return await message.answer('Вы отменили вход в аккаунт')
    await state.update_data(password=message.text)
    data = await state.get_data()
    login = data.get('login')
    password = message.text

    responce = requests.get('http://localhost:5000/api/telegram',
                            json={'type': 'login',
                                  'login': login,
                                  'password': password,
                                  'telegram_id': message.from_user.id}).json()
    if responce['success'] == 'OK':
        await state.finish()
        await message.answer('Вы успешно вошли')
    else:
        await message.answer('Неверный логин или пароль пользователя')
        await state.finish()


async def logout_command(message: types.Message):
    requests.put('http://localhost:5000/api/telegram',
                 json={'type': 'logout',
                       'telegram_id': message.from_user.id}).json()
    await message.answer('Вы успешно вышли')

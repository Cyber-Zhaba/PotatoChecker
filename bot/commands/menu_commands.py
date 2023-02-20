import requests
from aiogram import types
from aiogram.dispatcher import FSMContext

from bot.commands.structures.keyboards_menu import state_on_keyboard, back_keyboard
from bot.config import bot


async def menu_command_renamed(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if 'access_received' in data.keys() and data['access_received']:
        await message.answer(
            'Выберите действие из предложенных',
            reply_markup=state_on_keyboard
        )
    else:
        await message.answer('Сначала войдите в аккаунт')


async def call_notifications_on(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if 'access_received' in data.keys() and data['access_received']:
        if data['notification_status']:
            await state.update_data(notification_status=False)
            await callback_query.answer('Уведомления выключены')
        else:
            await state.update_data(notification_status=True)
            await callback_query.answer('Уведомления включены')
    else:
        await bot.send_message(callback_query.from_user.id, 'Вы не вошли в аккаунт')


async def call_get_report(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if 'access_received' in data.keys() and data['access_received']:
        text = []
        user_login = data['user_login']
        print(user_login)
        responce = requests.get('http://localhost:5000/api/telegram',
                                json={'type': 'get_favourite_sites',
                                      'login': user_login}).json()
        print(responce)
        try:
            for site_info in responce['sites'][0]:
                text.append(f"{site_info[0]} ({site_info[1]}) - {site_info[2]}")
        except KeyError:
            text = ['У вас нет избранных сайтов\n\nДобавить их можно на сайте']
        await callback_query.message.edit_text(
            '\n'.join(text),
            reply_markup=back_keyboard
        )
    else:
        await bot.send_message(callback_query.from_user.id, 'Вы не вошли в аккаунт')


async def call_featured_sites(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if 'access_received' in data.keys() and data['access_received']:
        text = []
        user_login = data['user_login']
        responce = requests.get('http://localhost:5000/api/telegram',
                                json={'type': 'get_favourite_sites',
                                      'login': user_login}).json()
        print(responce)
        try:
            for site_info in responce['sites'][0]:
                text.append(f"{site_info[0]} - {site_info[1]}")
        except KeyError:
            text = ['У вас нет избранных сайтов\n\nДобавить их можно на сайте']
            await callback_query.message.edit_text(
                '\n'.join(text),
                reply_markup=back_keyboard
            )
    else:
        await bot.send_message(callback_query.from_user.id, 'Вы не вошли в аккаунт')


async def call_back(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if 'access_received' in data.keys() and data['access_received']:
        await callback_query.message.edit_text(
            'Выберите действие из предложенных',
            reply_markup=state_on_keyboard
        )
    else:
        await callback_query.answer('Сначала войдите в аккаунт')


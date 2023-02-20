import requests
from aiogram import types
from aiogram.dispatcher import FSMContext

from bot.commands.structures.keyboards_menu import state_on_keyboard, back_keyboard
from bot.config import bot


async def menu_command_renamed(message: types.Message):
    data = requests.get('http://localhost:5000/api/telegram',
                        json={'type': 'check_login',
                              'telegram_id': message.from_user.id}).json()['status']
    if data == 'logged in':
        await message.answer(
            'Выберите действие из предложенных',
            reply_markup=state_on_keyboard
        )
    else:
        await message.answer('Сначала войдите в аккаунт')


async def call_notifications_on(callback_query: types.CallbackQuery):
    data = requests.get('http://localhost:5000/api/telegram',
                        json={'type': 'check_login',
                              'telegram_id': callback_query.from_user.id}).json()['status']
    if data == 'logged in':
        data = requests.get('http://localhost:5000/api/telegram',
                            json={'type': 'change_notify',
                                  'telegram_id': callback_query.from_user.id}).json()['success']
        if data == 0:
            await callback_query.answer('Уведомления выключены')
        else:
            await callback_query.answer('Уведомления включены')
    else:
        await bot.send_message(callback_query.from_user.id, 'Вы не вошли в аккаунт')


async def call_get_report(callback_query: types.CallbackQuery):
    data = requests.get('http://localhost:5000/api/telegram',
                        json={'type': 'check_login',
                              'telegram_id': callback_query.from_user.id}).json()['status']
    if data == 'logged in':
        text = []
        responce = requests.get('http://localhost:5000/api/telegram', json={'telegram_id': callback_query.from_user.id,
                                                                            'type': 'get_favourites'}).json()
        try:
            for site_info in responce['favourite_sites']:
                text.append(f'Состояние сайта {site_info[0]}: {site_info[1]}')
        except KeyError:
            text = ['У вас нет избранных сайтов\n\nДобавить их можно на сайте']
        await callback_query.message.edit_text(
            '\n'.join(text),
            reply_markup=back_keyboard
        )
    else:
        await bot.send_message(callback_query.from_user.id, 'Вы не вошли в аккаунт')


async def call_back(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(
        'Выберите действие из предложенных',
        reply_markup=state_on_keyboard
    )
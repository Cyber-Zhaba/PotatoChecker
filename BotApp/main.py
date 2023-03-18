import asyncio
import logging

import requests
from aiogram import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from modules.__init__ import *


def register_all_handlers(dp):
    dp.register_message_handler(start_command, commands=['start'])
    dp.register_message_handler(help_command, commands=['help'])
    dp.register_message_handler(about_command, commands=['about'])

    dp.register_message_handler(login_command, commands=['login'])
    dp.register_message_handler(get_user_login, state=LoginForm.login)
    dp.register_message_handler(get_user_password, state=LoginForm.password)
    dp.register_message_handler(logout_command, commands=['logout'])

    dp.register_message_handler(menu_command_renamed, commands=['menu'])
    dp.register_callback_query_handler(call_notifications_on, lambda c: c.data == 'notification_on')
    dp.register_callback_query_handler(call_get_report, lambda c: c.data == 'get_report')
    dp.register_callback_query_handler(call_back, lambda c: c.data == 'call_back')


async def main():
    logging.basicConfig(level=logging.INFO)

    commands_for_bot = []
    for cmd in bot_commands:
        commands_for_bot.append(BotCommand(command=cmd[0], description=cmd[1]))
    await bot.set_my_commands(commands=commands_for_bot)

    dp = Dispatcher(bot, storage=MemoryStorage())
    register_all_handlers(dp)

    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


async def noticed():
    response = requests.get('http://localhost:5000/api/telegram',
                            json={'type': 'get_data_for_notified_users'}).json()
    for user in response.keys():
        if response[user]['changed_sites']:
            websites = response[user]['changed_sites']
            id_telegram = int(user)
            websites_str = '\n'.join([f'{x[0]} {x[1]}' for x in websites])
            await bot.send_message(id_telegram, f"Отчёт по сайтам:\n{websites_str}")


if __name__ == '__main__':
    scheduler = AsyncIOScheduler()
    scheduler.add_job(noticed, "interval", seconds=300)
    scheduler.start()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

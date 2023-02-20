import logging
import asyncio

import requests
from aiogram import Dispatcher

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from commands.structures.states import LoginForm
from commands.bot_commands import bot_commands
from commands.about import about_command
from commands.help import help_command
from commands.start import start_command
from commands.site import site_command
from commands.login import (
    login_command,
    logout_command,
    get_user_login,
    get_user_password
)

from commands.menu_commands import menu_command_renamed
from commands.menu_commands import call_get_report
from commands.menu_commands import call_featured_sites
from commands.menu_commands import call_back
from commands.menu_commands import call_notifications_on
from bot.config import bot


def register_all_handlers(dp):
    dp.register_message_handler(start_command, commands=['start'])
    dp.register_message_handler(help_command, commands=['help'])
    dp.register_message_handler(about_command, commands=['about'])
    dp.register_message_handler(site_command, commands=['site'])

    dp.register_message_handler(login_command, commands=['login'])
    dp.register_message_handler(get_user_login, state=LoginForm.login)
    dp.register_message_handler(get_user_password, state=LoginForm.password)
    dp.register_message_handler(logout_command, commands=['logout'])

    dp.register_message_handler(menu_command_renamed, commands=['menu'])
    dp.register_callback_query_handler(call_notifications_on, lambda c: c.data == 'notification_on')
    dp.register_callback_query_handler(call_get_report, lambda c: c.data == 'get_report')
    dp.register_callback_query_handler(call_featured_sites, lambda c: c.data == 'featured_sites')
    dp.register_callback_query_handler(call_back, lambda c: c.data == 'back')


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


def noticed():
    responce = requests.get('http://localhost:5000/api/telegram',
                            json={'type': 'get_data_for_notified_users'}).json()
    print(responce)
    for user in responce.keys():
        if responce[user]['changed_sites']:
            websites = responce[user]['changed_sites']
            print(websites, user)


if __name__ == '__main__':
    scheduler = AsyncIOScheduler()
    scheduler.add_job(noticed, "interval", seconds=10)
    scheduler.start()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


__all__ = ['bot_commands', 'register_user_commands']

from aiogram import Router
from aiogram.enums import ContentType
from aiogram.filters import CommandStart
from aiogram.filters import Command
from aiogram import F

from bot.commands.start import start_command
from bot.commands.help import help_command
from bot.middlewares.register_check import RegisterCheck
from bot.commands.menu import menu_command
from bot.commands.about import about_command
from bot.commands.login import (
    login_command,
    LoginForm,
    get_user_login,
    get_user_password
)


def register_user_commands(router: Router) -> None:
    router.message.register(start_command, CommandStart())
    router.message.register(help_command, Command(commands=['help']))
    router.message.register(about_command, Command(commands=['about']))

    router.message.register(login_command, Command(commands=['login']))
    router.message.register(get_user_login, LoginForm.login)
    router.message.register(get_user_password, LoginForm.password)

    router.message.register(menu_command, Command(commands=['menu']))

    router.message.register(RegisterCheck)
    router.callback_query.register(RegisterCheck)



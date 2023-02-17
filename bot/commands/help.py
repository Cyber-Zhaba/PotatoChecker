from aiogram import types
from aiogram.filters import CommandObject
from aiogram.utils.keyboard import (
    KeyboardButton, ReplyKeyboardBuilder
)

from bot.commands.bot_commands import bot_commands


async def help_command(message: types.Message, command: CommandObject):
    menu_builder = ReplyKeyboardBuilder()

    menu_builder.add(
        KeyboardButton(text='/help')
    )

    if command.args:
        for cmd in bot_commands:
            if cmd[0] == command.args:
                return await message.answer(
                    f'{cmd[0]} - {cmd[1]}\n\n{cmd[2]}'
                )
        else:
            return await message.answer('Команда не найдена')

    return await message.answer(
        'Помощь и справка о боте'
        'Для того, чтобы получить информацию о команде используйте /help <команда>'
    )
from aiogram import types

from bot.commands.bot_commands import bot_commands


async def help_command(message: types.Message):
    command = message.get_args()
    if command:
        for cmd in bot_commands:
            if cmd[0] == command:
                return await message.answer(
                    f'{cmd[0]} - {cmd[1]}\n\n{cmd[2]}'
                )
        else:
            return await message.answer('Команда не найдена')

    return await message.answer(
        'Помощь и справка о боте'
        'Для того, чтобы получить информацию о команде используйте /help <команда>'
    )
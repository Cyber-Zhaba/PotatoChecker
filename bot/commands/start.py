from aiogram import types


async def start_command(message: types.Message) -> None:
    await message.answer(
        'Приветсвуем вас в боте мониторинга сайтов <em>Potato Check Sites Bot</em>',
        parse_mode='HTML'
    )
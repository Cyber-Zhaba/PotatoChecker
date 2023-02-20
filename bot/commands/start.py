from aiogram import types


async def start_command(message: types.Message) -> None:
    await message.answer(
        '<em>Hi</em>',
        parse_mode='HTML'
    )
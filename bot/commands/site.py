from aiogram import types


async def site_command(message: types.Message) -> None:
    await message.answer(
        '<em>Hi</em>',
        parse_mode='HTML'
    )
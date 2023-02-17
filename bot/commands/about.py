from aiogram import types


async def about_command(message: types.Message):
    await message.answer("Информация о сайте.")
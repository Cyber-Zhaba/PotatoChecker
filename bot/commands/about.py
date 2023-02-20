from aiogram import types


async def about_command(message: types.Message):
    await message.answer("Данный бот предоставляет Вам возможность, получить отчет о состоянии избранных сайтов")
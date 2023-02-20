from aiogram import types


async def start_command(message: types.Message) -> None:
    await message.answer(
        ('Приветсвуем вас в боте мониторинга сайтов\n<em>Potato Check Sites Bot</em>\n\n' +
         'Для получения более подброной информации о боте используйте команду <b>/about</b>'),
    )

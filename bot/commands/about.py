from aiogram import types


async def about_command(message: types.Message):
    await message.answer(("Данный бот предоставляет Вам возможность," +
                          " получить отчет о состоянии избранных сайтов." +
                          " Для входа в аккаунт использутся такие же логин" +
                          " и пароль как и для входа на сайт.\nДля входа используйте команду <b>/login</b>"))

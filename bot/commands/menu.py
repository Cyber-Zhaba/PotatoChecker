from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.commands.structures.menu_keyboard import state_off_keyboard


async def menu_command(message: types.Message):
    await message.answer(
        "Выберите действие из предложенных",
        reply_markup=state_off_keyboard
    )


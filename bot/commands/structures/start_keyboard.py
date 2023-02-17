from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def start_board() -> ReplyKeyboardMarkup:
    rk_builder = ReplyKeyboardBuilder()
    rk_builder.button('/help')
    rk_builder.button('/about')
    rk_builder.button('')
    return rk_builder.as_markup(resize_keyboard=True)

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


state_off_keyboard = InlineKeyboardBuilder([
        [InlineKeyboardButton(
            text="Включить уведомления",
            callback_data="notification_on")],
        [InlineKeyboardButton(
            text="Получить отчет",
            callback_data="get_report")],
        [InlineKeyboardButton(
            text="Избранные сайты",
            callback_data="featured_sites")],
        [InlineKeyboardButton(
            text="Сайт",
            url="https://google.com"
        )]
    ]).as_markup(resize_keyboard=True)


state_on_keyboard = InlineKeyboardBuilder([
        [InlineKeyboardButton(
            text="Включить уведомления",
            callback_data="notification_on")],
        [InlineKeyboardButton(
            text="Получить отчет",
            callback_data="get_report")],
        [InlineKeyboardButton(
            text="Избранные сайты",
            callback_data="featured_sites")],
        [InlineKeyboardButton(
            text="Сайт",
            url="https://google.com"
        )]
    ]).as_markup(resize_keyboard=True)




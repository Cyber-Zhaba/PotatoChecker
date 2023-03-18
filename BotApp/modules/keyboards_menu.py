from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


state_on_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text="Вкл/выкл уведомления",
            callback_data="notification_on")],
        [InlineKeyboardButton(
            text="Получить отчет",
            callback_data="get_report")],
        [InlineKeyboardButton(
            text="Сайт",
            url="https://google.com"
        )]
    ])


back_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text="Назад",
            callback_data="call_back"
        )]
    ])

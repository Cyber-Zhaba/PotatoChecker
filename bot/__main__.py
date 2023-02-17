import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from bot.commands import register_user_commands
from bot.commands.bot_commands import bot_commands


async def bot_start(logger: logging.Logger) -> None:
    """Запуск бота"""
    logging.basicConfig(level=logging.DEBUG)

    commands_for_bot = []
    for cmd in bot_commands:
        commands_for_bot.append(BotCommand(command=cmd[0], description=cmd[1]))

    dp = Dispatcher(storage=MemoryStorage())
    bot = Bot(token=os.getenv('token'), parse_mode='HTML')
    await bot.set_my_commands(commands=commands_for_bot)
    register_user_commands(dp)

    await dp.start_polling(bot, logger=logger)


def setup_env():
    """Настройка окружения"""


def main():
    """Функция для запуска"""
    logger = logging.getLogger(__name__)
    try:
        asyncio.run(bot_start(logger))
        logger.info('Bot started')
    except (KeyboardInterrupt, SystemExit):
        logger.info('Bot stopped')


if __name__ == '__main__':
    main()


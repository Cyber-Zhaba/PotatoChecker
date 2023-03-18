import configparser
from os import getcwd

from aiogram import Bot

config = configparser.ConfigParser()
cfg_path = ('../' if getcwd().split('\\')[-1] == 'BotApp' else '') + 'config.cfg'
config.read(cfg_path)
bot = Bot(config['TelegramBot']['Token'], parse_mode='HTML')

import logging
import os
# from dotenv import load_dotenv


from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from keyboards.kbd import kb_client



# BOT_TOKEN = os.getenv('TOKEN')
# ADMINS = os.getenv('ADMIN')

BOT_TOKEN = os.environ['TOKEN']
ADMINS = [os.environ['ADMIN']]

bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())


# Уведомление о запуске
async def on_startup_notify(dp: Dispatcher):
    for admin in ADMINS:
        try:
            await dp.bot.send_message(admin, "Бот Запущен", reply_markup=kb_client)
        except Exception as err:
            logging.exception(err)


# Подготовительные работы
async def on_startup(dispatcher):
    print('Бот в эфире!')
    await on_startup_notify(dispatcher)

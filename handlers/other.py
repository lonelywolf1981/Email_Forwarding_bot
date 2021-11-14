from aiogram import types, Dispatcher

from create_bot import bot
from keyboards.kbd import kb_client


async def echo_send(message: types.Message):
    await bot.send_message(message.from_user.id, 'Бот для отправки документов\n'
                                                 'для начала наберите команду "start"',
                           reply_markup=kb_client)
    await message.delete()


def register_handlers_other(dp: Dispatcher):
    dp.register_message_handler(echo_send)

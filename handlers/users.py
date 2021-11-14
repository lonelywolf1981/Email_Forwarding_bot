import logging
import os
import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
#from loguru import logger

from os import path
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from exchangelib import Credentials, Account, DELEGATE
from create_bot import dp, bot
from sqliter.sqliter import SQLighter as Sq
from utils.formatter import make_folder, send_email

username = os.environ['USER']
password = os.environ['PASSWD']
sender = os.environ['SENDER']
ADMINS = [os.environ['ADMIN']]
subject = 'files'
body = 'Your files'
emails = []
attachments = []

base = Sq('handlers/mailsend')

inkb = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='Отправить', callback_data='send'))


# Регистрация юзера
class FSMAdmin(StatesGroup):
    email = State()


# @dp.message_handler(commands=['add_email'], state=None)
async def add_mail(message: types.Message):
    email = Sq.check_email(base, str(message.from_user.id))
    if len(email) == 0:
        await FSMAdmin.email.set()
        await bot.send_message(message.from_user.id, 'Введите свой email')
        await message.delete()
    else:
        await bot.send_message(message.from_user.id,
                               'У вас уже есть зарегестрированный email')
        await message.delete()


@dp.message_handler(state="*", commands='отмена')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('OK')


# @dp.message_handler(state=FSMAdmin.email)
async def adding(message: types.Message, state: FSMContext):
    email = message.text
    Sq.add_user(base, (str(message.from_user.id), email))
    await state.finish()
    await message.reply('OK')


# @dp.message_handler(commands=['start'])
async def starter(message: types.Message):
    try:
        if not path.exists('data/' + str(message.from_user.id)):
            make_folder(str(message.from_user.id))
            os.environ['USER_PATH'] = 'data/' + str(message.from_user.id)

        if not Sq.user_exist(base, str(message.from_user.id)):
            await bot.send_message(message.from_user.id, 'Email не найден в базе\n'
                                                         'наберите команду "/add_email"')
            await message.delete()
        else:
            email = Sq.check_email(base, str(message.from_user.id))
            await bot.send_message(message.from_user.id, f'Ваш email {str(email[0][0])}')
            await message.delete()
        del attachments[:]
    except:
        await message.reply('Общение с ботом через ЛС, напишите ему:\nhttps://t.me/send_kmf_mail_bot')


# @dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    await bot.send_message(message.from_user.id, 'Бот позволяет пересылать файлы на вашу почту\n'
                                                 'Сначала отправьте боту нужные файлы\n'
                                                 'После того как файлы будут загружены нажмите кнопку "отправить"')
    await message.delete()


# Проверка работы
# @dp.message_handler(commands=['test'])
async def take_test(message: types.Message):
    for admin in ADMINS:
        try:
            await dp.bot.send_message(admin, Sq.select_all(base))
            await message.delete()
        except Exception as err:
            logging.exception(err)


# Перехват фото, и запись путей и типов в список
# @dp.message_handler(content_types=['photo'])
async def handle_docs_photo(message: types.Message):
    before = datetime.datetime.now()
    #logger.warning('Before = {}', before)
    try:
        files = await bot.get_file(message.photo[-1].file_id)
        # await message.answer('data/' + str(message.from_user.id) + files.file_path[-12:])
        await bot.download_file_by_id(message.photo[-1].file_id,
                                      'data/' + str(message.from_user.id) + '/' + files.file_path[-12:])
        now = datetime.datetime.now()
        #logger.warning('Now = {}', now)
        #logger.info('{} {}', message.from_user.username,
                    'data/' + str(message.from_user.first_name) + '/' + files.file_path[-12:])
        if now - before > datetime.timedelta(seconds=1):
            await message.answer('Все сохранено', reply_markup=inkb)
    except Exception as e:
        await message.answer(f'{message.text}, {e}')


# Перехват документов и запись путей и типов в список
# @dp.message_handler(content_types=['document'])
async def handle_docs(message: types.Message):
    before = datetime.datetime.now()
    #logger.warning('Before = {}', before)
    try:
        files = await bot.get_file(message.document.file_id)
        #logger.debug('{}', message)
        await bot.download_file_by_id(message.document.file_id,
                                      'data/' + str(message.from_user.id) + '/' + files.file_path[-12:])
        now = datetime.datetime.now()
        #logger.warning('Before = {}', before)
        #logger.info('{} {}', message.from_user.first_name, 'data/' + str(message.from_user.id) +
                    '/' + files.file_path[-12:])
        if now - before > datetime.timedelta(seconds=1):
            await message.answer('Все сохранено', reply_markup=inkb)
    except Exception as e:
        await message.reply(str(e))


# Отправка
@dp.callback_query_handler(text='send')
async def email_send(callback: types.CallbackQuery):

    # устанавливаем путь до файлов
    path_to_file = 'data/' + str(callback.from_user.id)

    # Формируем список вложений
    for file in os.listdir('data/' + str(callback.from_user.id)):
        attachments.append(path_to_file + '/' + file)

    if len(attachments) != 0:
        # Формируем список адресов для пересылки
        email = Sq.check_email(base, callback.from_user.id)
        emails.append(email[0][0])

        # Устанавливаем соедиение с почтовым сервером
        credentials = Credentials(username=username, password=password)
        account = Account(primary_smtp_address=sender, credentials=credentials, autodiscover=True,
                          access_type=DELEGATE)

        # Отправка писем
        try:
            send_email(account, subject, body, emails, attachments)
            await bot.send_message(callback.from_user.id, f'Почта отправлена на адрес {email[0][0]}')
            await callback.answer()
            # await callback.delete()
            del attachments[:]
            del emails[:]
        except Exception as e:
            await callback.answer(f'Ошибка {str(e)}')
    else:
        await bot.send_message(callback.from_user.id, f'Нечего отправлять')
        # await callback.delete()


def register_handlers_users(dp: Dispatcher):
    dp.register_message_handler(add_mail, commands=['add_email'], state=None)
    dp.register_message_handler(adding, state=FSMAdmin.email)
    dp.register_message_handler(starter, commands=['start'])
    dp.register_message_handler(send_help, commands=['help'])
    dp.register_message_handler(take_test, commands=['test'])
    dp.register_message_handler(handle_docs_photo, content_types=['photo'])
    dp.register_message_handler(handle_docs, content_types=['document'])
    # dp.register_message_handler(email_send, commands=['send'])
    # dp.register_callback_query_handler(text='send', callback=)

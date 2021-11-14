from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


b1 = KeyboardButton('/start')
b2 = KeyboardButton('/help')
#b3 = KeyboardButton('/send')
add_email = KeyboardButton('/add_email')
admin_kb = KeyboardButton('/test')


kb_client = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_add_email = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_admin = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

kb_client.add(b1).insert(b2)
kb_add_email.add(add_email)
kb_admin.add(admin_kb)

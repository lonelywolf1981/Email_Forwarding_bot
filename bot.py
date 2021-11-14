from aiogram import executor

from create_bot import dp, on_startup
from handlers import users, other

users.register_handlers_users(dp)
other.register_handlers_other(dp)


executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

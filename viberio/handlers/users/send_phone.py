from aiogram.types import ParseMode
from aiogram.dispatcher.filters import CommandStart
from aiogram import types
from aiogram.utils.markdown import hbold

from loader import dp, db
from keyboards.default.share import phone_share_kb
from viberio.handlers import bot_registered_user


@dp.message_handler(CommandStart())
async def send_phone(message: types.Message):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    # full_name = message.from_user.full_name
    user = await db.get_user_data(user_id)
    print(user)
    if not user:
        await message.answer(user_name + hbold(",для початку роботи з сервісом поділіться Вашим номером телефону"),
                             parse_mode=ParseMode.HTML, reply_markup=phone_share_kb)
    else:
        await bot_registered_user(message)

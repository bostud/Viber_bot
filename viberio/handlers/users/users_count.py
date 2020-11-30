import asyncio

from aiogram import types
from loader import dp,db


@dp.message_handler(commands=['count'])
async def send_phone(message: types.Message):
    first_name = message.from_user.first_name
    users_count = await db.count_users()
    if users_count >= 4:
        await message.answer(f"{first_name},наразі кількість користувачів сервісу складає: {users_count} людей")
    else:
        await message.answer(f"{first_name},наразі кількість користувачів сервісу складає: {users_count} людина")



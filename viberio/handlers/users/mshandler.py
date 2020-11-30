import types
from loader import bot
from aiogram.types import ContentType, ParseMode
from aiogram import types
from loader import dp
# import dialogflow_v2beta1
#
# @dp.message_handler()
# async def bot_echo(message: types.Message):
#     await message.answer(message.text)
#

# @dp.message_handler()
# async def echo_message(msg: types.Message):
#     await bot.send_message(msg.from_user.id, msg.text)


@dp.message_handler(content_types=ContentType.ANY)
async def unknown_message(message: types.Message):
    message_text = f"{message.from_user.first_name}, чим я можу Вам допомогти?"
    await message.answer(message_text, parse_mode=ParseMode.HTML)

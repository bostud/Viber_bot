from aiogram import types
from aiogram.types import ContentType, InputFile
import os
# from functions.functions import qrcode_read
from loader import dp


# @dp.message_handler(content_types=ContentType.PHOTO)
# async def catch_photo(message: types.Message):
#     photo = await message.photo[-1].download()
#     photo = message.photo[-1]
#     # photo_bytes = InputFile(photo)
#     qrcode_read()
#     # await message.
#     # await message.answer("dsds")

from aiogram import types

from keyboards.default import menu_uk_kb_show
from loader import dp


@dp.message_handler(text='Українська🇺🇦')
async def show_menu(message: types.Message):
    await message.answer(f'Оберіть дію з меню👇', reply_markup=menu_uk_kb_show)

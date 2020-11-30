from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from keyboards.default import menu_uk_kb_show
from keyboards.default.location_buttons import location_kb
from keyboards.inline.poshtomat import poshtomat_s_kb
from loader import dp
from meest_api.geo_locations import search_poshtomat_geo

from states import Menu


@dp.callback_query_handler(text="За Вашим місцезнаходженням")
async def get_geo(call: CallbackQuery):
    await call.message.answer(text="Поділіться Вашим місцезнаходженням\n для пошуку найближчого поштомату 👇",
                              reply_markup=location_kb)
    await Menu.Search_poshtomat_location.set()


@dp.message_handler(state="*", text="До головного меню")
async def show_result(message: types.Message, state: FSMContext):
    await message.answer(text="Оберіть дію з меню 👇", reply_markup=menu_uk_kb_show)
    await state.finish()


@dp.message_handler(state=Menu.Search_poshtomat_location, content_types=types.ContentTypes.LOCATION)
async def show_result(message: types.Message, state: FSMContext):
    location = message.location
    latitude = location.latitude
    longitude = location.longitude
    result = "\n".join(search_poshtomat_geo(str(latitude), str(longitude)))
    await message.answer_sticker(r'CAACAgIAAxkBAAEBPpZfQka0AzlY9lM27s1XsfkFot8qXwACCgADnP4yMFsQVnkk-4rwGwQ')
    await message.answer(
        f'Список найближчих відділень: {result}',
        parse_mode=types.ParseMode.HTML, reply_markup=poshtomat_s_kb, disable_web_page_preview=True)
    await message.answer(text="Оберіть дію з меню 👇", reply_markup=menu_uk_kb_show)
    await state.finish()

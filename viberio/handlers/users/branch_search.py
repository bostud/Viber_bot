import json

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.markdown import hbold

from meest_api.geo_locations import search_br_location
from keyboards.default import menu_uk_kb_show
from keyboards.default.location_buttons import location_kb
from keyboards.inline import branch_search_kb
from loader import dp, db
from meest_api.location import branch_search, search_post_location
from states import Menu
from datetime import datetime


@dp.callback_query_handler(text="Cancel2", state="*")
async def cancel(call: CallbackQuery, state: FSMContext):
    await call.message.delete_reply_markup()
    # await call.message.edit_text(text="Оберіть дію з меню 👇")
    await call.message.answer(hbold("Ви повернулися до головного меню"), reply_markup=menu_uk_kb_show)
    await state.finish()


@dp.callback_query_handler(text="go_back", state="*")
async def cancel(call: CallbackQuery, state: FSMContext):
    # await call.message.delete_reply_markup(
    await call.message.delete()
    # await call.message.edit_text(text="Оберіть дію з меню 👇")
    await call.message.answer(hbold("Оберіть, будь ласка, спосіб пошуку поштоматів Meest"),
                              reply_markup=branch_search_kb)
    await state.finish()


@dp.message_handler(text="Пошук поштоматів")
async def show_tracking(message: types.Message):
    # user_id = message.from_user.id
    # print(user_id)
    # data = {
    #     "info": {
    #         "event_date": datetime.now(),
    #         "user_name": message.from_user.full_name,
    #         "poshtomat_num": "Блаблабла",
    #         "status": "Получено",
    #         ""
    #     }
    # }
    # new = json.dumps(data)
    # print(type(data))
    # await db.add_data_info(user_id, new)
    await message.answer(hbold('Оберіть, будь ласка, спосіб пошуку поштоматів Meest'),
                         reply_markup=branch_search_kb)


# Поиск по номеру отделения
@dp.callback_query_handler(lambda query: query.data == "by_number")  # Хендлер для поиска отделения
async def branch_search_number(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.insert(types.InlineKeyboardButton(text="Назад", callback_data='go_back'))
    await call.message.answer(hbold("Введіть номер поштомату"), reply_markup=keyboard)
    await Menu.Branch_search.set()


# Поиск по номеру отделения
@dp.message_handler(state=Menu.Branch_search)  # Функция поиска отделения по номеру
async def search_by_number(message: types.Message, state: FSMContext):
    branch_num = message.text
    result = "\n".join(branch_search(branch_num))
    await message.answer(f"{result}")
    await message.answer(hbold("Оберіть дію з меню, або продовжуйте пошук потрібного відділення"),
                         reply_markup=branch_search_kb)
    await state.finish()


# Поиск по адресу
@dp.callback_query_handler(lambda query: query.data == "by_address", state="*")
async def search_by_address(call: CallbackQuery):
    await call.message.delete()
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.insert(types.InlineKeyboardButton(text=f"Назад", callback_data='go_back'))
    await call.message.answer("Введіть текст у форматі: <b>Місто, вулиця</b> 👇", reply_markup=keyboard,
                              parse_mode=types.ParseMode.HTML)
    await Menu.Search_br_by_address.set()


# Поиск по адресу
@dp.message_handler(state=Menu.Search_br_by_address)
async def search_by_address(message: types.Message, state: FSMContext):
    address = message.text
    await state.update_data(address=address)
    result = "\n".join(search_post_location(address))
    await message.answer(f'{result}')
    await message.answer(hbold("Оберіть дію з меню, або продовжуйте\n пошук"),
                         reply_markup=branch_search_kb)
    await state.finish()


@dp.callback_query_handler(lambda query: query.data == "by_shipment_num")
async def search_by_address(call: CallbackQuery):
    await call.message.delete()
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.insert(types.InlineKeyboardButton(text="Назад", callback_data='go_back'))
    await call.message.answer(hbold("Введіь номер відправленяя"), reply_markup=keyboard,
                              parse_mode=types.ParseMode.HTML)
    await Menu.Search_by_num.set()


# Поиск по локации
@dp.callback_query_handler(lambda query: query.data == "by_location")
async def search_by_geo(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer(hbold("Для пошуку найближчих поштоматів поділіться своєю локацією"),
                              parse_mode=types.ParseMode.HTML, reply_markup=location_kb)
    await Menu.Search_br_by_location.set()


# Поиск по локации
@dp.message_handler(state=Menu.Search_br_by_location, content_types=types.ContentTypes.LOCATION)
async def search_by_geo_location(message: types.Message, state: FSMContext):
    location = message.location
    latitude = location.latitude
    longitude = location.longitude
    result = "\n".join(search_br_location(str(latitude), str(longitude)))
    await message.answer(f'{result}')
    await message.answer(text="<b>Оберіть дію з меню</b>", reply_markup=branch_search_kb)
    await state.finish()

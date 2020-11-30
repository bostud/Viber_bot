from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.markdown import hcode, hbold
from numpy.core.defchararray import isdigit

from meest_api.create_parcel import create_parcel
from meest_api.location import poshtomat_num_to_id, branch_search, search_post_location
from keyboards.inline import cod_kb
from keyboards.inline.calback_datas import box_sizes
from keyboards.inline.create import create_parcel_kb
from loader import dp, bot, db
from aiogram import types
from states import ParcelCreate, SearchByAddress
import re


# @dp.message_handler(lambda query: query == "parcel_cre", state="*")
# async def start_dialog(message: types.Message):
#     await message.answer(hcode(
#         """Для створення посилки Вам потрібно вказати формат вантажу, поштомат для відправлення та поштомат отримання,ім'я отримувача і телефон."""))
#     size = open('data/img/sizes.png', 'rb')
#     await bot.send_photo(message.from_user.id, size, reply_markup=create_parcel_kb)


#
@dp.callback_query_handler(lambda query: query.data == "parcel_cre", state="*")
async def creat_parcel(call: CallbackQuery, state: FSMContext):
    size = open('data/img/sizes.png', 'rb')
    await call.message.edit_text(hcode(
        "Для створення посилки Вам потрібно вказати формат вантажу, поштомат для відправлення та поштомат отримання,ім'я отримувача і телефон."),
        parse_mode=types.ParseMode.HTML)
    await bot.send_photo(call.from_user.id, size, reply_markup=create_parcel_kb)
    await state.finish()


# Хендлер реагирует на кнопку з главного меню "Нове відправлення"
@dp.message_handler(text='Нове відправлення')
async def start_dialog(message: types.Message):
    await message.answer(hcode(
        """Для створення посилки Вам потрібно вказати формат вантажу, поштомат для відправлення та поштомат отримання,ім'я отримувача і телефон."""))
    size = open('data/img/sizes.png', 'rb')
    await bot.send_photo(message.from_user.id, size, reply_markup=create_parcel_kb)


# -------------------------------------------------------------------------------------
# Хендлеры для callback_query_data c стандартизированными размерами посылок для почтоматов
# Ширина(width)*Высота(height)*Глубина(length)
# Малая яч. 370*115*590мм.
# Сред. яч. 370*180*590мм.
# Больш. яч. 370*365*590мм.
#  "gabaritesMax": {
#           "length": 61,
#           "width": 37,
#           "height": 35
#         },

# Хендлер маленького размера посылки
@dp.callback_query_handler(box_sizes.filter(weight="0.589", volume="0.002"))
async def small_parcel(call: CallbackQuery, callback_data: dict, state: FSMContext):
    parcel_data = {
        'weight': float(callback_data['weight']),
        'volume': float(callback_data['volume'])}
    print(parcel_data)
    await call.message.delete()
    await state.update_data(parcel_size=parcel_data)
    await bot.answer_callback_query(callback_query_id=call.id)
    await call.answer(cache_time=60)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton(text="До головного меню", callback_data="Cancel3"))
    await call.message.answer(hbold("Введіть номер Вашого поштомату"), reply_markup=keyboard)
    await ParcelCreate.get_sender_br_num.set()


@dp.callback_query_handler(box_sizes.filter(weight="0.589", volume="0.003"))
async def small_parcel(call: CallbackQuery, callback_data: dict, state: FSMContext):
    parcel_data = {
        'weight': float(callback_data['weight']),
        'volume': float(callback_data['volume'])}
    print(parcel_data)
    await call.message.delete()
    await state.update_data(parcel_size=parcel_data)
    await bot.answer_callback_query(callback_query_id=call.id)
    await call.answer(cache_time=60)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton(text="До головного меню", callback_data="Cancel3"))
    await call.message.answer(hbold("Введіть номер Вашого поштомату"), reply_markup=keyboard)
    await ParcelCreate.get_sender_br_num.set()


# Хендлер среднего размера посылки
@dp.callback_query_handler(box_sizes.filter(weight="0.589", volume="0.037"))
async def medium_parcel(call: CallbackQuery, callback_data: dict, state: FSMContext):
    parcel_data = {
        'weight': float(callback_data['weight']),
        'volume': float(callback_data['volume'])}
    print(parcel_data)
    await call.message.delete()
    await state.update_data(parcel_size=parcel_data)
    await bot.answer_callback_query(callback_query_id=call.id)
    await call.answer(cache_time=60)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton(text="До головного меню", callback_data="Cancel3"))
    await call.message.answer(hbold("Введіть номер Вашого поштомату"), reply_markup=keyboard)
    await ParcelCreate.get_sender_br_num.set()


# Хендлер большого размера посылки
@dp.callback_query_handler(box_sizes.filter(weight="0.589", volume="0.074"))
async def big_parcel(call: CallbackQuery, callback_data: dict, state: FSMContext):
    parcel_data = {
        'weight': float(callback_data['weight']),
        'volume': float(callback_data['volume'])}
    await call.message.delete()
    await state.update_data(parcel_size=parcel_data)
    await bot.answer_callback_query(callback_query_id=call.id)
    await call.answer(cache_time=60)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton(text="До головного меню", callback_data="Cancel3"))
    await call.message.answer(hbold("Введіть номер Вашого поштомату"), reply_markup=keyboard)
    await ParcelCreate.get_sender_br_num.set()


# ---------------------------------------------------------------------

@dp.message_handler(regexp="^\d{4}$", state=ParcelCreate.get_sender_br_num)
async def sender(message: types.Message, state: FSMContext):
    chat_id = message.from_user.id
    sender_post_num = poshtomat_num_to_id(message.text)
    if sender_post_num is False:
        await bot.send_sticker(chat_id, r"CAACAgIAAxkBAAEBV_hfY3oxV-wJjpmg-gY-tQ8vKTEPHgACCwADnP4yMPctMM3hxWgtGwQ")
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Відмінити дію", callback_data="Cancel3"))
        await message.answer(text='Оберіть дію з меню', reply_markup=keyboard)
        return await bot.send_message(chat_id, f"Поштомат під номером {message.text} не існує\n"
                                               "Спробуйте ще раз 👇")
    await state.update_data(sender_poshtomat_num=message.text)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Пошук поштомату отримувача",
                                            callback_data="by_rec_address"))
    keyboard.add(types.InlineKeyboardButton(text="До головного меню",
                                            callback_data="Cancel3"))
    # await message.answer('Оберіть дію з поштоматом 👇', reply_markup=keyboard)
    result = "\n".join(branch_search(message.text))
    await message.answer(f"{result}", parse_mode=types.ParseMode.HTML,
                         disable_web_page_preview=True)
    await state.update_data(sender_post_id=sender_post_num)
    await message.answer(hbold("Введіть номер поштомату отримувача,\nчи проведіть пошук поштомату"),
                         reply_markup=keyboard)
    await ParcelCreate.get_res_br_num.set()


@dp.callback_query_handler(lambda query: query.data == "by_rec_address", state="*")
async def search_by_address(call: CallbackQuery):
    await call.message.delete()
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.insert(types.InlineKeyboardButton(text="До головного меню", callback_data='Cancel3'))
    await call.message.answer("Введіть текст у форматі: <b>Місто, вулиця</b> 👇", reply_markup=keyboard,
                              parse_mode=types.ParseMode.HTML)
    await SearchByAddress.SE1.set()


# @dp.callback_query_handler(lambda query: query.data == "back_to_enter_num", state=SearchByAddress)
# async def search_by_address(call: CallbackQuery):
#     await call.message.delete()
#     keyboard = types.InlineKeyboardMarkup(row_width=2)
#     # keyboard.insert(types.InlineKeyboardButton(text="Назад", callback_data='back_to_enter_num'))
#     await call.message.answer(text="Введіть номер поштомату отримувача 👇", reply_markup=keyboard,
#                               parse_mode=types.ParseMode.HTML)
#     await SearchByAddress.SE1.set()


# Поиск по адресу
@dp.message_handler(state=SearchByAddress.SE1)
async def search_by_address(message: types.Message, state: FSMContext):
    await message.delete()
    address = message.text
    await state.update_data(address=address)
    result = "\n".join(search_post_location(address))
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.insert(types.InlineKeyboardButton(text="Повторити пошук", callback_data='by_rec_address'))
    keyboard.insert(types.InlineKeyboardButton(text="До головного меню", callback_data='Cancel3'))
    await message.answer(f'{result}', reply_markup=keyboard)
    await message.answer(hbold("Введіть номер поштомату отримувача"))
    await ParcelCreate.get_res_br_num.set()


# @dp.callback_query_handler(lambda query: re.match(r"by_address", query.data), state=ParcelCreate.get_res_br_num)
# async def search_by_address(call: CallbackQuery):
#     await call.message.delete()
#     keyboard = types.InlineKeyboardMarkup(row_width=2)
#     keyboard.insert(types.InlineKeyboardButton(text=f"Назад", callback_data='go_back'))
#     await call.message.answer("Введіть текст у форматі: <b>Місто, вулиця</b> 👇", reply_markup=keyboard,
#                               parse_mode=types.ParseMode.HTML)
#     await Menu.Search_br_by_address.set()
#
#
# # Поиск по адресу
# @dp.message_handler(state=Menu.Search_br_by_address)
# async def search_by_address(message: types.Message, state: FSMContext):
#     address = message.text
#     await state.update_data(address=address)
#     result = "\n".join(search_post_location(address))
#     await message.answer(f'{result}')
#     await message.answer(text="Оберіть дію з меню, або продовжуйте\n пошук"
#                               "найближчих відділень до потрібної адреси",
#                          reply_markup=branch_search_kb)
#     await state.finish()

@dp.message_handler(regexp="^\d{4}$", state=ParcelCreate.get_res_br_num)
async def show_menu_parcel_size(message: types.Message, state: FSMContext):
    await state.update_data(res_poshtomat_num=message.text)
    chat_id = message.from_user.id
    res_post_num = poshtomat_num_to_id(message.text)
    if res_post_num is False:
        await bot.send_sticker(chat_id, r"CAACAgIAAxkBAAEBV_hfY3oxV-wJjpmg-gY-tQ8vKTEPHgACCwADnP4yMPctMM3hxWgtGwQ")
        return await bot.send_message(chat_id, f"Поштомат отримувача під номером {message.text} не існує\n"
                                               "Спробуйте ще раз 👇, або скористайтесь пошуком поштоматів")
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="До головного меню",
                                            callback_data="Cancel3"))  # Разобраться с надписью "Оберіть дію з поштоматом"
    result = "\n".join(branch_search(message.text))
    await message.answer(f"{result}", parse_mode=types.ParseMode.HTML,
                         disable_web_page_preview=True)
    await state.update_data(re_post_num=res_post_num)
    await message.answer(hbold("Введіть прізвище та ім'я отримувача "), reply_markup=keyboard)
    await ParcelCreate.get_res_fio.set()


@dp.message_handler(state=ParcelCreate.get_res_fio)
async def show_menu_parcel_size(message: types.Message, state: FSMContext):
    chat_id = message.from_user.id
    res_full_name = message.text
    # print(len(res_full_name))
    # if not re.match(r"([А-ЯЁ][а-яё]+[\-\s]?){3,}", res_full_name):
    #     await bot.send_sticker(chat_id, r"CAACAgIAAxkBAAEBV_hfY3oxV-wJjpmg-gY-tQ8vKTEPHgACCwADnP4yMPctMM3hxWgtGwQ")
    #     return await bot.send_message(chat_id,
    #                                   f"У ПІБ не може бути числових значень, або мати не коректний формат вводу\n"
    #                                   "Спробуйте ще раз 👇")
    await state.update_data(res_full_name=res_full_name)
    await message.answer(hbold("Введіть номер телефону отримувача у форматі:") + hcode("0501111111"),
                         parse_mode=types.ParseMode.HTML)
    # await state.update_data(message_id1=mess_to_del['message_id'])
    # print(mess_to_del)
    await ParcelCreate.get_res_phone.set()


@dp.message_handler(state=ParcelCreate.get_res_phone)
async def show_menu_parcel_size(message: types.Message, state: FSMContext):
    chat_id = message.from_user.id
    res_phone = message.text
    if res_phone == '0501111111':
        return await message.answer(hbold("Ви ввели номер телефону из прикладу\n"
                                          "будь ласка введіть номер телефону отримувача👇"))
    if not re.match(r'^[0]{1}[0-9]{9}$', res_phone):
        await bot.send_sticker(chat_id, r"CAACAgIAAxkBAAEBV_hfY3oxV-wJjpmg-gY-tQ8vKTEPHgACCwADnP4yMPctMM3hxWgtGwQ")
        return await bot.send_message(chat_id, hbold("Введений номер телефону: ") + hcode(res_phone) + hbold(
            "не відповідає формату\nСпробуйте ще раз"), parse_mode=types.ParseMode.HTML)
    res_phone = "38" + res_phone
    print(res_phone)
    await state.update_data(res_phone=res_phone)
    # data = await state.get_data()
    # message_id = data['message_id1']
    # print(data)
    # await bot.delete_message(chat_id,message_id)
    await message.answer(hbold("Чи бажаєте вказати суму післяплати?"), reply_markup=cod_kb,
                         parse_mode=types.ParseMode.HTML)
    await ParcelCreate.get_res_cod.set()


# @dp.callback_query_handler(state=ParcelCreate.get_res_cod)
# async def cod_pay_question(call: CallbackQuery, state: FSMContext):
#     await call.message.delete()
#     cod = types.InlineKeyboardMarkup(row_width=2)
#     cod.add(types.InlineKeyboardButton("Так", callback_data="True"))
#     cod.add(types.InlineKeyboardButton("Ні", callback_data="False"))
#     cod.add(types.InlineKeyboardButton("До головного меню", callback_data="Cancel3"))
#     await call.message.answer("Чи бажаєте вказати суму післяплати?", reply_markup=cod,
#                               parse_mode=types.ParseMode.HTML)
#     await ParcelCreate.get_res_cod_sum.set()


@dp.callback_query_handler(lambda query: re.match(r"cod_true|cod_false", query.data),
                           state=ParcelCreate.get_res_cod)  # Кто оплачивает
async def cod_pay(call: CallbackQuery, state: FSMContext):
    print("попал куда нужно")
    if 'cod_true' in call.data:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(types.InlineKeyboardButton("Відмінити дію", callback_data="Cancel3"))
        await call.message.edit_text(hbold("Введіть сумму післяплати у грн.\n"
                                           "Приклад: 1000"), reply_markup=keyboard)
        await ParcelCreate.get_res_cod_sum.set()
    if 'cod_false' in call.data:
        print("Cod нет")
        # await state.update_data(if_cod=call.data)
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(types.InlineKeyboardButton("Я", callback_data="False"))
        keyboard.add(types.InlineKeyboardButton("Отримувач", callback_data="True"))
        keyboard.add(types.InlineKeyboardButton("Відмінити дію", callback_data="Cancel3"))
        await call.message.edit_text(hbold("Хто оплачує відправлення?"), reply_markup=keyboard)
        await ParcelCreate.get_res_pay.set()


@dp.message_handler(state=ParcelCreate.get_res_cod_sum)
async def cod_amount(message: types.Message, state: FSMContext):
    print(message.text)
    amount_cod = message.text
    if re.match(r'^([1-9]|[1-9][0-9]|[1-9][0-9][0-9]|[1-9][0-9][0-9][0-9]|[1][0]{4})$', amount_cod):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("До головного меню", callback_data="Cancel3"))
        await message.answer(hbold("Введіть, будь ласка, номер банківської картки для повернення післяплати"),
                             reply_markup=keyboard)
        await state.update_data(amount_cod=amount_cod)
        await ParcelCreate.get_res_card_num.set()
        print("подходит")
    else:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("До головного меню", callback_data="Cancel3"))
        return await message.answer(
            "Сума післяплати не може дорівнювати 0 або бути більшою за 10000, та мати літери у своєму складі\n"
            "Повторіть ввод, або поверніться до головного меню", reply_markup=keyboard)


@dp.message_handler(state=ParcelCreate.get_res_card_num)
async def cod_amount(message: types.Message, state: FSMContext):
    print(message.text)
    card_number = message.text
    if re.match(r'^[0-9]{16}$', card_number):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("До головного меню", callback_data="Cancel3"))
        await message.answer(
            hbold("Введіть, будь ласка, Ім’я та Прізвище власника картки латиницею. Приклад вводу: IVAN SHEVCHENKO"),
            reply_markup=keyboard)
        await state.update_data(card_number=card_number)
        await ParcelCreate.get_res_card_name.set()
        print("подходит")
    else:
        menu_kb = types.InlineKeyboardMarkup()
        menu_kb.row(types.InlineKeyboardButton("До головного меню", callback_data="Cancel3"))
        return await message.answer(
            "Номер банковської карти складється з 16 цифр, та не може мати літери у своєму складі\n"
            "Повторіть ввод, або поверніться до головного меню",
            reply_markup=menu_kb)


@dp.message_handler(state=ParcelCreate.get_res_card_name)
async def cod_amount(message: types.Message, state: FSMContext):
    print(message.text)
    cardholder_name = message.text.upper()
    print(cardholder_name)
    await state.update_data(cardholder_name=cardholder_name)
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton("Я", callback_data="False"))
    keyboard.add(types.InlineKeyboardButton("Отримувач", callback_data="True"))
    keyboard.add(types.InlineKeyboardButton("До головного меню", callback_data="Cancel3"))
    await message.delete()
    await message.answer(hbold("Хто оплачує відправлення?"), reply_markup=keyboard)
    await ParcelCreate.get_res_pay.set()


# if isdigit(amount_cod) is False:
#     print("не число")
# else:
#     print(amount_cod)
#     print(type(amount_cod))
# # if isdigit(amount_cod) is False or amount_cod <= 0:
#     keyboard = types.InlineKeyboardMarkup()
#     keyboard.add(types.InlineKeyboardButton("До головного меню", callback_data="Cancel3"))
#     await message.answer(hbold("У значенні післяплати не може бути літер, тільки цифри від 1 до 1000\n"
#                                   "Повторіть вашу спробу з правильним значенням"), reply_markup=keyboard, disable_notification=False)
#     await state.update_data(amount_cod=amount_cod)
#     return await ParcelCreate.get_res_cod_sum.set()

# print(a)
# print(amount_cod)
# if int(amount_cod) <= 0:
#     keyboard = types.InlineKeyboardMarkup()
#     keyboard.add(types.InlineKeyboardButton("До головного меню", callback_data="Cancel3"))
#     await message.edit_text(hbold("У значенні післяплати не може бути літер, тільки цифри від 1 до 1000\n"
#                                   "Повторіть вашу спробу з правильним значенням"), reply_markup=keyboard)
#     await state.update_data(amount_cod=amount_cod)
#     return await ParcelCreate.get_res_cod_sum
# else:
#     print("другое")
#     return await ParcelCreate.get_res_cod_sum


@dp.callback_query_handler(lambda query: re.match(r"True|False", query.data),
                           state=ParcelCreate.get_res_pay)  # Кто оплачивает
async def take_from_postomat(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    who_pay = call.data
    print("Попал в хендлер оплаты")
    print(who_pay)
    await call.message.delete_reply_markup()
    await state.update_data(who_pay=who_pay)
    data = await state.get_data()
    print(data)
    # {'parcel_size': {'weight': 0.589, 'volume': 0.002}, 'sender_poshtomat_num': '4966',
    #  'sender_post_id': 'bd5f4052-dceb-11e8-80d7-1c98ec135261', 'res_poshtomat_num': '4966',
    #  're_post_num': 'bd5f4052-dceb-11e8-80d7-1c98ec135261', 'res_full_name': '0507723091', 'res_phone': '380507723091',
    #  'amount_cod': '12', 'card_number': 'IVAB', 'who_pay': 'True'}
    user_data = await db.get_user_data(call.from_user.id)
    user_phone = user_data['phone_number']
    sender_name = user_data['full_name']
    sender_poshtomat_num = data['sender_poshtomat_num']
    res_poshtomat_num = data['res_poshtomat_num']
    res_full_name = data['res_full_name']
    res_phone = data['res_phone']
    if 'amount_cod' in data:
        cardholder_name = data['cardholder_name']
        cod = data['amount_cod']
        card_number = data['card_number']
        parcel_info = f'<b>Відправник </b>: {hbold(sender_name)}\n' \
                      f'{hcode(user_phone)}\n' \
                      f'Дані отримання післяплати:  {hcode(cardholder_name)}\n' \
                      f'{hcode(card_number)}\n' \
                      f'Поштомат №:  {hcode(sender_poshtomat_num)}\n' \
                      f'<b>Отримувач </b>: {hcode(res_full_name)}\n' \
                      f'<b>Післяплата </b>: {hcode(cod)} грн\n' \
                      f'{hcode(res_phone)}\n' \
                      f'Поштомат №: {hcode(res_poshtomat_num)}\n'
        await call.message.edit_text(f"{parcel_info}")
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(types.InlineKeyboardButton(text="Створити", callback_data="create_parcel"))
        keyboard.add(types.InlineKeyboardButton(text="До головного меню", callback_data="Cancel3"))
        await call.message.answer(hbold('Якщо усі дані вірні, натисніть створити'), reply_markup=keyboard)
        await ParcelCreate.get_result.set()
    else:
        print(f"То что мне нужно{data}")
        parcel_info = f'<b>Відправник </b>: {hbold(sender_name)}\n' \
                      f'{hcode(user_phone)}\n' \
                      f'Поштомат №:  {hcode(sender_poshtomat_num)}\n' \
                      f'<b>Отримувач </b>: {hcode(res_full_name)}\n' \
                      f'{hcode(res_phone)}\n' \
                      f'Поштомат №: {hcode(res_poshtomat_num)}\n'
        print(parcel_info)
        await call.message.edit_text(f"{parcel_info}")
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(types.InlineKeyboardButton(text="Створити", callback_data="create_parcel"))
        keyboard.add(types.InlineKeyboardButton(text="До головного меню", callback_data="Cancel3"))
        await call.message.answer(hbold('Якщо усі дані вірні, натисніть створити'), reply_markup=keyboard)
        await ParcelCreate.get_result.set()


@dp.callback_query_handler(lambda query: re.match(r"create_parcel", query.data), state=ParcelCreate.get_result)
async def get_result_create_parcel(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    print(data)
    # await call.message.delete()
    # await call.message.edit_text()
    await call.message.delete_reply_markup()
    # res_phone = message.text
    user_data = await db.get_user_data(call.from_user.id)

    who_pay = data['who_pay']
    user_phone = user_data['phone_number']
    sender_name = user_data['full_name']
    sender_post_id = data.get("sender_post_id")
    re_post_num = data.get("re_post_num")
    re_full_name = data.get("res_full_name")
    parcel_size = data.get('parcel_size')
    res_phone = data['res_phone']
    sender_poshtomat_num = data['sender_poshtomat_num']
    await db.add_parcels_created(call.from_user.id)
    await state.update_data(user_phone=user_phone)
    await state.update_data(poshtomat_num=sender_poshtomat_num)
    result = create_parcel(sender_name, user_phone, sender_post_id,  # Камментим для теста
                           re_full_name, res_phone, re_post_num, parcel_size, who_pay)
    await call.message.edit_text(result, parse_mode=types.ParseMode.HTML)
    # await state.finish()
    my_parcels = types.InlineKeyboardMarkup()
    my_parcels.row(types.InlineKeyboardButton(text="Відправити зараз",
                                              callback_data="send_parcel_yes"))
    my_parcels.row(types.InlineKeyboardButton(text="До головного меню",
                                              callback_data="Cancel3"))
    await call.message.answer(hbold("Ви можете відправити посилку зараз,\nабо повернутися до головного меню?"),
                              reply_markup=my_parcels)
    await state.reset_state(with_data=False)

# @dp.callback_query_handler(lambda query: query.data == "send_parcel", state="*")
# async def send_parcel(call: CallbackQuery, state: FSMContext):
#     await call.message.delete()
#     keyboard = types.InlineKeyboardMarkup()
#     keyboard.add(types.InlineKeyboardButton(text=f"До головного меню", callback_data="Cancel3"))
#     await call.message.answer(hcode("Для повернення до головного меню 👇"), reply_markup=keyboard)
#     await call.message.answer(
#         text=call.from_user.first_name + ", введіть номер поштомату з якого\nВи бажаєте відправити посилку👇")
#     await MenuPoshtomat.P1_1.set()

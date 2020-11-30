from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery, ParseMode
import re

from aiogram.utils.markdown import hbold

from meest_api.get_payment_data import get_payment_data
from meest_api.pay import pay_by_portmone_my_parcels
from meest_api.poshtomatApi import parcel_debt_new, my_parcel_debt
from functions.functions import if_data_in_response
from keyboards.default import menu_uk_kb_show
from keyboards.default.share import phone_share_kb
from keyboards.inline.my_parcels import my_parcels_callback_kb
from loader import dp, db
from meest_api.appApi import parcels_for_delivery_in
from asgiref.sync import sync_to_async


@dp.message_handler(Text("Мої відправлення"))
async def my_parcels(message: types.Message):
    await message.answer(
        f"{message.from_user.first_name}, <code>отримайте інформацію по Відправленням які прямують до Вас чи від Вас.\n"
        f"Ви можете оплатити, відслідкувати чи отримати підтримку від наших операторів.</code>",
        reply_markup=my_parcels_callback_kb, parse_mode=types.ParseMode.HTML)


@dp.callback_query_handler(text="my_parcels")  # Хендлер для inline кнопки из создать посылку
async def my_parcels(call: CallbackQuery):
    await call.message.delete_reply_markup()
    await call.message.edit_text(call.from_user.first_name + hbold(", оберіть фільтр для Ваших відправлень"),
                                 reply_markup=my_parcels_callback_kb)


@dp.callback_query_handler(lambda query: re.match(r"in", query.data))
async def parcel_modes(call: CallbackQuery):
    user_id = call.from_user.id
    data = call.data
    print(data)
    # await bot.answer_callback_query(callbry(caack_query_id=call.id)
    await call.answer(cache_time=60)
    user_data = await if_data_in_response(await db.get_user_data(user_id))
    if user_data is False:
        return await call.message.answer(
            call.from_user.first_name + hbold(", для початку роботи з сервісом поділіться Вашим номером телефону\n"
                                              "за допомогою кнопки знизу 👇"), reply_markup=phone_share_kb)
    else:
        print(user_data)
        user_phone = user_data['phone_number']
        print(user_phone)
        result = await sync_to_async(parcels_for_delivery_in)(user_phone, data)
    if result is False:
        await call.message.delete_reply_markup()
        await call.message.delete()
        await call.message.answer(call.from_user.first_name + hbold(
            ", до Вас на даний момент не прямують відправлення.\nСкористайтеся іншими функціями з головного меню."),
                                  reply_markup=menu_uk_kb_show)
    else:
        for i in result:
            if i['debt_cost'] != 0:
                keyboard = types.InlineKeyboardMarkup(row_width=2)
                keyboard.insert(types.InlineKeyboardButton(text=f"Детальний трекінг", callback_data=i['num']))
                keyboard.insert(types.InlineKeyboardButton(text="Сформувати рахунок", callback_data=i['pay_num']))
                keyboard.insert(types.InlineKeyboardButton(text="Підтримка", url='t.me/MeestSupport_bot'))
                keyboard.add(types.InlineKeyboardButton(text="Сховати", callback_data="die"))
                await call.message.answer(
                    i['text'],
                    parse_mode=types.ParseMode.HTML, reply_markup=keyboard)
            elif i['debt_cost'] == 0:
                debt = i['debt_cost']
                debt = 'Відправлення сплачено відправником'
                keyboard = types.InlineKeyboardMarkup(row_width=2)
                keyboard.insert(types.InlineKeyboardButton(text=f"Детальний трекінг", callback_data=i['num']))
                keyboard.insert(types.InlineKeyboardButton(text="Підтримка", url='t.me/MeestSupport_bot'))
                keyboard.add(types.InlineKeyboardButton(text="Сховати", callback_data="die"))
                await call.message.answer(
                    i['text'],
                    parse_mode=types.ParseMode.HTML, reply_markup=keyboard)
        await call.message.answer(f"{call.from_user.first_name} ,оберіть фільтр для Ваших відправлень👇",
                                  reply_markup=my_parcels_callback_kb)


# Хендлер кнопки оплатить отправка
@dp.callback_query_handler(lambda query: re.match(r"pay_data_in", query.data))
async def pay_in(call: CallbackQuery, state: FSMContext):
    data = call.data
    print(data)
    parcel_num = data.replace('pay_data_in', '')
    get_data = get_payment_data(parcel_num, "")
    print(get_data)
    print(get_data)
    split_pay = get_data['split_pay']
    shipment_uid = get_data['shipment_uid']
    # pay_type = get_data['type']
    description = get_data['description']
    total_amount = my_parcel_debt(shipment_uid)
    print(total_amount)
    total_to_pay = total_amount['Total']
    pay_link = pay_by_portmone_my_parcels(parcel_num, total_to_pay, split_pay, shipment_uid, description)
    pay_button = types.InlineKeyboardMarkup(row_width=2)
    pay_button.insert(
        types.InlineKeyboardButton(text=f"💸 Оплатити {total_to_pay} грн", callback_data="pay_my_parcel_in",
                                   url=pay_link))
    # pay_button.insert(types.InlineKeyboardButton(text="Підтверджую оплату", callback_data="my_parcels_pay_confirm"))
    pay_button.add(types.InlineKeyboardButton(text="Відмінити дію", callback_data="Cancel3"))
    await call.message.edit_reply_markup(reply_markup=pay_button)
    # await call.message.edit_text(description, parse_mode=types.ParseMode.HTML, reply_markup=pay_button)
    # await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=pay_button)
    await state.finish()


@dp.callback_query_handler(lambda query: query.data == "my_parcels_pay_confirm")
async def pay_checkout_query(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    parcel_id = data['parcel_id_in']
    parcel_res = parcel_debt_new(parcel_id)
    # await call.message.answer(f"РЕЗУЛЬТАТ{parcel_res}")
    res_amount = parcel_res
    pay_link = data['pay_link']  # раскоментить
    if parcel_res == 0:
        await call.message.delete()
        await call.message.answer("Все сплачено!")
    if res_amount > 0:
        await call.message.delete()
        pay_button = types.InlineKeyboardMarkup(row_width=2)
        pay_button.row(types.InlineKeyboardButton(text=f"💸 Оплатити {res_amount} грн", callback_data="pay",
                                                  url=pay_link))
        pay_button.row(types.InlineKeyboardButton(text="Сховати", callback_data="Cancel3"))
        await call.message.edit_reply_markup(reply_markup=pay_button)
        await state.finish()

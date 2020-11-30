from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ParseMode
import re

from aiogram.utils.markdown import hbold

from meest_api.get_payment_data import get_payment_data
from meest_api.location import search_my_parcels
from meest_api.pay import pay_by_portmone_my_parcels
from meest_api.poshtomatApi import get_parcel_info, parcel_debt_new
from functions.functions import if_data_in_response
from keyboards.default.share import phone_share_kb
from keyboards.inline.my_parcels import my_parcels_callback_kb
from loader import dp, db
from meest_api.appApi import parcels_for_delivery_out
from asgiref.sync import sync_to_async


@dp.callback_query_handler(text="my_parcels")  # Хендлер для inline кнопки из создать посылку
async def my_parcels(call: CallbackQuery):
    await call.message.delete_reply_markup()
    await call.message.edit_text(f"{call.from_user.first_name} ,<b>оберіть фільтр для Ваших відправлень</b>",
                                 reply_markup=my_parcels_callback_kb)


# Хендлер отправления посылки
@dp.callback_query_handler(lambda query: query.data == "out")
async def parcel_modes(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    data = call.data
    await state.update_data(button_mode=data)
    print(data)
    await call.answer(cache_time=60)
    user_data = await if_data_in_response(await db.get_user_data(user_id))
    if user_data is False:
        return await call.message.answer(
            call.from_user.first_name + hbold(", для початку роботи з сервісом поділіться Вашим номером телефону\n"
                                              "за допомогою кнопки знизу 👇"), reply_markup=phone_share_kb)
    else:
        print(user_data)
        user_phone = user_data['phone_number']
        result = await sync_to_async(parcels_for_delivery_out)(user_phone, data)
    if result is False:
        # await call.message.delete_reply_markup()
        await call.message.delete()
        create_parcel = types.InlineKeyboardMarkup(row_width=2)
        create_parcel.add(types.InlineKeyboardButton(text="Створити", callback_data="parcel_cre"))
        create_parcel.add(types.InlineKeyboardButton(text="До головного меню", callback_data="Cancel3"))
        await call.message.answer(call.from_user.first_name + hbold(", створених відправлень ще не має. Створити?"),
                                  reply_markup=create_parcel)
    else:
        for i in result:
            if i['debt_cost'] != 0:
                keyboard = types.InlineKeyboardMarkup(row_width=2)
                keyboard.insert(types.InlineKeyboardButton(text="Детальний трекінг", callback_data=i['num']))
                keyboard.insert(types.InlineKeyboardButton(text="Сформувати рахунок", callback_data=i['pay_num_out']))
                keyboard.insert(types.InlineKeyboardButton(text="Підтримка", url='t.me/MeestSupport_bot'))
                # keyboard.insert(types.InlineKeyboardButton(text="Обрати час доставки(розробка)", callback_data="in"))
                keyboard.add(types.InlineKeyboardButton(text="Сховати", callback_data="die"))
                await call.message.answer(
                    i['text'],
                    parse_mode=types.ParseMode.HTML, reply_markup=keyboard)
            elif i['debt_cost'] == 0:
                keyboard = types.InlineKeyboardMarkup(row_width=2)
                keyboard.insert(types.InlineKeyboardButton(text=f"Детальний трекінг", callback_data=i['num']))
                keyboard.insert(types.InlineKeyboardButton(text="Підтримка", url='t.me/MeestSupport_bot'))
                # keyboard.insert(types.InlineKeyboardButton(text="Обрати час доставки(розробка)", callback_data="in"))
                keyboard.add(types.InlineKeyboardButton(text="Сховати", callback_data="die"))
                await call.message.answer(
                    i['text'],
                    parse_mode=types.ParseMode.HTML, reply_markup=keyboard)
        await call.message.answer(call.from_user.first_name + hbold(", оберіть фільтр для Ваших відправлень"),
                                  reply_markup=my_parcels_callback_kb)
        # await state.reset_state(with_data=False)


# Хендлер кнопки оплатить отправка
@dp.callback_query_handler(lambda query: re.match(r"pay_data_out", query.data))
async def pay_out(call: CallbackQuery, state: FSMContext):
    data = call.data
    print(data)
    parcel_num = data.replace('pay_data_out', '')
    get_data = await sync_to_async(get_payment_data)(parcel_num, "")
    print(get_data)
    split_pay = get_data['split_pay']
    print(split_pay)
    shipment_uid = get_data['shipment_uid']
    # pay_type = get_data['type']
    description = get_data['description']
    total_amount = parcel_debt_new(shipment_uid)
    total_to_pay = total_amount['total']
    pay_link = await sync_to_async(pay_by_portmone_my_parcels)(parcel_num, total_to_pay,
                                                               split_pay, shipment_uid, description)
    print(pay_link)
    pay_button = types.InlineKeyboardMarkup(row_width=2)
    pay_button.row(
        types.InlineKeyboardButton(text=f"💸 Оплатити {total_to_pay} грн", callback_data="Cancel3",
                                   url=pay_link))
    pay_button.row(types.InlineKeyboardButton(text="Сховати", callback_data="Cancel3"))
    await call.message.edit_reply_markup(reply_markup=pay_button)
    await state.finish()


@dp.callback_query_handler(lambda query: re.match(r"!><", query.data))
async def in_mode(call: CallbackQuery, state: FSMContext):
    data = call.data
    state_data = await state.get_data()
    print(state_data)
    num = data.replace('!><', '')
    print(num)
    parcel_info = await sync_to_async(get_parcel_info)(num)
    result = ("\n".join(search_my_parcels(num)))
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text=f"Сховати", callback_data="Cancel3"))
    await call.message.edit_text(parcel_info + result, parse_mode=types.ParseMode.HTML, reply_markup=keyboard)
    await state.finish()

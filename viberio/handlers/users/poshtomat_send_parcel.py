from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.markdown import hcode, hbold

from meest_api.get_payment_data import get_payment_data
from meest_api.location import poshtomat_info
from meest_api.pay import pay_by_portmone_my_parcels
from meest_api.poshtomatApi import parcels_list, parcel_debt, get_token_sender, verify_token, customer_insert, \
    customer_insert_conform, my_parcel_debt
from keyboards.default import menu_uk_kb_show
from keyboards.inline import branch_search_kb
from loader import dp
from states import ParcelInsert, NewParcel


@dp.callback_query_handler(lambda query: query.data == "search", state="*")
async def poshtomat_search(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer('<b>Оберіть, будь ласка, спосіб пошуку поштоматів Meest</b>',
                              reply_markup=branch_search_kb)
    await state.finish()


# Хендлер для вложения посылки в почтомат
@dp.callback_query_handler(lambda query: query.data == "send_parcel_yes", state="*")
async def choose_in(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    data = await state.get_data()
    # print(data)
    user_phone = data.get("user_phone")  # берем номер телефона
    # user_phone = "380507723091"  # тест отправки
    poshtomat_num = data.get("poshtomat_num")
    # poshtomat_num = "6077"  # тест отправки
    poshtomat_id_ref = poshtomat_info(poshtomat_num)
    await state.update_data(poshtomatIDRef=poshtomat_id_ref)
    print(user_phone)
    print(poshtomat_num)  # берем номер почтомата
    print("Это Хендлер словил нажататие in")
    result = parcels_list(poshtomat_num, user_phone)
    if result is False:
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.row(types.InlineKeyboardButton(text="Так", callback_data="parcel_cre"))
        keyboard.row(types.InlineKeyboardButton(text="Ні", callback_data="Cancel3"))
        await call.message.edit_text(call.from_user.first_name + hbold(
            ", у Вас не має створених посилок для вкладення у поштомат №:") + hcode(poshtomat_num) +
                                     hbold("\nБажаєте створити?"), reply_markup=keyboard)
        return await NewParcel.PL1.set()  # Разобраться со стейтом
    else:
        await state.update_data(choose_in_result=result)
        await call.message.answer(hcode('Оберіть Ваше відправлення для вкладення у поштомат'))
        for i in result:
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text="Відправити", callback_data=i['id']))
            await call.message.answer(
                i['text'],
                parse_mode=types.ParseMode.HTML, reply_markup=keyboard)
        main_menu = types.InlineKeyboardMarkup()
        main_menu.add(types.InlineKeyboardButton(text="До головного меню", callback_data="Cancel3"))
        await call.message.answer("Для повернення у головне меню", reply_markup=main_menu)
    await ParcelInsert.Insert1.set()


# Хендлер отправки
@dp.callback_query_handler(state=ParcelInsert.Insert1)
# Хендлер для id посылки отправления
# {'result_code': 200, 'result_info': 'ok', 'result': {'Error': '20', 'ErrorDetails': ' Немає вільних комірок розміруL'}}
async def catch_callback_in(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    parcel_id = call.data
    print(parcel_id)
    # print(call.data)
    # print("Попало в хендлер отправления")
    await state.update_data(parcel_id_in=parcel_id)
    data = await state.get_data()
    r = list(filter(lambda x: x['id'] == parcel_id, data['choose_in_result']))
    if r:
        num = r[0]['num']
        await state.update_data(parcel_num=num)
        # await state.update_data(choose_in_result=None)
    else:
        print("НЕ нашел")
        return await state.finish()
    parcel_res = parcel_debt(parcel_id, call.from_user.first_name)
    # amount = parcel_res['result']['Total']
    if parcel_res is True:
        await call.message.answer(
            hbold("Все сплачено!"))
        token_sender = get_token_sender(parcel_id)
        print(token_sender)
        await state.update_data(token_sender=token_sender)
        await call.message.answer(
            hbold("На Ваш мобільний телефон буде відправлено СMC з кодом варіфікації введіть його в телеграм"))
        return await ParcelInsert.Insert3.set()
    else:
        data = await state.get_data()
        parcel_num = data['parcel_num']
        amount = parcel_res['result']['Total']
        get_data = get_payment_data(parcel_num, amount)
        print(get_data)
        split_pay = get_data['split_pay']
        shipment_uid = get_data['shipment_uid']
        # pay_type = get_data['type']
        description = get_data['description']
        total_amount = my_parcel_debt(shipment_uid)
        total_to_pay = total_amount['Total']
        pay_link_in = pay_by_portmone_my_parcels(parcel_num, total_to_pay, split_pay, shipment_uid, description)
        print(pay_link_in)
        await state.update_data(pay_link_in=pay_link_in)  # Раскоментить
        pay_button = types.InlineKeyboardMarkup(row_width=2)
        pay_button.add(types.InlineKeyboardButton(text=f"💸 Оплатити {amount} грн", callback_data="pay",
                                                  url=pay_link_in))
        pay_button.add(types.InlineKeyboardButton(text="Підтверджую оплату", callback_data="payment_confirm"))
        # pay_button.add(types.InlineKeyboardButton(text="Відмінити дію", callback_data="Cancel3"))
        await call.message.edit_reply_markup(reply_markup=pay_button)
        await ParcelInsert.Insert2.set()


# Подтверждение платежа
@dp.callback_query_handler(lambda query: query.data == "payment_confirm", state=ParcelInsert.Insert2)
async def pay_checkout_query(call: CallbackQuery, state: FSMContext):
    # await call.answer(cache_time=30)
    data = await state.get_data()
    parcel_id = data['parcel_id_in']
    parcel_res = my_parcel_debt(parcel_id)
    res_amount = parcel_res['Total']
    print(parcel_res)
    # await call.message.answer(f"РЕЗУЛЬТАТ{parcel_res}")
    pay_link = data['pay_link_in']  # раскоментить
    if res_amount == 0:
        await call.message.delete()
        await call.answer(call.from_user.first_name + hcode(", Ваша посилка оплачена"), show_alert=True)
        token_sender = get_token_sender(parcel_id)
        await state.update_data(token_sender=token_sender)
        await call.message.answer(
            hbold("На Ваш мобільний телефон буде відправлено СMC з кодом варіфікації введіть його в телеграм"),
            parse_mode=types.ParseMode.HTML)
        await ParcelInsert.Insert3.set()
    if res_amount != 0:
        pay_button = types.InlineKeyboardMarkup(row_width=2)
        pay_button.add(types.InlineKeyboardButton(text=f"💸 Оплатити {res_amount} грн", callback_data="pay",
                                                  url=pay_link))
        pay_button.add(types.InlineKeyboardButton(text="Підтверджую оплату", callback_data="payment_confirm"))
        await call.answer(call.from_user.first_name + ", Ваша посилка ще не оплачена", show_alert=True)
        # pay_button.add(types.InlineKeyboardButton(text="До головного меню", callback_data="Cancel3"))
        return await call.message.edit_reply_markup(reply_markup=pay_button)


# Отправление
@dp.message_handler(state=ParcelInsert.Insert3)
async def to_sender(message: types.Message, state: FSMContext):
    data = await state.get_data()
    print(data)
    token_sender = data['token_sender']  # Получаем токен отправителя
    password = message.text
    result = verify_token(token_sender, password)
    if result == 104:
        return await message.answer(hbold("Невірний код з СМС"))
    if result == 103:
        await message.delete()
        await message.answer(hbold("Ви вичерпали усі спроби, та повернулися до головного меню"),
                             reply_markup=menu_uk_kb_show)
        return await state.finish()
    if result is True:
        door_open = types.InlineKeyboardMarkup()
        door_open.add(types.InlineKeyboardButton(text="Вкласти", callback_data="insert"))
        door_open.add(types.InlineKeyboardButton(text="Відмінити дію", callback_data="Cancel3"))
        await message.answer(hbold('Тепер ви можете відкрити комірку для вкладення у поштомат'), reply_markup=door_open)
        # await state.reset_state(with_data=False)
        await ParcelInsert.Insert4.set()


# Отправление  - вложение в почтомат
@dp.callback_query_handler(lambda query: query.data == "insert", state=ParcelInsert.Insert4)
async def insert_in_poshtomat(call: CallbackQuery, state: FSMContext):
    print("ХЕНДЛЕР СЛОВИЛ insert")
    data = await state.get_data()
    print(data)
    token_sender = data['token_sender']
    poshtomat_id_ref = data['poshtomatIDRef']
    parcel_id_in = data['parcel_id_in']
    parcel_num = data['parcel_num']
    trans_id = customer_insert(token_sender, poshtomat_id_ref, parcel_id_in, parcel_num)  # Функция вложения в почтомат
    print(trans_id)
    # await call.message.answer(trans_id)
    # a = "543aa7ede0243f3138096eb6e85bd4a1"
    if 'transID' not in trans_id:
        error = trans_id['ErrorDetails']
        await call.message.delete()
        await call.message.answer(text=error, reply_markup=menu_uk_kb_show)
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.insert(types.InlineKeyboardButton(text="Підтримка", url='t.me/MeestSupport_bot'))
        await call.message.answer("Зателефонуйте за номерами нашої лінії підтримки поштоматів:\n"
                                  "+380673735753\n"
                                  "+380503735753\n"
                                  "Або зверніться до наших операторів у чаті 👇", parse_mode=types.ParseMode.HTML,
                                  reply_markup=keyboard)  # Кликабельные кнопки
        return await state.finish()
    else:
        trans_id = trans_id['transID']
        await state.update_data(trans_id=trans_id)
        # await call.message.answer(
        #     f"{call.from_user.first_name}, комірка відкрита 👉 покладіть Ваше відправлення всередину")
        confirm_kb = types.InlineKeyboardMarkup()
        confirm_kb.add(types.InlineKeyboardButton(text="Підтвердження вкладення в поштомат", callback_data="confirm"))
        await call.message.edit_text(
            call.from_user.first_name + ", комірка відкрита 👉 покладіть Ваше відправлення всередину",
            reply_markup=confirm_kb)
        # await bot.answer_callback_query(callback_query_id=call.id)
        await call.answer(cache_time=60)
    await ParcelInsert.Insert5.set()


# Вложение и подтверждение отправки
@dp.callback_query_handler(lambda query: query.data == "confirm", state=ParcelInsert.Insert5)
async def confirm_handler(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    data = await state.get_data()
    token_sender = data['token_sender']
    poshtomat_id_ref = data['poshtomatIDRef']
    parcel_id_in = data['parcel_id_in']
    parcel_num = data['parcel_num']
    trans_id = data['trans_id']
    result = customer_insert_conform(token_sender, poshtomat_id_ref, parcel_id_in,
                                     trans_id)  # Функция подтверждения вложения
    print(result)
    await call.message.answer(
        call.from_user.first_name + hbold(",Ваше відправлення номер: ") + hcode(parcel_num) + hbold(
            "відправлене!\nДякуємо Вам за користування послугами компанії Meest"), reply_markup=menu_uk_kb_show)
    print("ПОСЫЛКА УСПЕШНО ОТПРАВЛЕНА!!")
    await state.finish()

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.markdown import hcode, hbold

from meest_api.get_payment_data import get_payment_data
from meest_api.location import poshtomat_num_to_id, branch_search, poshtomat_info
from meest_api.pay import pay_by_portmone_my_parcels
from meest_api.poshtomatApi import parcels_list_out, parcel_debt, verify_token, \
    get_token_receiver, customer_remove, customer_remove_repeat, \
    my_parcel_debt
from keyboards.default import menu_uk_kb_show
from loader import dp, db
from states import MenuPoshtomat, ParcelTake


# Хендлер текста из главного меню
@dp.message_handler(text="Відкрити комірку")
async def door_open(message: types.Message, state: FSMContext):
    await message.delete()
    keyboard = types.InlineKeyboardMarkup()
    # keyboard.add(types.InlineKeyboardButton(text=f"Відправити посилку", callback_data="send_parcel_yes"))
    keyboard.add(types.InlineKeyboardButton("До головного меню", callback_data="Cancel3"))
    await message.answer(
        message.from_user.first_name + hbold(", введіть номер поштомату з якого\nВи бажаєте отримати відправлення"),
        reply_markup=keyboard)
    await MenuPoshtomat.P1_1.set()


@dp.message_handler(regexp="^\d{4}$", state=MenuPoshtomat.P1_1)
async def enter_post_num(message: types.Message, state: FSMContext):
    mess = message.text
    res_post_num = poshtomat_num_to_id(mess)  # Получаем id из номера потомата
    await state.update_data(postomat_id=res_post_num)  # Заносим id в стейт
    if res_post_num is False:  # проверка существует ли почтомат
        await message.answer_sticker(r"CAACAgIAAxkBAAEBV_hfY3oxV-wJjpmg-gY-tQ8vKTEPHgACCwADnP4yMPctMM3hxWgtGwQ")
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="До головного меню", callback_data="Cancel3"))
        await message.answer('Для повернення до головного меню, скасуйте операцію', reply_markup=keyboard)
        return await message.answer(hbold("Поштомат під номером: ") + hcode(message.text) + hbold("не існує\nСпробуйте ще раз"))
    else:
        poshtomat_id_ref = poshtomat_info(message.text)
        await state.update_data(poshtomatIDRef=poshtomat_id_ref)
        poshtomat_num = message.text
        await state.update_data(poshtomat_num=poshtomat_num)
        user_id = message.from_user.id
        user_data = await db.get_user_data(user_id)
        user_phone = user_data['phone_number']
        print(user_phone)
        await state.update_data(user_phone=user_phone)
        await message.answer_sticker(r"CAACAgIAAxkBAAEBWclfZnya3xNdppAKqMv3U_pxremMfAACDAADnP4yMAvSYoYcS3C6GwQ")
        result = "\n".join(branch_search(message.text))
        await message.answer(f"{result}", parse_mode=types.ParseMode.HTML)
        # data = await state.get_data()
        print("ЭТО ХЕНДЛЕР OUT")
        # print(data)
        # user_phone = data.get("user_phone")  # берем номер телефона
        # poshtomat_num = data.get("poshtomat_num")  # берем номер почтомата
        result = parcels_list_out(poshtomat_num, user_phone)
        await state.update_data(choose_out_result=result)
    if result is False:
        keyboard_send_parcel = types.InlineKeyboardMarkup()
        keyboard_send_parcel.row(types.InlineKeyboardButton(text="Так", callback_data="send_parcel_yes"))
        keyboard_send_parcel.row(types.InlineKeyboardButton(text="Ні", callback_data="Cancel3"))
        await message.answer(
            message.from_user.first_name + hbold(",для Вас не має посилок для отримання у поштоматі №:") + hcode(
                poshtomat_num) + hbold("\nБажаєте відправити посилку?"),
            reply_markup=keyboard_send_parcel)
        return state.finish()
    else:
        await message.answer('Оберіть Вашу посилку для отримання у поштоматі')
        for i in result:
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text=f"Отримати", callback_data=i['id']))
            keyboard.add(types.InlineKeyboardButton(text=f"До головного меню", callback_data="Cancel3"))
            await message.answer(
                i['text'],
                parse_mode=types.ParseMode.HTML, reply_markup=keyboard)
        main_menu = types.InlineKeyboardMarkup()
        main_menu.add(types.InlineKeyboardButton(text=f"До головного меню", callback_data="Cancel3"))
        # await message.answer("Для повернення у головне меню", reply_markup=main_menu)
    # keyboard = types.InlineKeyboardMarkup()
    # keyboard.add(types.InlineKeyboardButton(text="Отримати", callback_data="parcels_out"))
    # keyboard.add(types.InlineKeyboardButton(text="Відправити", callback_data="parcels_in"))
    # keyboard.add(types.InlineKeyboardButton(text=f"До головного меню", callback_data="Cancel2"))
    # await message.answer('Оберіть дію з поштоматом 👇', reply_markup=keyboard)
    await ParcelTake.Take1.set()


@dp.callback_query_handler(state=ParcelTake.Take1)
async def choose_out(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    parcel_id = call.data
    print(call.data)
    print("Попало в хендлер получить")
    await state.update_data(parcel_id_out=parcel_id)
    data = await state.get_data()
    # post_num = data['num']
    r = list(filter(lambda x: x['id'] == parcel_id, data['choose_out_result']))
    if r:
        num = r[0]['num']
        await state.update_data(parcel_num=num)
        # await state.update_data(choose_out_result=None)
    else:
        print("НЕ нашел")
        return await state.finish()
    parcel_res = parcel_debt(parcel_id, call.from_user.first_name)
    print(parcel_res)
    if parcel_res is True:
        await call.message.answer(hbold("Посилка оплачена"))
        token_receiver = get_token_receiver(parcel_id)
        await state.update_data(token_receiver=token_receiver)
        print(data)
        # await call.message.answer(f"{parcel_debt(parcel_id, call.from_user.first_name)}")
        await call.message.answer(
            hbold("На Ваш мобільний телефон буде відправлено СMC з кодом варіфікації введіть його в телеграм"))
        await ParcelTake.Take3.set()
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
        pay_link_out = pay_by_portmone_my_parcels(parcel_num, total_to_pay, split_pay, shipment_uid, description)
        print(pay_link_out)
        await state.update_data(pay_link_in=pay_link_out)  # Раскоментить
        pay_button = types.InlineKeyboardMarkup(row_width=2)
        pay_button.add(types.InlineKeyboardButton(text=f"💸 Оплатити {amount} грн", callback_data="pay_out",
                                                  url=pay_link_out))
        pay_button.add(types.InlineKeyboardButton(text="Підтверджую оплату", callback_data="payment_confirm_out"))
        # pay_button.add(types.InlineKeyboardButton(text="До головного меню", callback_data="Cancel3"))
        # await call.message.delete()
        await call.message.edit_reply_markup(reply_markup=pay_button)
        await ParcelTake.Take2.set()
        # await state.finish()


# Подтверждение платежа получение посылки
@dp.callback_query_handler(lambda query: query.data == "payment_confirm_out", state=ParcelTake.Take2)
async def pay_checkout_out_query(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    print(data)
    parcel_id_out = data['parcel_id_out']
    parcel_res = my_parcel_debt(parcel_id_out)
    res_amount = parcel_res['Total']
    pay_link_out = data['pay_link_out']  # раскоментить
    if parcel_res == 0:
        await call.message.delete()
        await call.answer("Посилка оплачена", show_alert=True)
        token_receiver = get_token_receiver(parcel_id_out)
        await state.update_data(token_receiver=token_receiver)
        await call.message.answer(
            hbold("На Ваш мобільний телефон буде відправлено СMC з кодом варіфікації введіть його в телеграм"))
        return await ParcelTake.Take3.set()
    if res_amount != 0:
        pay_button = types.InlineKeyboardMarkup(row_width=2)
        pay_button.add(types.InlineKeyboardButton(text=f"💸 Оплатити {res_amount} грн", callback_data="pay_out",
                                                  url=pay_link_out))
        pay_button.add(types.InlineKeyboardButton(text="Підтверджую оплату", callback_data="payment_confirm_out"))
        await call.answer(call.from_user.first_name + ", Ваша посилка ще не оплачена", show_alert=True)
        pay_button.add(types.InlineKeyboardButton(text="До головного меню", callback_data="Cancel3"))
        return await call.message.edit_reply_markup(reply_markup=pay_button)


# Получение из почтомата до мене
@dp.message_handler(state=ParcelTake.Take3)
async def to_receiver(message: types.Message, state: FSMContext):
    data = await state.get_data()
    print("Вы попали в стейт получения")
    token_receiver = data['token_receiver']
    poshtomat_id_ref = data['poshtomatIDRef']
    parcel_id_out = data['parcel_id_out']
    password = message.text
    result = verify_token(token_receiver, password)
    if result == 104:
        return await message.answer("Невірний код з СМС")
    if result == 103:
        await message.delete()
        await message.answer("Ви вичерпали усі спроби, та повернулися до головного меню", reply_markup=menu_uk_kb_show)
        return await state.finish()
    if result is True:
        # await message.answer(f"Тепер ви можете відкрити комірку для отримання Вашого відправлення")
        print("Забрать с почтомата")
        trans_id = customer_remove(token_receiver, poshtomat_id_ref, parcel_id_out)  # Функция вложения в почтомат
        print(trans_id)
        if 'transID' not in trans_id:
            await message.delete()
            error = trans_id['ErrorDetails']
            await message.answer(hbold(error))
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            keyboard.insert(types.InlineKeyboardButton(text="Підтримка", url='t.me/MeestSupport_bot'))
            await message.answer("Зателефонуйте за номерами нашої лінії підтримки поштомтів:\n"
                                 "+380673735753\n"
                                 "+380503735753\n"
                                 "Або зверніться до наших операторів у чаті 👇", parse_mode=types.ParseMode.HTML,
                                 reply_markup=keyboard)
            await message.answer("Ви повернулися до головного меню", reply_markup=menu_uk_kb_show)
            await state.finish()
        else:
            trans_id = trans_id['transID']
            print(trans_id)
            await state.update_data(trans_id_out=trans_id)
            confirm_kb = types.InlineKeyboardMarkup()
            confirm_kb.add(types.InlineKeyboardButton(text="Так я забрав посилку", callback_data="yes"))
            confirm_kb.add(types.InlineKeyboardButton(text="Ні комірка ще зачинена", callback_data="no"))
            await message.answer(message.from_user.first_name + hbold(
                ",якщо комірка відкрита,заберіть своє відправлення, та зачиніть комірку"),
                                 reply_markup=confirm_kb)
            # await message.answer(reply_markup=confirm_kb)
            # await bot.answer_callback_query(callback_query_id=call.id)
            await state.reset_state(with_data=False)


# ПОЛУЧЕНИЕ
# @dp.callback_query_handler(lambda query: query.data == "take_out", state=ParcelTake.Take4)
# async def take_from_postomat(call: CallbackQuery, state: FSMContext):
#     # result = customer_insert()
#     # parcel_id = call.data
#     # {'postomat_id': 'e1f2e8b7-508e-11e9-80dd-1c98ec135261', 'poshtomat_num': '6077', 'user_phone': '380507723091',
#     # 'token_out': '2ffda9ca2d3f74a07cb3c69d8a4c598e'}
#     print("Забрать с почтомата")
#     data = await state.get_data()
#     print(f"State DATA {data}")
#     token_receiver = data['token_receiver']
#     poshtomat_id_ref = data['poshtomatIDRef']
#     parcel_id_out = data['parcel_id_out']
#     # parcel_num = data['parcel_num']
#     trans_id = customer_remove(token_receiver, poshtomat_id_ref, parcel_id_out)  # Функция вложения в почтомат
#     # await call.message.answer(f"State DATA {trans_id}")
#     print(trans_id)
#     if 'transID' not in trans_id:
#         await call.message.delete()
#         error = trans_id['ErrorDetails']
#         await call.message.answer(hbold(error))
#         keyboard = types.InlineKeyboardMarkup(row_width=2)
#         keyboard.insert(types.InlineKeyboardButton(text="Підтримка", url='t.me/MeestSupport_bot'))
#         await call.message.answer("Зателефонуйте за номерами нашої лінії підтримки поштомтів:\n"
#                                   "+380673735753\n"
#                                   "+380503735753\n"
#                                   "Або зверніться до наших операторів у чаті 👇", parse_mode=types.ParseMode.HTML,
#                                   reply_markup=keyboard)
#         await call.message.answer("Ви повернулися до головного меню", reply_markup=menu_uk_kb_show)
#         await state.finish()
#     else:
#         trans_id = trans_id['transID']
#         print(trans_id)
#         await state.update_data(trans_id_out=trans_id)
#         await call.message.answer(
#             f"{call.from_user.first_name}, якщо комірка відкрита👉 заберіть своє відправлення, та зачиніть комірку")
#         confirm_kb = types.InlineKeyboardMarkup()
#         confirm_kb.add(types.InlineKeyboardButton(text="Так я забрав відправлення", callback_data="yes"))
#         confirm_kb.add(types.InlineKeyboardButton(text="Ні комірка ще зачинена", callback_data="no"))
#         await call.message.edit_reply_markup(reply_markup=confirm_kb)
#         # await bot.answer_callback_query(callback_query_id=call.id)
#         await state.reset_state(with_data=False)


# ПОЛУЧЕНИЕ
@dp.callback_query_handler(lambda query: query.data == "yes")
async def yes(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    chat_id = call.message.from_user.id
    await db.add_parcels_received(call.from_user.id)
    # await call.message.delete()
    await call.message.delete_reply_markup()
    await call.message.answer(call.from_user.first_name + hbold(", дякуємо Вам за користування послугами Meest!"))
    await state.finish()


@dp.callback_query_handler(lambda query: query.data == "no")
async def no(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    chat_id = call.message.from_user.id
    data = await state.get_data()
    print(f"State DATA {data}")
    token_receiver = data['token_receiver']
    poshtomat_id_ref = data['poshtomatIDRef']
    parcel_id_out = data['parcel_id_out']
    trans_id = data['trans_id_out']
    # parcel_num = data['parcel_num']
    customer_remove_repeat(token_receiver, poshtomat_id_ref, parcel_id_out, trans_id)
    # await call.message.delete()
    await db.add_door_not_opened(call.from_user.id)
    await call.message.delete_reply_markup()
    await call.message.answer(call.from_user.first_name + hbold(
        ",дякуємо, за користування послугами Meest\nзаберіть посилку та зачиніть будь ласка комірку"),
                              reply_markup=menu_uk_kb_show)
    await state.finish()

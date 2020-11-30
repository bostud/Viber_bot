from aiogram import types
from aiogram.dispatcher import FSMContext

from aiogram.types import CallbackQuery
from aiogram.utils.markdown import hbold

from functions.functions import if_data_in_response
from keyboards.default import menu_uk_kb_show
from keyboards.default.share import phone_share_kb
from keyboards.inline.my_parcels import my_parcels_callback_kb
from loader import dp, bot, db
from meest_api.appApi import parcels_delivery_archive
from asgiref.sync import sync_to_async


@dp.callback_query_handler(lambda query: query.data == "archive")
async def parcel_mode_archive(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    data = call.data
    print(data)
    await bot.answer_callback_query(callback_query_id=call.id)
    await call.answer(cache_time=60)
    user_data = await if_data_in_response(await db.get_user_data(user_id))
    if user_data is False:
        return await call.message.answer(
            call.from_user.first_name + hbold(", для початку роботи з сервісом поділіться Вашим номером телефону\n"
                                              "за допомогою кнопки знизу 👇"), reply_markup=phone_share_kb)
    user_phone = user_data['phone_number']
    print(user_phone)
    result = await sync_to_async(parcels_delivery_archive)(user_phone, data)
    if result is False:
        await call.message.delete_reply_markup()
        await call.message.delete()
        await call.message.answer(call.from_user.first_name + hbold(
            ", на цей час у Вас не має архівних посилок."), reply_markup=menu_uk_kb_show)
    # Нужно чтоб номер посылки заносился во все кнопки по очереди
    # result = (parcels_for_delivery(user_phone, data))
    else:
        for i in result:
            await call.message.answer(
                i['text'],
                parse_mode=types.ParseMode.HTML)
            await call.message.answer(f"{call.from_user.first_name} ,<b>оберіть фільтр для Ваших відправлень</b>",
                              reply_markup=my_parcels_callback_kb)

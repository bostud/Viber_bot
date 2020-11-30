import json

from aiogram import types
from aiogram.utils.markdown import hbold

from viberio.meest_api.test import format_data_json
from loader import dp, db


@dp.message_handler(text="Відстежити відправлення")
async def to_parcel(message: types.Message):
    main_menu = types.InlineKeyboardMarkup()
    # user_id = message.from_user.id
    # old_json = await db.get_users_json(user_id)
    # print(old_json)
    # parcels_created = await db.get_parcels_created()
    # parcels_sent = await db.get_parcels_sent()
    # parcels_received = await db.get_parcels_received()
    # door_not_opened = await db.get_door_not_opened()
    # await message.answer(f"<b>Відправлено:</b> {parcels_sent}\n"
    #                      f"<b>Отримано:</b> {parcels_received}\n"
    #                      f"<b>Створено:</b> {parcels_created}\n")
    #                      # f"<b>Отримано(Повторне відкриття комірки):</b> {door_not_opened} \n"
    #                      # f"<b>Всього:</b> {parcels_sent+parcels_received}")
    # events = await db.get_data_events(message.from_user.id)
    data = {"menu": {
  "id": "file",
  "value": "File",
  "popup": {
    "menuitem": [
      {"value": "New", "onclick": "CreateNewDoc()"},
      {"value": "Open", "onclick": "OpenDoc()"},
      {"value": "Close", "onclick": "CloseDoc()"}
    ]
  }
}}
    res = await db.get_users_json(message.from_user.id)
    existed_data = json.loads(res)
    print(existed_data)

    new_data = await format_data_json(message.from_user.full_name,
                                      message.from_user.id, "4966",
                                      "Отправлено успешно", "None", "None")
    print(new_data)
    existed_data = [existed_data, new_data]
    existed_data_str = json.dumps(existed_data, indent=2)
    await db.update_data_info(message.from_user.id, existed_data_str)

    # f'UPDATE users SET data_info = {existed_data_str}  WHERE id={message.from_user.id}'
    main_menu.add(types.InlineKeyboardButton(text="До головного меню", callback_data="Cancel3"))
    await message.answer('<code>Отримуйте інформацію про актуальний статус відправлення</code>',
                         parse_mode=types.ParseMode.HTML, reply_markup=main_menu)
    await message.answer(hbold('Введіть номер відправлення'))
#
#     await Menu.Parcel_search.set()
#
#
# @dp.message_handler(state=Menu.Parcel_search)
# async def parcel_handler(message: types.Message, state: FSMContext):
#     parcel_num = message.text
#     result = ("\n".join(await sync_to_async(parcel_search)(parcel_num)))
#     print(result)
#     if result is False:
#         await message.answer(
#             '<b>Неможливо знайти посилку за таким номером</b>',
#             parse_mode=types.ParseMode.HTML, reply_markup=menu_uk_kb_show)
#     else:
#         await message.answer(
#             f'{result}',
#             parse_mode=types.ParseMode.HTML, reply_markup=menu_uk_kb_show)
#     await state.finish()

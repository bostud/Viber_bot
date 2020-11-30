from aiogram.types import ParseMode
from aiogram.utils.markdown import hbold
from asyncpg import exceptions
from keyboards.default import menu_uk_kb_show
from aiogram import types
from loader import dp, db
from functions.functions import if_plus_in_phone


@dp.message_handler(content_types=types.ContentTypes.CONTACT)
async def bot_start(message: types.Message):
    user_id = message.contact.user_id
    full_name = message.contact.full_name
    phone_number = message.contact.phone_number
    phone_number = if_plus_in_phone(phone_number)
    date_time = message.date
    try:
        await db.add_user(user_id, full_name, phone_number, str(date_time))
    except exceptions.UniqueViolationError:
        pass
    await message.answer_sticker(r'CAACAgIAAxkBAAEBQwFfRtU_4TFyEl8Ro3siT5nG8WovKQACHwADnP4yMCBW8jz3ttrRGwQ')
    await message.answer(f'<b>Ласкаво просимо, {message.from_user.first_name}!</b> '
                         f'\nМене звати Meest Поштомат бот', parse_mode=ParseMode.HTML,
                         reply_markup=menu_uk_kb_show)


async def bot_registered_user(message: types.Message):
    await message.answer_sticker(r'CAACAgIAAxkBAAEBUFpfWK8xpKRPi0E1inVYx_8M8K1k7gACDAADnP4yMAvSYoYcS3C6GwQ')
    await message.answer(hbold("З поверненням," + message.from_user.first_name + "!\nОберіть дію з меню"),
                         parse_mode=ParseMode.HTML,
                         reply_markup=menu_uk_kb_show)


@dp.message_handler(text='Підтримка')
async def send_service(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    # keyboard.add(types.InlineKeyboardButton(text=f"Відправити посилку", callback_data="send_parcel_yes"))
    keyboard.add(types.InlineKeyboardButton(text=f"Отправить", callback_data="send_parcel_yes"))
    await message.answer("Тест отправка", reply_markup=keyboard)
    await message.answer(
        f"{message.from_user.first_name}, зверніться до наших операторів в чат 👉 @MeestSupport_bot, або\n"
        f"зателефонуйте за номерами нашої лінії підтримки поштоматів:\n"
        f"+380673735753\n"
        f"+380503735753\n", reply_markup=menu_uk_kb_show)

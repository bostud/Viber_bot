from loader import dp
from aiogram import types
from aiogram.dispatcher.filters import Text


@dp.message_handler(
    Text(equals=['Привет', 'Привіт', 'звати', 'Допоможи', 'Ти кто', 'Подскажи', 'Посилку'], ignore_case=True),
    state="*")
async def my_parcels(message: types.Message):
    question = message.text
    if 'Привет' in question:
        await message.answer("Доброго дня, чим я можу Вам допомогти?")
    if 'Посилку' in question:
        await message.answer("Вам треба обрати з головного меню пункт 'Нове відправлення'"
                             ", та слідкувати за моїми підказками, після створення посилки ви зможете відправити її")
    if 'Допоможи' or 'допоможи':
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.row(types.InlineKeyboardButton(text="Підтримка", url='t.me/MeestSupport_bot'))
        await message.answer("Зателефонуйте за номерами нашої лінії підтримки поштомтів:\n"
                                  "+380673735753\n"
                                  "+380503735753\n"
                                  "Або зверніться до наших операторів у чаті 👇", parse_mode=types.ParseMode.HTML,
                                  reply_markup=keyboard)
    else:
        await message.answer("Нажаль я не зрозумів питання, та я швидко навчаюсь, "
                             "та зможу відпосвісти Вам у нашу наступну зустріч")

        # await message.answer(message.text)

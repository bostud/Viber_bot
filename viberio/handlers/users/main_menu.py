from aiogram.types import CallbackQuery
from keyboards.inline.lang_choose import lang_choose_kb
from loader import dp


@dp.callback_query_handler(text="Меню вибора мови")
async def ukr(call: CallbackQuery):
    await call.message.edit_text("Оберіть будь ласка мову для спілкування👇")
    await call.message.edit_reply_markup(reply_markup=lang_choose_kb)

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from keyboards.default import menu_uk_kb_show
from loader import dp, bot


@dp.callback_query_handler(text="Cancel3", state="*")
async def cancel(call: CallbackQuery, state: FSMContext):
    # await call.message.delete_reply_markup()
    await call.message.delete()
    await bot.send_message(chat_id=call.from_user.id, text="Ви повернулись до головного меню",
                           reply_markup=menu_uk_kb_show)
    # await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.from_user.id)
    await state.finish()


@dp.callback_query_handler(text="die", state="*")
async def cancel(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.finish()

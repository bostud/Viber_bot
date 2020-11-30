from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram import types
from aiogram.utils.markdown import hlink
from loader import dp


@dp.message_handler(Command("clear"), state="*")
async def debug_clear_state(message: types.Message, state: FSMContext):
    await message.answer(
        f"😉 Просимо зробити скрін та сповістити про цей інцедент розробника:👉{hlink('Баги боту Поштоматик', '@t.me/PoshtomatikBugs')}",
        parse_mode=types.ParseMode.HTML)
    await state.finish()



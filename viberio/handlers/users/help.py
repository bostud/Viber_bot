from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.builtin import CommandHelp

from loader import dp, db
from utils.misc import rate_limit

@rate_limit(5, 'help')
@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    text = [
        'Список команд: ',
        '/start - Почати діалог',
        '/help -  Отримати довідку',
        # '/clear - Застрягли в меню - це допоможе',
        # '/count - Кількість користувачів сервісу',

    ]
    await message.answer('\n'.join(text))


@dp.message_handler(Command("stat_info"))
async def bot_help(message: types.Message):
    parcels_created = await db.get_parcels_created()
    parcels_sent = await db.get_parcels_sent()
    parcels_received = await db.get_parcels_received()
    door_not_opened = await db.get_door_not_opened()
    await message.answer(f"<b>Відправлено:</b> {parcels_sent}\n"
                         f"<b>Отримано:</b> {parcels_received}\n"
                         f"<b>Створено:</b> {parcels_created}\n"
                         f"<b>Отримано(Повторне відкриття комірки):</b> {door_not_opened} \n"
                         f"<b>Всього:</b> {parcels_sent + parcels_received}")
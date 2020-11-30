import asyncio
import logging

import asyncpg
from aiohttp import web
from viberio.api.client import ViberBot
from viberio.db_api.postgresql import Database
from viberio.dispatcher.dispatcher import Dispatcher
from viberio.dispatcher.webhook import ViberWebhookView
from viberio.keyboards.default import menu_kb, my_parcels_kb, poshtomat_search_kb
from viberio.keyboards.default.parcel_create import create_parcel_kb
from viberio.keyboards.default.send_phone import send_phone_kb
from viberio.types import requests
from viberio.types.configuration import BotConfiguration
from viberio.types.messages.text_message import TextMessage
from viberio.types.requests import ViberMessageRequest, ViberConversationStartedRequest, ViberUnsubscribedRequest, \
    ViberSubscribedRequest
from viberio.data import config
import re

API_TOKEN = config.BOT_TOKEN
WEBHOOK_URL = config.NGROK

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    # level=logging.INFO,
                    level=logging.DEBUG,
                    )
loop = asyncio.get_event_loop()
app = web.Application()
bot_config = BotConfiguration(auth_token=API_TOKEN, name='Poshtomat bot')
viber = ViberBot(bot_config)
dp = Dispatcher(viber)
db = Database(loop=dp.loop)
# dp = Dispatcher(bot, storage=storage)
ViberWebhookView.bind(dp, app, '/')


@dp.request_handler()
async def webhook(request: ViberMessageRequest, data: dict):
    print('Viber request', request)
    return True


@dp.subscribed_handler()
async def subscribed(request: ViberSubscribedRequest, data: dict):
    return await viber.send_message(request.user.id, TextMessage(text='Thanks for subscription!'))
    # return True


@dp.text_messages_handler(lambda msg: msg.message.text == 'main_menu')
async def menu(request: requests.ViberMessageRequest, data: dict):
    return await viber.send_messages(request.sender.id,
                                     TextMessage(text="Оберіть дію з головного меню", keyboard=menu_kb))


@dp.contact_messages_handler()
async def menu(request: requests.ViberMessageRequest, data: dict):
    print(data)
    await viber.send_messages(request.sender.id,
                              TextMessage(text="Благодарю, я получил Ваш контакт", keyboard=menu_kb,
                                          tracking_data=f"{data}"))
    return True


@dp.text_messages_handler(lambda msg: msg.message.text == 'my_parcels')
async def menu(request: requests.ViberMessageRequest, data: dict):
    print(f"LALALALALLALA{data}")

    return await viber.send_messages(request.sender.id,
                                     TextMessage(
                                         text=f"{request.sender.name}, отримайте інформацію по Відправленням які "
                                              f"прямують до Вас чи від Вас. "
                                              f"Ви можете оплатити, відслідкувати чи отримати підтримку від наших операторів.",
                                         keyboard=my_parcels_kb))


# regexp="^\d{4}$", state=MenuPoshtomat.P1_1
# lambda msg: msg.message.text == '4966'
# lambda query: re.match(r"in", query.data)


# @dp.text_messages_handler(lambda msg: re.match(r"^\d{4}$", msg.message.text))
# async def poshtomat_search(request: requests.ViberMessageRequest, data: dict):
#     # a = await viber.get_user_details(request.sender.id)
#     # print(a)
#     poshtomat_num = request.message.text
#     data = request.data
#     print(data)
#     result = "\n".join(branch_search(poshtomat_num))
#     # res = branch_search("4966")
#     return await viber.send_messages(request.sender.id,
#                                      TextMessage(
#                                          text=result,
#                                          keyboard=my_parcels_kb))


@dp.text_messages_handler(lambda msg: msg.message.text == 'poshtomat_search')
async def menu(request: requests.ViberMessageRequest, data: dict):
    return await viber.send_messages(request.sender.id,
                                     TextMessage(
                                         text="Оберіть, будь ласка, спосіб пошуку поштоматів Meest",
                                         keyboard=poshtomat_search_kb))


@dp.text_messages_handler(lambda msg: msg.message.text == 'help')
async def menu(request: requests.ViberMessageRequest, data: dict):
    return await viber.send_messages(request.sender.id,
                                     TextMessage(
                                         text="Зверніться до наших операторів в чат, або зателефонуйте за номерами "
                                              "нашої лінії підтримки поштоматів:\n"
                                              "+380673735753\n"
                                              "+380503735753\n"
                                              "Графік роботи: 8-22 Пн-Нд",
                                         keyboard=menu_kb))


# @dp.text_messages_handler(lambda msg: msg.message.text == 'help')
# async def menu(request: requests.ViberMessageRequest, data: dict):
#     return await viber.send_messages(request.sender.id,
#                                      TextMessage(
#                                          text="Зверніться до наших операторів в чат, або зателефонуйте за номерами нашої лінії підтримки поштоматів:\n"
#                                               "+380673735753\n"
#                                               "+380503735753\n"
#                                               "Графік роботи: 8-22 Пн-Нд",
#                                          keyboard=menu_kb))


@dp.subscribed_handler()
async def subscribed(request: requests.ViberSubscribedRequest, data: dict):
    return await viber.send_messages(request.user.id,
                                     TextMessage(
                                         text=f"{request.user.name}, Дякуємо Вам за підписку, залишайтеся з нами та отримуйте повну\n"
                                              f"про Ваші відправлення"))


@dp.text_messages_handler(lambda msg: msg.message.text == 'create_parcel')
async def menu(request: requests.ViberMessageRequest, data: dict):
    return await viber.send_messages(request.sender.id,
                                     TextMessage(
                                         text="Для створення посилки Вам потрібно вказати формат вантажу, поштомат для відправлення та поштомат отримання,ім'я отримувача і телефон.",
                                         keyboard=create_parcel_kb))


@dp.conversation_started_handler()
async def start(request: ViberConversationStartedRequest, data: dict):
    id = request.user.id
    name = request.user.name
    country = request.user.country
    language = request.user.language
    api_version = request.user.api_version
    akk = request.data
    print(akk)
    try:
        await db.add_viber_user(id, name, country, language, api_version)
    except asyncpg.UniqueViolationError:
        pass
    await viber.send_message(request.user.id,
                             TextMessage(
                                 text=f'{request.user.name}, для початку роботи з сервісом поділіться своїм номером '
                                      f'телефону',
                                 keyboard=send_phone_kb))
    return True


@dp.subscribed_handler()
async def subscribed(request: ViberSubscribedRequest, data: dict):
    await viber.send_message(request.user.id, TextMessage(text='Thanks for subscription!'))
    return True


@dp.unsubscribed_handler()
async def unsubscribed(request: ViberUnsubscribedRequest, data: dict):
    await viber.send_message(request.user_id, TextMessage(text='Bye!'))
    return True


async def set_webhook():
    await asyncio.sleep(1)
    result = await viber.set_webhook(WEBHOOK_URL)


async def on_shutdown(application: web.Application):
    # await viber.unset_webhook()
    await viber.close()


if __name__ == '__main__':
    app.on_shutdown.append(on_shutdown)
    loop.create_task(set_webhook())
    web.run_app(app, host='0.0.0.0', port=8443)

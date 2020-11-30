# from aiogram import types
#
# from aiogram.types import LabeledPrice
#
# from utils.misc.item import Item
#
# Tesla_S = Item(
#     title="Tesla Model S",
#     description="Tesla начала поставки с 1000 седанов ограниченного выпуска Signature и Signature Performance,"
#                 " оснащённых аккумуляторами ёмкостью 85 кВт·ч и стоимостью 95 400 и 105 400 долларов соответственно.",
#     currency="UAH",
#     prices=[
#         LabeledPrice(
#             label="TESLA M S",
#             amount=1_00
#         )
#     ],
#     start_parameter="create_invoice_tesla_model_s",
#     photo_url="https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.drive.ru%2Fnews%2Ftesla%2F5cc163f9ec05c4e82900001c.html&psig=AOvVaw0zzyBPtWJ-qAuX5VXt4YUl&ust=1601500149935000&source=images&cd=vfe&ved=0CAIQjRxqFwoTCNj6l46jj-wCFQAAAAAdAAAAABAJ",
#     photo_height=400
#
# )
#
# Tesla_X = Item(
#     title="Tesla Model X",
#     description="Tesla начала поставки с 1000 седанов ограниченного выпуска Signature и Signature Performance,"
#                 " оснащённых аккумуляторами ёмкостью 85 кВт·ч и стоимостью 95 400 и 105 400 долларов соответственно.",
#     currency="RUB",
#     prices=[
#         LabeledPrice(
#             label="TESLA M S",
#             amount=15_000_00
#         ),
#         LabeledPrice(
#             label="Скидка",
#             amount=2_000_00
#         ),
#         LabeledPrice(
#             label="НДС",
#             amount=10_000_00
#         ),
#     ],
#     start_parameter="create_invoice_tesla_model_s",
#     photo_url="https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.drive.ru%2Fnews%2Ftesla%2F560b992c95a65666b1000016.html&psig=AOvVaw0in6yhovAE96XFWRg2lKff&ust=1601500363329000&source=images&cd=vfe&ved=0CAIQjRxqFwoTCLi2mPOjj-wCFQAAAAAdAAAAABAJ",
#     photo_height=400,
#     need_shipping_address=True,
#     is_flexible=True,
# )
# POST_REGULAR_SHOPPING = types.ShippingOption(
#     id="rest_reg",
#     title="Почтомат",
#     prices=[
#         types.LabeledPrice(
#             "Обычная коробка", 0
#         ),
#         types.LabeledPrice(
#             "Почтомат", 2500
#         ),
#     ]
# )
# POST_FAST_SHIPING = types.ShippingOption(
#     id="post_fast",
#     title="Почтомат",
#     prices=[
#         types.LabeledPrice(
#             "Обычная коробка", 0
#         ),
#         types.LabeledPrice(
#             "Почтомат", 2500
#         ),
#     ]
# )
#
# PICKUP_SHIPING = types.ShippingOption(
#     id="pick_up",
#     title="Почтомат",
#     prices=[
#         types.LabeledPrice(
#             "Обычная коробка", 0
#         ),
#         types.LabeledPrice(
#             "Почтомат", 2500
#         ),
#     ]
# )
#

import re


def aa(amm):
    if re.match(r'1[1-9]\d[0-9]{4}', amm):
        print("Подходит")
    else:
        print("Не подходит")
# aa("12345)

import os
from dotenv import load_dotenv

load_dotenv()

# токен бота
BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
NGROK = os.getenv("NGROK")

PROVIDER_TOKEN = os.getenv("PROVIDER_TOKEN")

# токен API_MEEST для CHATBOT
CHAT_BOT_TOKEN = os.getenv("API_CHATBOT_TOKEN")

# база данных
PGUSER = str(os.getenv("PGUSER"))
PGPASSWORD = str(os.getenv("PGPASSWORD"))
DATABASE = str(os.getenv("DATABASE"))
ip = os.getenv("ip")
POSTGRES_URL = f"postgresql://{PGUSER}:{PGPASSWORD}@{ip}/{DATABASE}"

# Оплата портмоне
PAYMENT_SYSTEM_ID = os.getenv("PAYMENT_SYSTEM_ID_PORTMONE_IN_1C")
# 1C_AUTH_API
LOGIN_1C = os.getenv("LOGIN_1C")
PASSWORD_1C = os.getenv("PASSWORD_1C")

# админы бота
admins = [
    485626761,
    # 821419257
]

aiogram_redis = {
    'host': ip,
}

redis = {
    'address': (ip, 6379),
    'encoding': 'utf8'
}

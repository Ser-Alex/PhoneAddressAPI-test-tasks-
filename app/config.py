import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env (если он существует)
load_dotenv()

# Общие настройки
ENV = os.getenv('ENV')

# Настройки для Redis
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')

import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env (если он существует)
load_dotenv()

# Общие настройки
ENV = os.getenv('ENV')

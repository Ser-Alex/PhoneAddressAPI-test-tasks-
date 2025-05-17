FROM python:3.11-slim

WORKDIR /app

# Обновляем pip до нужной версии для стабильной работы
RUN pip install --upgrade pip==25.0.1

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

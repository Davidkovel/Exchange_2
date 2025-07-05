FROM python:3.11-slim

WORKDIR /app

# Сначала копируем только requirements.txt для кэширования
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем всю структуру проекта
COPY . .

# Запускаем приложение из правильного модуля
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]



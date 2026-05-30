FROM python:3.12-slim

WORKDIR /app

# Копируем файл зависимостей (хорошая практика)
# Если у вас нет requirements.txt, можно оставить просто COPY
COPY api/ /app/

# Устанавливаем библиотеки
RUN pip install --no-cache-dir fastapi uvicorn psutil

# КОРРЕКТИРОВКА КОМАНДЫ:
# 1. Файл называется app.py, поэтому пишем app:app (а не main:app)
# 2. Хост ОБЯЗАТЕЛЬНО 0.0.0.0 внутри Docker
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

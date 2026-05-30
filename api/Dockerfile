FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Важно: внутри докера используем 0.0.0.0
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

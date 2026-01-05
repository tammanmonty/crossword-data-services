FROM python:3.10-slim
LABEL authors="TammanM"


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


WORKDIR /data_pipeline

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY /data_pipeline /app

CMD ["python", "-m", "app.main"]

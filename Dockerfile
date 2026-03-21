FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    OPEN_BROWSER=0 \
    BACKEND_HOST=0.0.0.0 \
    FRONTEND_HOST=0.0.0.0

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 8000 8501

CMD ["python", "run_do_an.py"]

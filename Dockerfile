FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /app/ecommerce

RUN python manage.py collectstatic --noinput || true

CMD ["gunicorn", "ecommerce.wsgi:application", "--bind", "0.0.0.0:8000"]
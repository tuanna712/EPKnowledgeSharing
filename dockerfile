FROM python:3.10-bookworm

ENV PYTHONBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

# CMD gunicorn EPDB.wsgi:application --bind 0.0.0.0:8000
CMD python manage.py runserver 0.0.0.0:8000

EXPOSE 8000


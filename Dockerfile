FROM python:3.6.2 AS goat

RUN apt-get update && pip install django && mkdir /goat

WORKDIR /goat

EXPOSE 8000

ENTRYPOINT python manage.py runserver 0.0.0.0:8000



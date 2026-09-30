#!/bin/sh -ex

python manage.py migrate
exec gunicorn config.wsgi:application -k gthread -w 2 --threads 2 -b 0.0.0.0:8000

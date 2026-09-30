#!/bin/sh -ex

python manage.py migrate
exec gunicorn config.wsgi:application -w 4 -b 0.0.0.0:8000

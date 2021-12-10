FROM python:3.9.7-slim

# set work directory
WORKDIR /usr/src/app

# set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update &&  apt-get install nginx \
    supervisor build-essential  gcc libc-dev gettext \
    libffi-dev libpq-dev -y

# install dependencies
RUN pip install --upgrade pip
RUN pip install gunicorn

COPY . /usr/src/app/

RUN if [ ! -f requirements.txt ]; then echo requirements.txt does not exist >&2; exit 1; fi;
RUN pip install -r requirements.txt

RUN python manage.py collectstatic --noinput

COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
CMD ["sh", "/usr/src/app/run.sh"]
FROM python:3.10.4-slim

ENV PYTHONDONTWRITEBYTECODE = 1
ENV PYTHONUNBUFFERED = 1

RUN apt-get update && apt-get install --fix-broken\
    && apt-get install -y build-essential libssl-dev\
    libffi-dev libpq-dev python-dev gcc gettext

RUN mkdir /usr/src/app
ENV HOME=/usr/src/app
RUN mkdir $HOME/staticfiles
RUN mkdir $HOME/media
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip install -U pip && pip install -r requirements.txt

COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY . .

ENTRYPOINT ["sh", "/usr/src/app/entrypoint.sh"]
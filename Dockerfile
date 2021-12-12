FROM python:3.9.7-alpine

ENV PYTHONDONTWRITEBYTECODE = 1
ENV PYTHONUNBUFFERED = 1

RUN mkdir /usr/src/app
ENV HOME=/usr/src/app
RUN mkdir $HOME/staticfiles
RUN mkdir $HOME/media
WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app

RUN apk update \
    && apk add postgresql-dev gcc python3-dev \ 
    musl-dev make supervisor gettext jpeg-dev \
    libffi-dev build-base zlib-dev linux-headers

COPY . .

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
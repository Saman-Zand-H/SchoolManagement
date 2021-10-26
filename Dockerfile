FROM python:3.9.7-alpine

ENV PYTHONDONTWRITEBYTECODE = 1
ENV PYTHONUNBUFFERED = 1

WORKDIR /usr/src/app

RUN apk update \
    && apk add build-base postgresql-dev alpine-sdk gcc python3-dev musl-dev jpeg-dev zlib-dev libffi-dev

RUN pip install -U pip
RUN pip install -U setuptools
COPY requirements.txt /usr/src/app
RUN pip install -r requirements.txt

COPY . /usr/src/app
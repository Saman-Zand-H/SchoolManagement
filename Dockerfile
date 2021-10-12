FROM python:latest

ENV PYTHONDONTWRITEBYTECODE = 1
ENV PYTHONUNBUFFERED = 1

WORKDIR /Sample-Projects/

COPY requirements.txt /Sample-Projects/

RUN pip install -r requirements.txt

COPY . /Sample-Projects/
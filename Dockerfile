FROM python:3.9.7-alpine

ENV PYTHONDONTWRITEBYTECODE = 1
ENV PYTHONUNBUFFERED = 1

RUN mkdir /usr/src/app
ENV HOME=/usr/src/app
RUN mkdir $HOME/staticfiles
RUN mkdir $HOME/media
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app
RUN apk add --no-cache --virtual .build-deps \
    build-base ca-certificates gcc postgresql-dev linux-headers musl-dev \
    libffi-dev jpeg-dev zlib-dev \
    && pip install -r requirements.txt \
    && find /usr/local \
    \( -type d -a -name test -o -name tests \) \
    -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
    -exec rm -rf '{}' + \
    && runDeps="$( \
    scanelf --needed --nobanner --recursive /usr/local \
    | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
    | sort -u \
    | xargs -r apk info --installed \
    | sort -u \
    )" \
    && apk add --virtual .rundeps $runDeps \
    && apk del .build-deps

COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

COPY . .

#ENTRYPOINT ["/usr/src/app/entrypoint.sh"]

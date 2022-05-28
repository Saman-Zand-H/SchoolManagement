#!/bin/bash

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput 
python manage.py compilemessages
python manage.py algolia_applysettings
python manage.py algolia_reindex
daphne -b 0.0.0.0 -p 8000 conf.asgi:application
celery -A conf worker -l info

exec "$@"

MANAGE_FILE=/usr/src/app/manage.py
if test -f "$MANAGE_FILE"; then
    python manage.py migrate --noinput
fi

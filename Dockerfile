FROM python:3.10.4-slim

ENV PYTHONDONTWRITEBYTECODE = 1
ENV PYTHONUNBUFFERED = 1

# Install necessary dependencies
RUN apt-get update && apt-get install --fix-broken -y\
    build-essential libssl-dev xvfb curl wget nginx supervisor\
    libffi-dev libpq-dev python-dev gcc gettext unzip \
    daemonize dbus-user-session fontconfig

# Adding trusting keys to apt for repositories
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

# Adding Google Chrome to the repositories
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

# Updating apt to see and install Google Chrome
RUN apt-get -y update

# Magic happens
RUN apt-get install -y google-chrome-stable

# Download the Chrome Driver
ENV CHROMEDRIVER_LATEST_RELEASE 1
RUN wget -O /tmp/chromedriver.zip \
    http://chromedriver.storage.googleapis.com/`\
    curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip

# Unzip the Chrome Driver into /usr/local/bin directory
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# Set display port as an environment variable
ENV DISPLAY=:99

RUN mkdir /usr/src/app
ENV HOME=/usr/src/app
RUN mkdir $HOME/staticfiles
RUN mkdir $HOME/media
RUN mkdir /run/daphne
RUN mkdir $HOME/logs
RUN mkdir $HOME/logs/app
RUN mkdir $HOME/logs/asgi
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip install -U pip && pip install -r requirements.txt

COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

COPY celery_conf/celeryd /etc/default/celeryd
COPY celery_conf/celeryd.init /etc/init.d/celeryd
RUN chmod 777 /etc/init.d/celeryd

COPY . .

ENTRYPOINT ["sh", "/usr/src/app/entrypoint.sh"]
FROM python:3.8-slim-buster

ENV PYTHONUNBUFFERED 1

RUN apt-get update -qq && apt-get install -y -qq \
    # std libs
    unzip wget sudo less nano curl git gosu build-essential software-properties-common \
    # python basic libs
    gettext \
    # geodjango
    gdal-bin binutils libproj-dev libgdal-dev \
    # postgresql
    libpq-dev postgresql-client && \
    apt-get clean all && rm -rf /var/apt/lists/* && rm -rf /var/cache/apt/*

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements
RUN pip install -r /requirements/local.txt

COPY ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r//' /entrypoint
RUN chmod +x /entrypoint

COPY ./compose/local/django/start /start
RUN sed -i 's/\r//' /start
RUN chmod +x /start

WORKDIR /app

ENTRYPOINT ["/entrypoint"]

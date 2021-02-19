FROM python:3.8-slim-buster AS base

LABEL maintainer="Ethan Andrews <eandrews@whoi.edu>"

ENV PYTHONUNBUFFERED 1

RUN apt-get update -qq && apt-get install -y -qq \
    unzip wget sudo less nano curl git gosu build-essential software-properties-common \
    # python basic libs
    gettext \
    # postgresql
    libpq-dev postgresql-client && \
    apt-get clean all && rm -rf /var/apt/lists/* && rm -rf /var/cache/apt/*

# Requirements are installed here to ensure they will be cached.
COPY ./habhub-dataserver/requirements /requirements
RUN pip install --prefix=/install -r /requirements/production.txt \
    && rm -rf /requirements

# Build optimized image
FROM python:3.8-slim-buster AS build-image

ENV PYTHONUNBUFFERED 1

RUN apt-get update -qq && apt-get install -y -qq \
    # python basic libs
    gettext \
    # geodjango
    gdal-bin binutils libproj-dev libgdal-dev \
    # postgresql
    libpq-dev postgresql-client && \
    apt-get clean all && rm -rf /var/apt/lists/* && rm -rf /var/cache/apt/*

COPY --from=base /install /usr/local

RUN groupadd -r django \
    && useradd --no-log-init -r -g django django

COPY ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r//' /entrypoint
RUN chmod +x /entrypoint && chown django /entrypoint

COPY ./compose/production/django/start /start
RUN sed -i 's/\r//' /start
RUN chmod +x /start && chown django /start

COPY ./compose/production/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r//' /start-celeryworker
RUN chmod +x /start-celeryworker && chown django /start-celeryworker

COPY ./compose/production/django/celery/beat/start /start-celerybeat
RUN sed -i 's/\r//' /start-celerybeat
RUN chmod +x /start-celerybeat && chown django /start-celerybeat

COPY ./compose/production/django/celery/flower/start /start-flower
RUN sed -i 's/\r//' /start-flower
RUN chmod +x /start-flower && chown django /start-flower

COPY ./habhub-dataserver /app
WORKDIR /app

RUN chown -R django /app

USER django

ENTRYPOINT ["/entrypoint"]

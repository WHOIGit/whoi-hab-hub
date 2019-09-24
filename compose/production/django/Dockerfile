FROM python:3.7-slim-buster

ENV PYTHONUNBUFFERED 1

RUN apt-get update \
  # psycopg2 dependencies
  && apt-get -y install gcc g++ python3-dev python3-setuptools musl-dev \
  # Pillow dependencies
  libtiff5-dev libjpeg62-turbo-dev libopenjp2-7-dev zlib1g-dev \
  libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev \
  python3-tk \
  # CFFI dependencies
  libffi-dev \
  # Translations dependencies
  gettext \
  # geodjango
  gdal-bin binutils libproj-dev libgdal-dev \
  # https://docs.djangoproject.com/en/dev/ref/django-admin/#dbshell
  postgresql-client

RUN groupadd django \
    && useradd -r -s /bin/bash -g django -G sudo django

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements
RUN pip install --no-cache-dir -r /requirements/production.txt \
    && rm -rf /requirements

COPY ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r//' /entrypoint
RUN chmod +x /entrypoint
RUN chown django /entrypoint

COPY ./compose/production/django/start /start
RUN sed -i 's/\r//' /start
RUN chmod +x /start
RUN chown django /start

COPY . /app

RUN mkdir /app/staticfiles && mkdir /app/media

RUN chown -R django:django /app

USER django

WORKDIR /app

ENTRYPOINT ["/entrypoint"]

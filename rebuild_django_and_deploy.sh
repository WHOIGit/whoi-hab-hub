#!/bin/bash
# Script to rebuild all Django containers and run migrate/collectstatic to deploy
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

if [ -e production.yml ]
then
    docker-compose -f production.yml up -d --no-deps --build django
    docker-compose -f production.yml run --rm django python manage.py migrate
    docker-compose -f production.yml run --rm django python manage.py collectstatic --noinput
    docker-compose -f production.yml up -d --no-deps --build celeryworker
    docker-compose -f production.yml up -d --no-deps --build celerybeat
    docker-compose -f production.yml up -d --no-deps --build flower
fi

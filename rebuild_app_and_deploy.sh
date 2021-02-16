#!/bin/bash
# Script to rebuild all Django containers and run migrate/collectstatic to deploy
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

if [ -e production.yml ]
then
    docker-compose -f docker-compose-prod.yml up -d --no-deps --build django
    docker-compose -f docker-compose-prod.yml up -d --no-deps --build react_frontend
    docker-compose -f docker-compose-prod.yml run --rm django python manage.py migrate
    docker-compose -f docker-compose-prod.yml run --rm django python manage.py collectstatic --noinput
    docker-compose -f docker-compose-prod.yml up -d --no-deps --build celeryworker
    docker-compose -f docker-compose-prod.yml up -d --no-deps --build celerybeat
    docker-compose -f docker-compose-prod.yml up -d --no-deps --build flower
fi

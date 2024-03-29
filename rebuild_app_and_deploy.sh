#!/bin/bash
# Script to rebuild all Django containers and run migrate/collectstatic to deploy
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

if [ -e docker-compose-prod.yml ]
then
    docker-compose -f docker-compose-prod.yml pull
    docker-compose -f docker-compose-prod.yml up -d --no-deps django
    docker-compose -f docker-compose-prod.yml run --rm django python manage.py migrate
    docker-compose -f docker-compose-prod.yml run --rm django python manage.py collectstatic --noinput
    docker-compose -f docker-compose-prod.yml up -d --no-deps celeryworker
    docker-compose -f docker-compose-prod.yml up -d --no-deps celerybeat
    docker-compose -f docker-compose-prod.yml up -d --no-deps flower
    docker-compose -f docker-compose-prod.yml up -d --no-deps react_frontend
fi

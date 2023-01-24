#!/bin/sh
docker buildx build -f compose/production/django/Dockerfile -t ghcr.io/whoigit/habhub-dataserver:stable --platform linux/amd64 --push .

docker buildx build -f compose/production/react-frontend/Dockerfile -t ghcr.io/whoigit/habhub-react-frontend:stable --platform linux/amd64 --push .
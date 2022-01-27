#!/bin/bash
docker build -t ghcr.io/whoigit/habhub-react-frontend:stable -f compose/production/react-frontend/Dockerfile .
docker push ghcr.io/whoigit/habhub-react-frontend:stable

docker build -t ghcr.io/whoigit/habhub-dataserver:stable -f compose/production/django/Dockerfile .
docker push ghcr.io/whoigit/habhub-dataserver:stable
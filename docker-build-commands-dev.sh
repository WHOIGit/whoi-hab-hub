#!/bin/bash
docker build -t ghcr.io/whoigit/habhub-react-frontend:develop-maplibre -f compose/production/react-frontend/Dockerfile .
docker push ghcr.io/whoigit/habhub-react-frontend:develop-maplibre

docker build -t ghcr.io/whoigit/habhub-dataserver:develop -f compose/production/django/Dockerfile .
docker push ghcr.io/whoigit/habhub-dataserver:develop
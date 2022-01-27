#!/bin/bash
docker build -t ghcr.io/whoigit/habhub-react-frontend:develop -f compose/production/react-frontend/Dockerfile .
docker push ghcr.io/whoigit/habhub-react-frontend:develop

docker build -t ghcr.io/whoigit/habhub-dataserver:develop -f compose/production/django/Dockerfile .
docker push ghcr.io/whoigit/habhub-dataserver:develop
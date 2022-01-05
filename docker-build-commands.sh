#!/bin/bash
docker build -t ghcr.io/whoigit/habhub-react-frontend:stable -f compose/production/react-frontend/Dockerfile .
docker push ghcr.io/whoigit/habhub-react-frontend:stable
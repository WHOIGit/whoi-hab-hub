#FROM postgis/postgis:12-3.1-alpine
FROM ghcr.io/baosystems/postgis:18-3.6


LABEL maintainer="Ethan Andrews <eandrews@whoi.edu>"

# install Debian security updates for packages in the base image (e.g. libbrotli1)
RUN apt-get update -qq && apt-get upgrade -y -qq && \
    apt-get clean all && rm -rf /var/lib/apt/lists/*

COPY ./compose/production/postgres/maintenance /usr/local/bin/maintenance
RUN chmod +x /usr/local/bin/maintenance/*
RUN mv /usr/local/bin/maintenance/* /usr/local/bin \
    && rmdir /usr/local/bin/maintenance

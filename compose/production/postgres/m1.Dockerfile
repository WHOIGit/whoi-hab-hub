FROM gangstead/postgis:13-3.1-arm

LABEL maintainer="Ethan Andrews <eandrews@whoi.edu>"

COPY ./compose/production/postgres/maintenance /usr/local/bin/maintenance
RUN chmod +x /usr/local/bin/maintenance/*
RUN mv /usr/local/bin/maintenance/* /usr/local/bin \
    && rmdir /usr/local/bin/maintenance

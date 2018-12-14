FROM nginx:1.15

RUN mv /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/z-default.conf

COPY ./compose/production/nginx/starterkit.conf /etc/nginx/conf.d/starterkit.conf

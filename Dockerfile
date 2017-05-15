FROM jfloff/alpine-python
MAINTAINER Taylor Owen (as0bu)

COPY . /app

RUN pip install --timeout 60 -r /app/requirements.txt && \
    python /app/manage.py migrate && \
    apk add --update nginx supervisor && \
    rm /etc/nginx/conf.d/default.conf && \
    ln -s /app/nginx_conf/yeastbot.conf /etc/nginx/conf.d/ && \
    ln -sf /app/nginx_conf/nginx.conf /etc/nginx/nginx.conf

EXPOSE 8000
CMD [ "/usr/bin/supervisord", "-c", "/app/supervisord.ini" ]

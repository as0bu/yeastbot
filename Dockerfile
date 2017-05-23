FROM jfloff/alpine-python
MAINTAINER Taylor Owen (as0bu)

COPY . /app

RUN pip install --timeout 60 -r /app/requirements.txt && \
    python /app/manage.py migrate && \
    apk add --update nginx && \
    rm -rf /var/cache/apk/* && \
    rm /etc/nginx/conf.d/default.conf && \
    ln -s /app/config_files/nginx_conf/yeastbot.conf /etc/nginx/conf.d/ && \
    ln -sf /app/config_files/nginx_conf/nginx.conf /etc/nginx/nginx.conf

EXPOSE 8000
CMD [ "/usr/bin/uwsgi", "--ini", "/app/config_files/uwsgi.ini" ]

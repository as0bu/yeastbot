FROM jfloff/alpine-python
MAINTAINER Taylor Owen (as0bu)

RUN pip install django \
    && pip install django-bootstrap3 \
    && pip install beautifulsoup4 \
    && pip install requests

COPY . /app
EXPOSE 8000

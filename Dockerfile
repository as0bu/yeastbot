FROM jfloff/alpine-python
MAINTAINER Taylor Owen (as0bu)

COPY . /app

RUN pip install -r /app/requirements.txt && \
    python /app/manage.py migrate

EXPOSE 8000


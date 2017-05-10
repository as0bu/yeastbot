FROM jfloff/alpine-python
MAINTAINER Taylor Owen (as0bu)

RUN pip install django \
    && pip install beautifulsoup4 \
    && pip install requests \
    && pip install pdfminer.six

COPY . /app
EXPOSE 8000

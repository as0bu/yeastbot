#!/bin/bash

uwsgi --http :8001 --chdir /app --module yeastbot.wsgi &
nginx

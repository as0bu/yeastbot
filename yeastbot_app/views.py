from django.shortcuts import render, HttpResponse, loader
import os
import csv
import json
import code
import pprint

# Create your views here.

def index(request):
    return HttpResponse('Hello World!')


def test(request):
    return HttpResponse('This is a test')


def yeastbot(request):
    app_dir = os.path.dirname(__file__)
    db_path = os.path.join(app_dir, './data/yeastbot_db.csv')
    data = []
    with open(db_path, 'r') as db_csv:
        reader = csv.DictReader(db_csv)
        for row in reader:
            data.append(row)
    #code.interact(local=locals())
    template = loader.get_template('yeastbot.html')
    return HttpResponse(template.render({'data': data}, request))

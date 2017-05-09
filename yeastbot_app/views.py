from django.shortcuts import render, HttpResponse, loader
from yeastbot_app.code.parse_labs import parse_labs
import os
import json
import code
import pprint

# Create your views here.

def yeastbot(request):
    app_dir = os.path.dirname(__file__)
    cache_path = os.path.join(app_dir, './data/cache.json')
    with open(cache_path, 'r') as cache:
        data = json.load(cache)
#    code.interact(local=locals())
    template = loader.get_template('yeastbot.html')
    return HttpResponse(template.render({'data': data}, request))

def yeastbot_cache(request):
    parse_labs()
    return HttpResponse('Caching is complete!')

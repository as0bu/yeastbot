from django.conf.urls import url
from yeastbot_app import views

urlpatterns = [
  url(r'^$', views.yeastbot, name='yeastbot'),
  url(r'^cache/$', views.yeastbot_cache, name='yeastbot_cache'),
]

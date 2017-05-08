from django.conf.urls import url
from yeastbot_app import views

urlpatterns = [
  url(r'^$', views.index, name='index'),
  url(r'^test/$', views.test, name='test'),
  url(r'^yeastbot/$', views.yeastbot, name='yeastbot'),
]

from django.conf.urls.defaults import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='themes_home'),
    url(r'^([\w\-_]+)/$', views.theme, name='themes_theme'),
)


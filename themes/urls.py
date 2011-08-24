from django.conf.urls.defaults import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='themes_home'),
    url(r'^([\w\-_]+)/$', views.theme, name='themes_theme'),
    url(r'^([\w\-_]+)/up-file/$', views.theme_up_file, name='themes_up_file'),
)


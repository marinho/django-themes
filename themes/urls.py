from django.conf.urls.defaults import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='themes_home'),
    url(r'^import/$', views.theme_import, name='themes_import'),
    url(r'^disable-preview/$', views.theme_preview, name='themes_disable_preview'),
    url(r'^([\w\-_]+)/$', views.theme, name='themes_theme'),
    url(r'^([\w\-_]+)/delete/$', views.theme_delete, name='themes_delete'),
    url(r'^([\w\-_]+)/set-default/$', views.theme_set_default, name='themes_set_default'),
    url(r'^([\w\-_]+)/preview/$', views.theme_preview, name='themes_preview'),
    url(r'^([\w\-_]+)/rename/$', views.theme_rename, name='themes_rename'),
    url(r'^([\w\-_]+)/up-file/$', views.theme_up_file, name='themes_up_file'),
    url(r'^([\w\-_]+)/edit-child/$', views.theme_edit_child, name='themes_edit_child'),
    url(r'^([\w\-_]+)/delete-child/$', views.theme_delete_child, name='themes_delete_child'),
    url(r'^([\w\-_]+)/create-template/$', views.theme_create_template, name='themes_create_template'),
    url(r'^([\w\-_]+)/create-static-file/$', views.theme_create_static_file, name='themes_create_static_file'),
    url(r'^([\w\-_]+)/download/$', views.theme_download, name='themes_download'),
)


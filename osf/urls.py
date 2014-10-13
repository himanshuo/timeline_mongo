__author__ = 'himanshu'
from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = patterns('osf.views',
    url(r'^create_new_project/$', 'create_new_project'),
    url(r'^project_detail/$', 'project_detail'),
    url(r'^update_project/$', 'update_project'),
    url(r'^delete_project/$', 'delete_project'),
    url(r'^delete_all_projects/$', 'delete_all_projects'),
)

urlpatterns = format_suffix_patterns(urlpatterns)
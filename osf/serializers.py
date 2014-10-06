"""
__author__ = 'himanshu'
from django.forms import widgets
from rest_framework import serializers
from osf.models import Timeline,History


class TimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timeline
        fields = ("id",'title', 'author', 'wiki',"project_id","current_version","date", "history" )




class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = ('title', 'author', 'wiki',"version","date" )


"""
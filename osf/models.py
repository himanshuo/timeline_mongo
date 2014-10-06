from django.db import models
from djangotoolbox.fields import ListField
from django_mongodb_engine.contrib import MongoDBManager


from djangotoolbox.fields import EmbeddedModelField


#Timeline( title='t1',author='a1' ,wiki='w1', project_id=1, current_version=1).save()
class Timeline(models.Model):

    title = models.CharField(max_length=256, blank=True,default='')
    author = models.CharField(max_length=256, blank=True, default='')
    wiki = models.TextField(default='')
    project_id = models.IntegerField(blank=False, null=False)
    #current_version = models.IntegerField()
    #date= models.DateTimeField(auto_now=True)
    date= models.DateTimeField()


    history = ListField(EmbeddedModelField('History'))
    objects = MongoDBManager()


class History(models.Model):
    title = models.CharField(max_length=256, blank=True,default='')
    author = models.CharField(max_length=256, blank=True, default='')
    wiki = models.TextField(default='')
    #version = models.IntegerField()
    #date = models.DateTimeField(auto_now_add=True)
    date = models.DateTimeField()
    class MongoMeta:
        ordering = ['date']


    #can use raw_update to create your specific updates in the future for when you add in a new timeline, and the current
    #needs to go into history


    #goal:create function so that you can access appropriate historical data.
    #IDEA was to create



    #ADD A TIMELINE
    """
Timeline( title='tc',author='ac' ,wiki='wc', project_id=1).save()
t = Timeline.objects.get(project_id=1)
t.history.append(History(title="t1", wiki="w1", author="a1", date=datetime.date(month=9, day=20,year=2014)))
t.history.append(History(title="t2", date=datetime.date(month=9, day=21,year=2014) ))
t.history.append(History(title="t3", author="a3", date=datetime.date(month=9, day=29,year=2014)))
t.history.append(History(wiki="w4",date=datetime.date(month=10, day=20,year=2014) ))
t.history.append(History(wiki="w5",date=datetime.date(month=10, day=25,year=2014)))
t.history.append(History(wiki="w6", date=datetime.date(month=10, day=26,year=2014)))
t.history.append(History(wiki="w7", author="a7", date=datetime.date(month=10, day=27,year=2014)))
t.history.append(History(title="t8", wiki="w8", author="a8", date=datetime.date(month=12, day=20,year=2014)))
t.history.append(History(wiki="w9", date=datetime.date(month=12, day=25,year=2014)))
t.save()


    """
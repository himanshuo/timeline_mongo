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


#BOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO!!!! this sucks. the latency between server and client too slow to allow for simple
# useful return data (increase max_project_id by 1).
#if you were to concurrently have multiple created project request, then you would have to put them in queue so that
#the next generated project_id doesnt clash with the next generated project_id of a different request.
#simple solution for current purposes is to just have client input what project id they want.

#this could be handled using Map/Reduce but thats unneccessrily slow.
## we could also index project_id and perhaps sort like that, but again, thats going to be a lot slower than just having
# a "database handler" collection whose entire purpose is to handle data about our Timeline and History collections.

#going to just be one instance. will store metadata about db. thus will allow constant time for attaining some data about
#collections
#class DatabaseHandler(models.Model):
#    max_project_id = models.IntegerField(default=0)#start with project_id=0
#    objects = MongoDBManager()


class History(models.Model):
    title = models.CharField(max_length=256, blank=True,default='')
    author = models.CharField(max_length=256, blank=True, default='')
    wiki = models.TextField(default='')
    #version = models.IntegerField()
    #date = models.DateTimeField(auto_now_add=True)
    date = models.DateTimeField()
    #class MongoMeta:
    #    ordering = ['-date']


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
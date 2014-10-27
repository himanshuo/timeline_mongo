

#from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
#from rest_framework.renderers import JSONRenderer
#from rest_framework.parsers import JSONParser
from osf.models import Timeline
#from osf.serializers import TimelineSerializer

#this is for the second part.
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny,IsAdminUser

from osf.models import Timeline,History
#this is for working with custom queries from django to postgres
from django.db import connection

#working with time
import datetime

#appropriate curl command is for POST
#curl --header "Content-Type: application/json" -d '{"title":"xyz","users":"xyzsdf", "wiki":"weeeee"}' http://127.0.0.1:8000/timeline/

import json

from django.db import connections
from pymongo import MongoClient


def proper_creation_request(data):
    if 'wiki' not in data or not data['wiki']:
        return False;
    if 'title' not in data or not data['title']:
        return False;
    if 'author' not in data or not data['author']:
        return False;
    if 'date' not in data or not data['author']:
        return False;
    return True



#{"wiki":"w1", "title":"t1", "author":"a1", "project_id": 3}
@csrf_exempt
@api_view(['POST'])
def create_new_project(request, format=None):
    print "new proj called"
    if request.method == 'POST':
        #print str(request.DATA)

        if 'project_id' not in request.DATA or not request.DATA['project_id']:
            print "pid not in request"
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if not proper_creation_request(request.DATA):
            print 'not proper request'
            return Response(status=status.HTTP_400_BAD_REQUEST)

        pid = int(request.DATA['project_id'])
        print pid,"is pid"

        #if project with given project id exists, then throw error.
        try:
            k = Timeline.objects.get(project_id=pid)

            #if previous line works then not good.
            return Response("project already exists.", status=status.HTTP_400_BAD_REQUEST)
        except:
            #if cant get object by given project id then you are good.
            pass


        post_date = request.DATA['date'].split("-")
        d = datetime.datetime(month=int(post_date[0]), day=int(post_date[1]),year=int(post_date[2])) # 09-20-2014

        t = Timeline(project_id=pid,
                 wiki=request.DATA['wiki'],
                 author=request.DATA['author'],
                 title=request.DATA['title'],
                 date=d)



        h = History(wiki=request.DATA['wiki'],
                 author=request.DATA['author'],
                 title=request.DATA['title'],
                 date=d)

        t.history.append(h)
        t.save()
        #print "new project succesfully created."





        out = {pid: "Project Created."}
        return Response( out, status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST)




@csrf_exempt
@api_view(['GET'])
def project_detail(request, format=None):
    print "get called"
    if request.method == "GET":
        if 'project_id' not in request.GET or not request.GET['project_id']:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if 'date' in request.GET and request.GET['date']:
            #print request.GET['project_id'], request.GET['date']
            url_date = request.GET['date'].split("-")
            d = datetime.datetime(month=int(url_date[0]), day=int(url_date[1]),year=int(url_date[2])) # 09-20-2014
#########################POTENTIALLY ADD day+1 HERE since you want to get data back from anytime on input date as well. THUS should start checking from one day after input day.
            try:
                t = Timeline.objects.get(project_id=int(request.GET['project_id']))

                #actual values of the historical object
                author = ""
                title=""
                wiki=""

                #have the values of the historical object been set?
                hasauthor=False
                hastitle=False
                haswiki=False


                #for i in t.history:
                #    print i.date

                #sort by date (note that date in this case is actually in ms so its all good :) )
                hist = sorted(t.history, key=lambda history: history.date, reverse=True)

                #for i in hist:
                #    print i.title, i.title=="", i.title==None, i.title is not None
                #for i in hist:
                #    print i.wiki
               # print "#################################################################"
                for h in hist:
                    #print h.date,d,'this is it'
                    #print "historical date:",h.date,"input date:", d

                    #print h.date,"should be less than", d
                    if h.date <= d:

                        if not hasauthor or not hastitle or not haswiki:
                            if not hasauthor and not is_empty(h.author):
                                author = h.author
                                #print "author:",author
                                hasauthor = True
                            if not hastitle and not is_empty(h.title):
                                title = h.title
                                #print "title:",title, "is_empty(h.title) returned true in this case"
                                hastitle = True
                            if not haswiki and not is_empty(h.wiki):
                                wiki = h.wiki
                                #print "wiki:",wiki
                                haswiki=True

                        else:
                            break
                #print title, author, wiki
                most_recent_hist = History(title=title, author=author, wiki=wiki)
                #print "#################################################################"

            except:
                return Response("failed to create proper historical object", status=status.HTTP_400_BAD_REQUEST)

            out  = {"project_id":int(request.GET['project_id']),
                             "title": title,
                             "author": author,
                             "wiki":wiki}
            return Response(out , status = status.HTTP_200_OK)
            #return Response("No results attained.",status=status.HTTP_204_NO_CONTENT)


        try:
            t = Timeline.objects.get(project_id= int(request.GET['project_id']) )



            out = {"project_id":int(t.project_id),
                             "title": t.title,
                             "author": t.author,
                             "wiki":t.wiki}

            return Response(out , status=status.HTTP_200_OK)
        except:
            return Response("No results attained.", status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_400_BAD_REQUEST)


def is_empty(x):
    if x is None:
        return True
    if x==None:
        return True
    if x=="":
        return True
    return False



@api_view(['POST'])
def update_project(request):
    if request.method=="POST":
        print '"update project called'
        #print str(request.DATA)
        if 'project_id' not in request.DATA or not request.DATA['project_id']:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if 'date' not in request.DATA or not request.DATA['date']: #written yyyy-dd-mm
            return Response("must add date for when this historical value was added", status=status.HTTP_400_BAD_REQUEST)
        try:

            url_date = request.DATA['date'].split("-")
            d = datetime.datetime(month=int(url_date[0]), day=int(url_date[1]),year=int(url_date[2])) # 09-20-2014

            t = Timeline.objects.get(project_id=int(request.DATA['project_id']))

            #hist = get_most_recent_history_by_project_id(request.DATA['project_id'], datetime.datetime(month=12, day=30, year=9999))

            #determine all differences between current version and old version


            #determine where differences are. Also, update current values for each.

            #old values of things moved into this history object. ONLY do so if value changed(in request.DATA and is diff than old.).
            oldVals = History()
            oldVals.date = d
            t.date = d
            #print hist.title,hist.wiki,hist.author,"<-shuold be title, w, author"
            #print hist.wiki is request.DATA['wiki']
            #print "old values \n new value"
            #print "------------------------------"
            if 'wiki' in request.DATA and t.wiki is not request.DATA['wiki']:
                #print t.wiki
                oldVals.wiki = request.DATA['wiki']
                t.wiki = request.DATA['wiki']
                #print t.wiki
            if 'title' in request.DATA and t.title is not request.DATA['title']:
                #print t.title
                oldVals.title = request.DATA['title']
                t.title = request.DATA['title']
                #print t.title
            if 'author' in request.DATA and t.author is not request.DATA['author']:
                #print t.author
                oldVals.author = request.DATA['author']
                t.author = request.DATA['author']
                #print t.author
            #print "------------------------------"


             #if number of histories divisible by 10 then make new history include all latest updates from previous 10
            if len(t.history) % 10==0:
                print "history has length:",len(t.history)
                hist = sorted(t.history, key=lambda history: history.date, reverse=True)

                hasauthor = 'author' in request.DATA
                hastitle = 'title' in request.DATA
                haswiki = 'wiki' in request.DATA


                for h in hist:
                        #print h.date,d,'this is it'
                        #print "historical date:",h.date,"input date:", d

                        #print h.date,"should be less than", d
                        if h.date <= d:

                            if not hasauthor or not hastitle or not haswiki:
                                if not hasauthor and not is_empty(h.author):
                                    oldVals.author = h.author
                                    #print "author:",author
                                    hasauthor = True
                                if not hastitle and not is_empty(h.title):
                                    oldVals.title = h.title
                                    #print "title:",title, "is_empty(h.title) returned true in this case"
                                    hastitle = True
                                if not haswiki and not is_empty(h.wiki):
                                    oldVals.wiki = h.wiki
                                    #print "wiki:",wiki
                                    haswiki=True

                            else:
                                break


            #print "upto append history worked."
           # print oldVals
            #actually add historical values into history list in timeline
            t.history.append(oldVals)
            #save all changes to timeline object.
            #print "upto save worked"
            t.save()


        #serializer = TimelineSerializer(data=request.DATA)
        #if serializer.is_valid():
        #    serializer.save()

            #out  = {"project_id":int(t.project_id),
            #                 "title": t.title,
            #                 "author": t.author,
            #                 "date":t.date,
            #                 "wiki":t.wiki}
            #print int(t.project_id)
            out = {int(t.project_id): "Project Updated."}
            return Response(out, status=status.HTTP_206_PARTIAL_CONTENT)
        except:
            return Response("failed.", status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_400_BAD_REQUEST)



#>>> from pymongo import MongoClient
#>>> c = MongoClient()
#>>> c.test_database
#Database(MongoClient('localhost', 27017), u'test_database')
#>>> c['test-database']
#Database(MongoClient('localhost', 27017), u'test-database')


#NOTE: can only delete one at a time using this method. :(
@api_view(['DELETE'])
def delete_project(request):
    if request.method=="DELETE":
        print '"delete project called'
        try:
            #print "hi",str(request.DATA)
            #c = MongoClient()
            #c.my_database['']

            database_wrapper = MongoClient()['my_database']

            collection = database_wrapper.osf_timeline

            collection.find_and_modify(query={'project_id':id}, )
            return Response("deleted project_id="+str(id),status.HTTP_200_OK )
        except:
            Response("failed to delete project_id "+str(request.DATA['project_id']), status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_all_projects(request):
    if request.method=="DELETE":
        print '"delete project called'
        try:

            database_wrapper = MongoClient()['my_database']
            collection = database_wrapper.osf_timeline
            collection.remove({})
            return Response("all projects deleted.",status.HTTP_200_OK )
        except:
            Response("failed to delete all projects ", status=status.HTTP_400_BAD_REQUEST)
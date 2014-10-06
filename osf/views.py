
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
        print str(request.DATA)
        if 'project_id' not in request.DATA or not request.DATA['project_id']:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if not proper_creation_request(request.DATA):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        post_date = request.DATA['date'].split("-")
        d = datetime.datetime(month=int(post_date[0]), day=int(post_date[1])+1,year=int(post_date[2])) # 09-20-2014

        Timeline(project_id=int(request.DATA['project_id']),
                 wiki=request.DATA['wiki'],
                 author=request.DATA['author'],
                 title=request.DATA['title'],
                 date=d).save()

        #serializer = TimelineSerializer(data=request.DATA)
        #if serializer.is_valid():
        #    serializer.save()
        #TODO: you can make the response value be equal to the input data to match what other methods do.
        return Response("new project created", status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST)



def get_most_recent_history_by_project_id(id, d):
    try:
        t = Timeline.objects.get(project_id=int(id))
        #print t, "this is the timeline"

        #t = Timeline.objects.all()

        author = ""
        title=""
        wiki=""
        date=""
        hasauthor=False
        hastitle=False
        haswiki=False
        hasdate=False

        #for i in t.history:
        #    print i.date

        #sort by date
        hist = sorted(t.history, key=lambda history: history.date, reverse=True)
        #for i in hist:
            #print i.date
        for i in hist:
            print i.wiki
        for h in hist:
            #print h.date,d,'this is it'
            print "historical date:",h.date,"input date:", d
            if h.date <= d and (not hasauthor or not hasdate or not hastitle or not haswiki):
                if not hasauthor and h.author is not "" and h.author != None and h.author is not None:
                    author = h.author
                    hasauthor = True
                if not hastitle and h.title is not "" and h.title != None and h.title is not None:
                    title = h.title
                    hastitle = True
                if not haswiki and h.wiki is not "" and h.wiki != None and h.wiki is not None:
                    wiki = h.wiki
                    haswiki=True
                if not hasdate and h.date is not "" and h.date != None and h.date is not None:
                    date = h.date
                    hasdate = True
                print wiki
            else:
                break
        most_recent_hist = History(title=title, author=author, wiki=wiki, date=date)
        return most_recent_hist
    except:
        return None

@csrf_exempt
@api_view(['GET'])
def project_detail(request, format=None):
    print "get called"
    if request.method=="GET":
        if 'project_id' not in request.GET or not request.GET['project_id']:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if 'date' in request.GET and request.GET['date']:

            url_date = request.GET['date'].split("-")
            d = datetime.datetime(month=int(url_date[0]), day=int(url_date[1])+1,year=int(url_date[2])) # 09-20-2014
            h= get_most_recent_history_by_project_id(request.GET['project_id'],d)

            print h.wiki, h.title, h.author,h.date

            return Response((request.GET['project_id'],h.author, h.title, h.wiki, h.date) , status = status.HTTP_200_OK)
            #return Response("No results attained.",status=status.HTTP_204_NO_CONTENT)


        try:
            t = Timeline.objects.get(project_id= int(request.GET['project_id']) )


            return Response((t.project_id, t.author, t.title, t.wiki, t.date) , status=status.HTTP_200_OK)
        except:
            return Response("No results attained.", status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_400_BAD_REQUEST)





@api_view(['POST'])
def update_project(request):
    if request.method=="POST":
        print '"update project called'
        print str(request.DATA)
        if 'project_id' not in request.DATA or not request.DATA['project_id']:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if 'date' not in request.DATA or not request.DATA['date']: #written yyyy-dd-mm
            return Response("must add date for when this historical value was added", status=status.HTTP_400_BAD_REQUEST)
        try:
            t = Timeline.objects.get(project_id=int(request.DATA['project_id']))
            #hist = sorted(t.history, key=lambda history: history.date, reverse=True)

            hist=get_most_recent_history_by_project_id(request.GET['project_id'])
            print hist,t,"supposed to be here"
            #determine all differences between current version and old version

            wikichanged=False
            titlechanged=False
            authorchanged=False
            #determine where differences are. Also, update current values for each.

            print hist[-1].title,hist[-1].wiki,hist[-1].author

            if hist[-1].wiki is not request.DATA['wiki']:
                wikichanged=True
                t.wiki = request.DATA['wiki']
            if hist[-1].title is not request.DATA['title']:
                titlechanged=True
                t.title = request.DATA['title']
            if hist[-1].author is not request.DATA['author']:
                authorchanged=True
                t.author = request.DATA['author']
            print wikichanged, titlechanged, authorchanged

            #move all differences into history
            if wikichanged or titlechanged or authorchanged:
                oldVals = History()
                if wikichanged:
                    oldVals.wiki=request.DATA['wiki']
                if titlechanged:
                    oldVals.title=request.DATA['title']
                if authorchanged:
                    oldVals.author=request.DATA['author']

                url_date = request.DATA['date'].split("-")
                d = datetime.datetime(month=int(url_date[0]), day=int(url_date[1])+1,year=int(url_date[2])) # 09-20-2014
                oldVals.date = d
                #actually add historical values into history list in timeline
                t.history.append(oldVals)

                #save all changes to timeline object.
                t.save()


        #serializer = TimelineSerializer(data=request.DATA)
        #if serializer.is_valid():
        #    serializer.save()
            return Response((t.project_id, t.author, t.title, t.wiki, t.date), status=status.HTTP_206_PARTIAL_CONTENT)
        except:
            return Response("failed.", status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_400_BAD_REQUEST)


#steps to using this are:
# curl

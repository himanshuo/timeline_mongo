#from django.test import TestCase
from unittest import TestCase

__author__ = 'himanshu'

#from osf.models import Timeline,History

import requests
import urllib
import datetime
import time
from datetime import tzinfo
import calendar
#--data "csrfmiddlewaretoken=QX4YKZLbWnYH6RGBdcEqe6CezwHlLej1
# &_content_type=application%2Fx-www-form-urlencoded
# &_content=author%3Da2%26wiki%3Dw2%26project_id%3D2%26date%3D09-21-2014"
#
#
# http://localhost:8000/update_project/



def create_project(project_id, date, title, wiki, author, port):
    payload = {'project_id': project_id, 'date': date,'title':title, 'wiki':wiki, 'author':author}
    payload = urllib.urlencode(payload) # date=09-20-2014&wiki=w1&project_id=3&author=a1&title=t1   ???correct????

    print payload
    data = {'csrfmiddlewaretoken':'QX4YKZLbWnYH6RGBdcEqe6CezwHlLej1',
            '_content_type':'application/x-www-form-urlencoded',
            '_content': payload}#after application, not sure if %2F or /
    r = requests.post('http://localhost:'+str(port)+'/create_new_project/', data=data)
    #returns a list? can you turn it into json?

    return r.json()

def get_project(project_id,port, date=None, ):
    if date is None:
        payload = {'project_id': project_id}
        r = requests.get('http://localhost:'+str(port)+'/project_detail/', params=payload)
        return r.json()
    else:
        payload = {'project_id': project_id, 'date': date}
        r = requests.get('http://localhost:'+str(port)+'/project_detail/', params=payload)
        return r.json()





def update_project(project_id, date, port, title=None, wiki=None, author=None):
    #buid payload
    payload=dict()
    payload['project_id']= project_id
    payload['date']= date
    if title is not None:
        payload['title']=title
    if wiki is not None:
        payload['wiki']=wiki
    if author is not None:
        payload['author']=author

    payload = urllib.urlencode(payload) # date=09-20-2014&wiki=w1&project_id=3&author=a1&title=t1   ???correct????

    print payload
    data = {'csrfmiddlewaretoken':'QX4YKZLbWnYH6RGBdcEqe6CezwHlLej1',
            '_content_type':'application/x-www-form-urlencoded',
            '_content': payload}#after application, not sure if %2F or /
    r = requests.post('http://localhost:'+str(port)+'/update_project/', data=data)
    return r.json()


def delete_project(project_id, port):
#csrfmiddlewaretoken=zuqEpa8H4yg3v8Ba4zfFEhWXRjP5nzmP&_method=DELETE
    payload={'project_id':int(project_id)}
    payload = urllib.urlencode(payload)
    data = {'csrfmiddlewaretoken':'zuqEpa8H4yg3v8Ba4zfFEhWXRjP5nzmP',
            '_method':'DELETE',
            'project_id': int(project_id)}#after application, not sure if %2F or /
    r = requests.delete('http://localhost:'+str(port)+'/delete_project/', data=data)

def delete_all_projects_in_range(start, end, port):
    for i in range(start, end):
        delete_project(i, port)

def delete_all_projects(port):
    payload={}
    payload = urllib.urlencode(payload)
    data = {'csrfmiddlewaretoken':'zuqEpa8H4yg3v8Ba4zfFEhWXRjP5nzmP',
            '_method':'DELETE'}
    r = requests.delete('http://localhost:'+str(port)+'/delete_all_projects/', data=data)



#can make more complex.
def convert_utc_format(month, day, year):
    #2014-09-20T00:00:00
    return year+"-"+month+"-"+day+"T"+"00:00:00"


class TestTimeline(TestCase):
    def setUp(self):
        d=convert_utc_format("09", "20","2014")
        self.original = {"title": 't1',
                             "author": 'a1',
                             "date": str(d),
                             "wiki":'w1'}
    #def tearDown(self):
        #determine how to delete.
        #Timeline.objects.raw_update()
    #    pass

    def test_simple(self):
        original = self.original

        original['project_id'] = 3000
        old = original.copy()

        x= create_project(3000,'09-20-2014', 't1','w1','a1', port=8000)
        self.assertEqual(x, original)

        nextday=convert_utc_format("09","21","2014")
        original['title']='t2'
        original['date']=nextday

        self.assertEqual(update_project(3000, date="09-21-2014", title= "t2", port=8000),original )

        self.assertEqual(get_project(3000, port=8000), original)
        del old["date"]
        self.assertEqual(get_project(3000,date="09-20-2014", port=8000),old)
        delete_all_projects(8000)

    """
    def test_simple_thousand(self):

        list_of_times = []
        for i in range(1,1000):
            #clean
            t1 = time.time()
            original = self.original.copy()

            original['project_id'] = i
            old = original.copy()

            x= create_project(i,'09-20-2014', 't1','w1','a1', port=8000)
            self.assertEqual(x, original)

            nextday=convert_utc_format("09","21","2014")
            original['title']='t2'
            original['date']=nextday

            self.assertEqual(update_project(i, date="09-21-2014", title="t2", port=8000),original )

            self.assertEqual(get_project(i, port=8000), original)
            del old["date"]
            self.assertEqual(get_project(i,date="09-20-2014", port=8000),old)
            t2 = time.time()
            list_of_times.append(t2-t1)
        print float(sum(list_of_times))/1000.0
        self.assertTrue(float(sum(list_of_times))/1000.0 < 0.5)
        delete_all_projects(8000)
    """


    def test_thousand_updates(self):
        original = self.original.copy()
        original['project_id'] = 1
        old = original.copy()
        x = create_project(1,'09-20-2014', 't1','w1','a1', port=8000)
        self.assertEqual(x, original)

        list_of_times = []
        for i in range(2,10):
            t1 = time.time()
            nextyear=convert_utc_format("09","21",str(2014+i))
            original['title'] = 't'+str(i)
            original['date']= nextyear

            self.assertEqual(update_project(1, date=nextyear, title='t'+str(i), port=8000),original)

            self.assertEqual(get_project(1, port=8000), original)

            t2 = time.time()
            list_of_times.append(t2-t1)
        print float(sum(list_of_times))/10.0
        self.assertTrue(float(sum(list_of_times))/10.0 < 0.1)
        delete_all_projects(8000)


#things to test:
#1) diff ports
#2) tons of updates
#3) time for each specific portion: create, update, get, get_historical
#4) determine if tweaks make faster
#5) diff amounts of input sizes - does larger input size make slower?
#6) how does concurrancy effect this. do so for all of these.


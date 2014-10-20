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

    #print payload
    data = {'csrfmiddlewaretoken':'QX4YKZLbWnYH6RGBdcEqe6CezwHlLej1',
            '_content_type':'application/x-www-form-urlencoded',
            '_content': payload}#after application, not sure if %2F or /
    r = requests.post('http://localhost:'+str(port)+'/create_new_project/', data=data)
    #returns a list? can you turn it into json?
    print r.status_code
    ret=r.json()
    if ret[str(project_id)] == "Project Created." and r.status_code < 300:
        ret[project_id] = "Project Created."
        del ret[str(project_id)]
        return ret
    return ret


def get_project(project_id,port, date=None, ):
    if date is None:
        payload = {'project_id': project_id}
        r = requests.get('http://localhost:'+str(port)+'/project_detail/', params=payload)
        if r.status_code<300:
            return r.json()
        else:
            return {project_id:"status code was not 2xx"}
    else:
        payload = {'project_id': project_id, 'date': date}
        r = requests.get('http://localhost:'+str(port)+'/project_detail/', params=payload)
        if r.status_code<300:
            return r.json()
        else:
            return {project_id:"status code was not 2xx"}





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

    #print payload
    data = {'csrfmiddlewaretoken':'QX4YKZLbWnYH6RGBdcEqe6CezwHlLej1',
            '_content_type':'application/x-www-form-urlencoded',
            '_content': payload}#after application, not sure if %2F or /
    r = requests.post('http://localhost:'+str(port)+'/update_project/', data=data)
    ret= r.json()
    if ret[str(project_id)] == "Project Updated." and r.status_code < 300:
        ret[project_id] = "Project Updated."
        del ret[str(project_id)]
        return ret
    return ret


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


class TestTimeline():
    def __init__(self):
        #d=convert_utc_format("09", "20","2014")
        self.original = {"title": 't1',
                             "author": 'a1',
                             #"date": str(d),
                             "wiki":'w1'}
        self.ports = [8000,9000]
        #8000 is mongo
        #9000 is postgres
        #2424 is hybrid

    def works(self, should_be, actually_is, test_name):
        if should_be != actually_is:
            print test_name,"failed. It should have been:" ,should_be,"but was:",actually_is
            return False
        return True

    def test_simple(self):
        for p in self.ports:


            original = self.original
            t1 = time.time()
            original['project_id'] = 3000
            old = original.copy()

            x= create_project(3000,'09-20-2014', 't1','w1','a1', port=p)

            if not self.works(test_name="test_simple", should_be={3000:"Project Created."}, actually_is=x):
                return
            nextday=convert_utc_format("09","21","2014")
            original['title']='t2'
            #original['date']=nextday

            y= update_project(3000, date="09-21-2014", title= "t2", port=p)

            if not self.works(test_name="test_simple", should_be={3000: "Project Updated."}, actually_is=y):
                return
            z = get_project(3000, port=p)


            if not self.works(test_name="test_simple", should_be=original, actually_is=z):
                return

            q = get_project(3000,date="09-20-2014", port=p)

            if not self.works(test_name="test_simple", should_be=old, actually_is=q):
                return

            t2 = time.time()
            delete_all_projects(p)
            print "Port",p,": Went through all steps once for one project in",t2-t1,"seconds"


    def test_simple_x_times(self, num_times):
        for p in self.ports:
            list_of_times = []
            test_passed = True
            for i in range(1,num_times):
                #clean
                t1 = time.time()
                original = self.original.copy()

                original['project_id'] = i
                old = original.copy()

                x= create_project(i,'09-20-2014', 't1','w1','a1', port=p)
                test_passed =  x == original
                if not test_passed:
                    print "test_simple_x_times failed", x, "!=", original
                    return

                nextday=convert_utc_format("09","21","2014")
                original['title']='t2'
                original['date']=nextday

                y = update_project(i, date="09-21-2014", title="t2", port=p)
                test_passed = y ==original
                if not test_passed:
                    print "test_simple_x_times failed", y, "!=", original
                    return

                z = get_project(i, port=p)
                test_passed = z ==original
                if not test_passed:
                    print "test_simple_x_times failed", z, "!=", original
                    return

                del old["date"]

                q = get_project(i,date="09-20-2014", port=p)
                test_passed = q==old
                if not test_passed:
                    print "test_simple_x_times failed", q, "!=", original
                    return

                t2 = time.time()
                list_of_times.append(t2-t1)
            print "Port",p, ": Ran",num_times,"project iterations in average of ", float(sum(list_of_times))/float(num_times),"seconds"

            delete_all_projects(p)



    def test_x_updates(self, num_times):

        for p in self.ports:
            test_passed = True
            original = self.original.copy()
            original['project_id'] = 1
            old = original.copy()
            x = create_project(1,'09-20-2014', 't1','w1','a1', port=p)
            test_passed = x== original
            if not test_passed:
                print "test_thousand_updates failed.", x ,"!=",original
                return

            list_of_times = []
            for i in range(2,num_times+2):
                t1 = time.time()
                nextyear=convert_utc_format("09","21",str(2014+i))
                original['title'] = 't'+str(i)
                original['date']= nextyear

                y = update_project(1, date="09-21-"+str(2014+i), title='t'+str(i), port=p)
                test_passed =  y==original
                if not test_passed:
                    print "test_thousand_updates failed.", y ,"!=",original
                    return

                q = get_project(1, port=p)
                test_passed =  q==original
                if not test_passed:
                    print "test_thousand_updates failed.", q ,"!=",original
                    return
                t2 = time.time()
                list_of_times.append(t2-t1)
            print "ran", num_times ,"updates on single project in average of ",float(sum(list_of_times))/float(num_times),"seconds"
            delete_all_projects(p)




def show_options(options):
    for i in range(0,len(options)):
        print i,"-", options[i]
    return ""




if __name__=="__main__":
    while True:
        delete_all_projects(8000)
        print "Input Test Option (each option tests all three set ups):"
        options={}
        options[0]="Exit"
        options[1]="simple all steps"
        options[2] ="thousand all steps"
        options[3] ="thousand create project"
        options[4] ="thousand update randomly"
        options[5] ="thousand update and view project randomly"
        options[6] ="view single project with update spread 10,000 histories apart"
        options[7] ="million all steps"
        options[8] ="million create project"
        options[9] ="million update randomly"
        options[10] ="million update and view project randomly"
        options[11] ="view single project with update spread million histories apart"

        test = TestTimeline()


        def case1():
            test.test_simple()
        def case2():
            test.test_simple_x_times(1000)
        def case4():
            test.test_x_updates(1000)

        cases = {
            1: case1,
            2: case2,
            4: case4
        }
        option = int(input(show_options(options)))

        if option==0:
            break
        else:
            cases[option]()






#things to test:
#1) diff ports
#2) tons of updates
#3) time for each specific portion: create, update, get, get_historical
#4) determine if tweaks make faster
#5) diff amounts of input sizes - does larger input size make slower?
#6) how does concurrancy effect this. do so for all of these.


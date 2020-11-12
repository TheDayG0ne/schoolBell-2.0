#!/usr/bin/python
# -*- coding: utf-8 -*-

import cgi, re, json
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import collections

from config import * 

class MainRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path == '/':
            
            lessons = readSchedule()
            schedule = ''
            for lesson in lessons:
                schedule += u"<b>Час "+lesson+"</b>: "+lessons[lesson].get('start', '--:--') + " - " + lessons[lesson].get('end', '--:--') + "<br />"
            
            data = {
                'schedule': schedule.encode('utf-8')
            }
            
            TemplateOut(self, 'index.html', data)
            return

        elif self.path == '/form.html':
            
            lessons = readSchedule()

            form = ''
            for lesson in lessons:
                form += u"<div class='form_block'><label>Час "+lesson+"</label> <input type='text' name='lesson_"+lesson+"_start' value='"+lessons[lesson].get('start', '--:--') + "'> - <input type='text' name='lesson_"+lesson+"_end' value='"+lessons[lesson].get('end', '--:--') + "'> </div> """

            data = {
                'form': form.encode('utf-8')
            }
            
            TemplateOut(self, 'form.html', data)
            return
        
        elif self.path == '/remote.html':
            
            lessons = readScheduleRemote()

            form = ''
            for lesson in lessons:
                form += u"<div class='form_block'><label>Час "+lesson+"</label> <input type='text' name='lesson_"+lesson+"_start' value='"+lessons[lesson].get('start', '--:--') + "'> - <input type='text' name='lesson_"+lesson+"_end' value='"+lessons[lesson].get('end', '--:--') + "'> </div> """

            data = {
                'form': form.encode('utf-8')
            }
            
            TemplateOut(self, 'form.html', data)
            return

        else:
            try:
                TemplateOut(self, self.path)
            except IOError:
                self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):

        # Parse the form data posted
        form = cgi.FieldStorage(
            fp=self.rfile, 
            headers=self.headers,
            environ={
                'REQUEST_METHOD':'POST',
                'CONTENT_TYPE':self.headers['Content-Type'],
            }
        )

        lessons = {}
        if self.path.endswith('save'):

            # Echo back information about what was posted in the form
            for field in form.keys():

                field_item = form[field]

                if type(field_item) == type([]):
                    pass # no arrays processing now
                else:
                    if field_item.filename:
                        pass #no files now.
                    else:
                        if re.match('lesson_([\d]+)_(start|end)', field):
                            (lesson, state) = re.findall('lesson_([\d]+)_(start|end)', field)[0]
                            try:
                                lessons[lesson]
                            except Exception:
                                lessons[lesson] = {}

                            lessons[lesson][state] = field_item.value

            # printlessons
            json_s = json.dumps(lessons)

            if json_s:
                try:
                    f = open(JSON_FILE, 'w+') 
                    f.write(json_s)
                    f.close()

                    HTMLOut(self, 'Saved OK.' + JS_REDIRECT)
                except IOError, e:
                    # raise e
                    HTMLOut(self, 'Error saving. IO error. '+e.message)
            else:
                HTMLOut(self, 'Json Error.')
        else:
            self.send_error(404, 'Wrong POST url: %s' % self.path)

        return



def Redirect(request, location):
    request.send_response(301)
    request.send_header('Location', location)
    request.end_headers()           
    return     

def Headers200(request):
    request.send_response(200)
    request.send_header('Content-type',    'text/html')
    request.end_headers()         
    return   

def TemplateOut(request, out_file, data = {}):

    f = open(SCRIPT_DIR + out_file) 
    out = f.read()
    f.close()

    #tiny template engine
    for key, var in data.items():
        out = out.replace("{{"+key+"}}", var)

    HTMLOut(request, out)

def HTMLOut(request, html):
    Headers200(request)

    f = open(SCRIPT_DIR + 'base.html') 
    out = f.read()
    f.close()

    out = out.replace("{{content}}", html)
    request.wfile.write(out)

def readSchedule():

    try:
        f = open(JSON_FILE, 'r') 
        json_s = f.read()
        f.close()
    except IOError:
        return [] 
    
    try:
        lessons = json.loads(json_s)
    except Exception:
        return []

    lessons = collections.OrderedDict(sorted(lessons.items()))

    return lessons

def readScheduleRemote():

    import urllib2

    try:
        response = urllib2.urlopen(REMOTE_URL)
        json_s = response.read()    
    except Exception:
        return []

    try:
        lessons = json.loads(json_s)
    except Exception:
        return []

    lessons = collections.OrderedDict(sorted(lessons.items()))

    return lessons

def main():
    try:
        server = HTTPServer(('', 8088), MainRequestHandler)
        print 'Started httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server.'
        server.socket.close()

if __name__ == '__main__':
    main()

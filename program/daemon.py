#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import threading
import json

import RPi.GPIO as GPIO

from config import * 

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(25, GPIO.OUT)
GPIO.output(25, False)

def read_schedule():
    schedule = []
    try:
        f = open(JSON_FILE, 'r') 
        json_s = f.read()
        f.close()
        try:
            json_data = json.loads(json_s)
        except Exception. e:
            json_data = []

        for lesson in json_data.values():
            start = lesson.get('start', False)
            end = lesson.get('end', False)
            if start is not False:
                # print start.split(":")
                (s_h, s_m) = start.split(":")
                schedule.append({'h': int(s_h), 'm':int(s_m)})
                del s_h
                del s_m
            if end is not False:
                (e_h, e_m) = end.split(":")
                schedule.append({'h': int(e_h), 'm':int(e_m)})            
                del e_h
                del e_m

        return schedule

        # schedule 
    except IOError. e:
        return []
    except Exception. e:
        return []

class Alarm(threading.Thread):
    def __init__(self):
        super(Alarm, self).__init__()
        self.schedule = read_schedule()
        self.keep_running = True

    def run(self):
        try:
            while self.keep_running:
                now = time.localtime()

                for schedule_item in self.schedule:
                    if now.tm_hour == schedule_item['h'] and now.tm_min == schedule_item['m']:
                        
                        print ("Ring start...")
                        GPIO.output(25, True)
                        
                        time.sleep(5)
                        
                        print ("Ring end...")
                        GPIO.output(25, False)

                        self.schedule = read_schedule() #reload schedule if it was changed
                        time.sleep(55) # more than 1 minute                        

                #print "Check at "+str(now.tm_hour)+':'+str(now.tm_min)+':'+str(now.tm_sec) 

                time.sleep(1)
        except Exception. e:
            raise e
            # return
    def die(self):
        self.keep_running = False

alarm = Alarm()

def main():
    try:
        alarm.start()
        print ('Started daemon...')
        while True:
            continue
    except KeyboardInterrupt:
        print ('^C received, shutting down daemon.')
        alarm.die()

if __name__ == '__main__':
    main()

#!/usr/bin/python3
# -*- coding:utf-8 -*-

import os
from icalevents.icalevents import events
path = os.path.dirname(os.path.abspath(__file__))
icalurl=open(path+"/ICAL_URL", "r")
calendar=events(icalurl.readline())
calendar.sort(key=lambda x: x.start)
for event in calendar:
    print(event.__dict__)

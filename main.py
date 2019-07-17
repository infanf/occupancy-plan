#!/usr/bin/python3
# -*- coding:utf-8 -*-

import epd2in13b
import hashlib
import json
import os
import time
import traceback
from PIL import Image,ImageDraw,ImageFont
from datetime import datetime, timedelta, timezone
from icalevents.icalevents import events
from icalevents.icalparser import Event

currentEvent = None
nextEvent = None
calendarCache = []

def eventsequal(eventA: Event, eventB: Event) -> bool:
    return eventA.uid == eventB.uid and eventA.start == eventB.start and eventA.end == eventB.end

def updatedisplay(reloadit=False, clearfirst=False):
    try:
        global currentEvent, nextEvent, calendarCache
        path = os.path.dirname(os.path.abspath(__file__))
        epd = epd2in13b.EPD()
        epd.init()
        if clearfirst:
            epd.Clear()
            epd.sleep()
            reloadit = True
        unsetNext = True
        try:
            icalurl=open(path+"/ICAL_URL", "r")
            calendar=events(icalurl.readline())
            calendarCache=calendar
        except:
            calendar=calendarCache
        index = 0
        calendar.sort(key=lambda x: x.start)
        for event in calendar:
            if index == 0:
                if event.start < datetime.now(timezone.utc): # room is occupied at the moment, event is current event
                    reloadit = reloadit or currentEvent == None or not eventsequal(event, currentEvent)
                    currentEvent = event
                else: # room is free, event is next event
                    if currentEvent: # old event still in cache
                        currentEvent = None
                        reloadit = True
                    unsetNext = False
                    reloadit = reloadit or nextEvent == None or not eventsequal(event, nextEvent)
                    nextEvent = event
                    break
            if index == 1:
                reloadit = reloadit or nextEvent == None or not eventsequal(event, nextEvent)
                nextEvent = event
                unsetNext = False
                break
            index=index+1
        if unsetNext and nextEvent:
            nextEvent = None
            reloadit = True
        if (nextEvent or currentEvent) and len(calendar) == 0:
            nextEvent = None
            currentEvent = None
            reloadit = True
        HBlackimage = Image.new('1', (epd2in13b.EPD_HEIGHT, epd2in13b.EPD_WIDTH), 255)
        HRedimage = Image.new('1', (epd2in13b.EPD_HEIGHT, epd2in13b.EPD_WIDTH), 255)
        drawblack = ImageDraw.Draw(HBlackimage)
        drawred = ImageDraw.Draw(HRedimage)
        fontTiny = ImageFont.truetype(path+'/ProggyTiny.ttf', 16)
        fontSmall = ImageFont.truetype(path+'/ProggyClean.ttf', 16)
        fontBig = ImageFont.truetype(path+'/Roboto-Regular.ttf', 32)
        fontHuge = ImageFont.truetype(path+'/Roboto-Regular.ttf', 44)
        meetingimage = Image.open(path+'/meeting.bmp')
        if currentEvent:
            drawred.rectangle((1, 1, epd2in13b.EPD_HEIGHT - 2, epd2in13b.EPD_WIDTH - 41), fill = 0)
            x=20
            y=4
            drawred.text((x+48, y-2), 'BELEGT', font = fontBig, fill=1)
            drawred.bitmap(bitmap=meetingimage, xy=(x,y), fill=1)
            circimage = Image.open(path+'/circ14.bmp')
            drawred.bitmap(bitmap=circimage, xy=(x+10,y+0), fill=1)
            wrongwayimage = Image.open(path+'/wrongway.bmp')
            drawblack.bitmap(bitmap=wrongwayimage, xy=(x+11,y+1))
            drawred.text((8, epd2in13b.EPD_WIDTH-63), 'Noch bis ' + currentEvent.end.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%H:%M"), font = fontTiny, fill=1)
            if currentEvent.private:
                drawred.text((8, epd2in13b.EPD_WIDTH-52), 'privater Termin', font = fontTiny, fill=1)
            else:
                drawred.text((8, epd2in13b.EPD_WIDTH-52), currentEvent.summary[:32], font = fontTiny, fill=1)
        else:
            x=30
            y=14
            drawblack.bitmap(bitmap=meetingimage, xy=(x,y), fill=0)
            checkimage = Image.open(path+'/check.bmp')
            drawblack.bitmap(bitmap=checkimage, xy=(x+10,y+3), fill=0)
            drawblack.text((x+54, y-7), 'FREI', font = fontHuge, fill=0)
        drawblack.rectangle((0, 0, epd2in13b.EPD_HEIGHT - 1, epd2in13b.EPD_WIDTH - 40), outline = 0)
        if nextEvent:
            hourstillevent = (nextEvent.start - datetime.now(timezone.utc)).seconds // 3600
            minutestillevent = (nextEvent.start - datetime.now(timezone.utc)).seconds // 60 % 60
            if nextEvent.private:
                drawblack.text((8, epd2in13b.EPD_WIDTH - 18), 'privater Termin', font = fontSmall)
            else:
                drawblack.text((8, epd2in13b.EPD_WIDTH - 18), nextEvent.summary[:28], font = fontSmall)
            if hourstillevent == 0 and minutestillevent <= 15:
                reloadit = True
                drawblack.text((8, epd2in13b.EPD_WIDTH - 32), 'Nächste Belegung in', font = fontTiny)
                drawred.text((8, epd2in13b.EPD_WIDTH - 32), '                    ' + str(minutestillevent) + ' Minuten', font = fontTiny)
                drawred.text((9, epd2in13b.EPD_WIDTH - 32), '                    ' + str(minutestillevent), font = fontTiny)
            else:
                drawblack.text((8, epd2in13b.EPD_WIDTH - 32), 'Nächste Belegung um ' + nextEvent.start.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%H:%M"), font = fontTiny)
        else:
            drawblack.text((8, epd2in13b.EPD_WIDTH - 26), 'Demnächst keine Belegung', font = fontSmall)
        if reloadit:
            epd.display(epd.getbuffer(HBlackimage.rotate(180)), epd.getbuffer(HRedimage.rotate(180)))
            epd.sleep()

    except:
        print('traceback.format_exc():\n%s',traceback.format_exc())
        exit()

updatedisplay(True)
while True:
    time.sleep(30)
    updatedisplay(clearfirst=(datetime.now().minute % 60 == 0))

#!/usr/bin/python3
# -*- coding:utf-8 -*-

import epd2in13b
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

try:
    epd = epd2in13b.EPD()
    epd.init()
    print("Clear...")

    print("Drawing")

    HBlackimage = Image.new('1', (epd2in13b.EPD_HEIGHT, epd2in13b.EPD_WIDTH), 255)  # 298*126
    HRedimage = Image.new('1', (epd2in13b.EPD_HEIGHT, epd2in13b.EPD_WIDTH), 255)  # 298*126
    ImageTemplateS = Image.open('template-s.bmp')
    ImageTemplateM = Image.open('template-m.bmp')
    drawblack = ImageDraw.Draw(HBlackimage)
    drawred = ImageDraw.Draw(HRedimage)
    font11 = ImageFont.truetype('./ProggyTinySZ.ttf', 16)
    for x in range(3):
        HBlackimage.paste(ImageTemplateS, (12, 8 + x * 18))
        drawblack.text((44, 10 + x * 18), 'Wolfratshausen', font = font11, fill=0)
        drawblack.text((20, 10 + x * 18), 'S7', font = font11, fill=1)
        drawred.text((170, 10 + x * 18), '00:02', font = font11, fill=0)
    HBlackimage.paste(ImageTemplateM, (12, 8 + 3 * 18))
    drawblack.text((44, 10 + 3 * 18), 'Rosenheim', font = font11, fill=0)
    drawblack.text((23, 10 + 3 * 18), 'M', font = font11, fill=1)
    drawred.text((170, 10 + 3 * 18), '00:13', font = font11, fill=0)
    HBlackimage.paste(ImageTemplateS, (12, 8 + 4 * 18))
    drawblack.text((44, 10 + 4 * 18), 'Pasing', font = font11, fill=0)
    drawblack.text((17, 10 + 4 * 18), 'S20', font = font11, fill=1)
    drawred.text((170, 10 + 4 * 18), '00:24', font = font11, fill=0)
    epd.display(epd.getbuffer(HBlackimage),  epd.getbuffer(HRedimage))

    epd.sleep()

except:
    print('traceback.format_exc():\n%s',traceback.format_exc())
    exit()

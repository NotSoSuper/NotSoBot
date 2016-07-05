#!/usr/bin/env python
 
import sys
import subprocess
from subprocess import call
import aalib 
import PIL
import imghdr
import numpy as np
import random
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
from PIL import ImageOps
from bisect import bisect
from PIL import ImageChops
from PIL.GifImagePlugin import getheader, getdata
global GREYSCALE, BOUNDS
global img_new_magnitude, fontsize

img_new_magnitude = 10 
fontsize = 15

global font
font = ImageFont.truetype("/root/discord/files/FreeMonoBold.ttf", fontsize, encoding="unic")
 
GREYSCALE = [
            " ",
            " ",
            ".,-",
            "_ivc=!/|\\~",
            "gjez2]/(YL)t[+T7Vf",
            "mdK4ZGbNDXY5P*Q",
            "W8KMA",
            "#%$"
            ]

BOUNDS = [36,72,108,144,180,216,252]
 
def get_image_text(img):   
  im = img
  im=im.resize((100,100),Image.BILINEAR)
  im=im.convert("L") # convert to mono
  str=""
  for y in range(0,im.size[1]):
    for x in range(0,im.size[0]):
      LUM=255-im.getpixel((x,y))
      row=bisect(BOUNDS,LUM)
      possibles=GREYSCALE[row]
      str=str+possibles[random.randint(0,len(possibles)-1)]
    str=str+"\n"

  return str

def image_to_text(img):
  text = get_image_text(img)
  img = Image.new("RGBA", (100,100))
  draw = ImageDraw.Draw(img)
  draw.text((0,0), text, (0,0,0))
  return img

def create_ascii_image(videofilename):
  myimage = videofilename
  image_width, image_height = myimage.size
  aalib_screen_width= int(image_width/24.9)*img_new_magnitude
  aalib_screen_height= int(image_height/41.39)*img_new_magnitude
  screen = aalib.AsciiScreen(width=aalib_screen_width, height=aalib_screen_height )
  myimage = videofilename.convert("L").resize(screen.virtual_size)
  screen.put_image((0,0), myimage)
  y = 0
  how_many_rows = len ( screen.render().splitlines() ) 
  new_img_width, font_size = font.getsize (screen.render().splitlines()[0])
  img=Image.new("RGBA", (new_img_width, how_many_rows*fontsize), (255,255,255))
  draw = ImageDraw.Draw(img)
  for lines in screen.render().splitlines():
    draw.text( (0,y), lines, (0,0,0),font=font )
    y = y + fontsize
  imagefit = ImageOps.fit(img, (image_width, image_height), Image.ANTIALIAS)
  return imagefit
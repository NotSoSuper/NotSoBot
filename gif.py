import wand
import glob
import subprocess
import os
from PIL import Image
from images2gif import writeGif
from image import *
from subprocess import call

class AnimatedGif:
  def __init__(self, GIF_NAME):
    self.im = Image.open(GIF_NAME)
    self.name = GIF_NAME
    self.frames = []

  def get_frames(self):
    try:
      i= 0
      while 1:
        self.im.seek(i)
        imframe = self.im.copy()
        if i == 0: 
          palette = imframe.getpalette()
        else:
          imframe.putpalette(palette)
        yield imframe
        i += 1
    except EOFError:
      pass

  def split_gif(self):
    for i, frame in enumerate(self.get_frames()):
      self.frames.append(create_ascii_image(frame))

  def construct_frames(self):
    subprocess.call(["ffmpeg", "-y", "-i", "%d.png","-r", "10", "/root/discord/files/gif/2.gif"])
    j = 0
    while j < self.i:
      subprocess.call(["rm", str(j)+".png"])
      j += 1

  def text_frames(self):
    for frame in self.frames:
      frame = create_ascii_image(frame)

  def process_image(self):
    infile = self.name
    try:
      im = Image.open(infile)
    except IOError:
      print("Cant load", infile)
      sys.exit(1)
    self.i = 0
    mypalette = im.getpalette()
    try:
      while 1:
        im.putpalette(mypalette)
        new_im = Image.new("RGBA", im.size)
        new_im.paste(im)
        new_im = create_ascii_image(new_im)
        new_im.save(str(self.i)+'.png')
        self.i += 1
        im.seek(im.tell() + 1)
    except EOFError:
      pass

  def extractFrames(self, gif, out):
    frame = Image.open(gif)
    nframes = 0
    while frame:
      frame.save('%s/%s.png' % (out, nframes), 'GIF')
      nframes += 1
      try:
        frame.seek(nframes)
      except EOFError:
        break
    return True

def liquid(self):
  for s in glob.glob("/root/discord/files/gif/*.png"):
    image = wand.image.Image(filename=s)
    i = image.clone()
    i.transform(resize='800x800>')
    i.liquid_rescale(width=int(i.width*0.5), height=int(i.height*0.5), delta_x=1, rigidity=0)
    i.liquid_rescale(width=int(i.width*1.5), height=int(i.height*1.5), delta_x=2, rigidity=0)
    i.resize(i.width, i.height)
    i.save(filename=s)

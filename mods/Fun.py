import sys
import os
import re
import asyncio
import traceback
import requests
import aiohttp
import urllib.request
import json
import wand
import PIL
import copy
import PIL.Image
import PIL.ImageFont
import PIL.ImageOps
import PIL.ImageDraw
import random
import discord
import subprocess
import time
import html
import urbandict
import shutil
import magic
import numpy as np
import datetime
import macintoshplus
from sys import argv, path
from discord.ext import commands
from utils import checks
from discord.message import Message
from discord.user import User
from pyfiglet import figlet_format
from wand.drawing import Drawing
from wand.image import Image
from wand.color import Color
from PIL import ImageDraw
from PIL import Image
from gif import *
from image import *
from subprocess import call

cool = "```xl\n{0}\n```"
code = "```py\n{0}\n```"
image_mimes = ['image/png', 'image/pjpeg', 'image/jpeg', 'image/x-icon']
google_api = ['apikey']
api_count = 0

PIXEL_ON = 0  # PIL color to use for "on"
PIXEL_OFF = 255  # PIL color to use for "off"

def isimage(url:str):
  r = requests.get(url, stream=True)
  mime = magic.from_buffer(next(r.iter_content(256)), mime=True).decode()
  if any([mime == x for x in image_mimes]):
    return True
  else:
    return False

def isgif(url:str):
  r = requests.get(url, stream=True)
  mime = magic.from_buffer(next(r.iter_content(256)), mime=True).decode()
  if mime == "image/gif":
    return True
  else:
    return False

async def download(link:str, path:str):
  with aiohttp.ClientSession() as session:
    async with session.get(link) as resp:
      data = await resp.read()
      with open(path,"wb") as f:
        f.write(data)

#cant remember where I got this from google
def text_image(text_path, font_path=None):
    grayscale = 'L'
    with open(text_path) as text_file:
      lines = tuple(l.rstrip() for l in text_file.readlines())

    large_font = 20
    font_path = font_path or '/root/discord/files/cour.ttf'
    try:
      font = PIL.ImageFont.truetype(font_path, size=large_font)
    except IOError:
      font = PIL.ImageFont.load_default()
      print('Could not use chosen font. Using default.')

    pt2px = lambda pt: int(round(pt * 96.0 / 72))
    max_width_line = max(lines, key=lambda s: font.getsize(s)[0])
    test_string = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    max_height = pt2px(font.getsize(test_string)[1])
    max_width = pt2px(font.getsize(max_width_line)[0])
    height = max_height * len(lines)
    width = int(round(max_width + 40))
    image = PIL.Image.new(grayscale, (width, height), color=PIXEL_OFF)
    draw = PIL.ImageDraw.Draw(image)

    vertical_position = 5
    horizontal_position = 5
    line_spacing = int(round(max_height * 0.8))
    for line in lines:
      draw.text((horizontal_position, vertical_position),
                line, fill=PIXEL_ON, font=font)
      vertical_position += line_spacing
    c_box = PIL.ImageOps.invert(image).getbbox()
    image = image.crop(c_box)
    return image

def remove(old, new):
  subprocess.call(["rm", old])
  subprocess.call(["rm", new])

class Fun():
  def __init__(self,bot):
    self.bot = bot

  async def gist(self, ctx, idk, content:str):
    gist = {
      'description': 'ASCII for text: "{2}" | \nUploaded from NotSoSuper\'s Bot by: {0} <{1}>.'.format(ctx.message.author.name, ctx.message.author.id, idk),
      'public': True,
      'files': {
          '{0}_ascii.txt'.format(idk): {
              'content': content
          }
      }
    }
    headers = {'Authorization': 'token key'}
    async with aiohttp.post('https://api.github.com/gists', data=json.dumps(gist), headers=headers) as gh:
      if gh.status != 201:
        await self.bot.say('Could not create gist.')
      else:
        js = await gh.json()
        await self.bot.say('Uploaded to gist, URL: <{0[html_url]}>'.format(js))

  #was bored and some guy gave me the idea, dont ask
  # @commands.command(pass_context=True)
  # async def kys(self, ctx, *, user:str):
  #   """rope"""
  #   user = user.replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
  #   if len(ctx.message.mentions) != 0:
  #     user = ctx.message.mentions[0].name
  #   msg = "``` _________     \n|         |    \n|         0 <-- {0}    \n|        /|\\  \n|        / \\  \n|              \n|              \n```\n".format(user)
  #   msg += "**Kill Your Self** ``" + str(user) + "``\n"    
  #   await self.bot.say(msg)

  @commands.command(pass_context=True, aliases=['go', 'googl', 'gogle'])
  async def google(self, ctx, *, text:str=None):
    try:
      global api_count
      if text == None:
        await self.bot.say("Error: Invalid Syntax\n`.google <text>`")
        return
      if len(google_api) == api_count or len(google_api) < api_count:
        api_count = 0
      key = google_api[api_count]
      api_count += 1
      api = "https://www.googleapis.com/customsearch/v1?key={0}&cx=015418243597773804934:it6asz9vcss&q={1}".format(key, text)
      # api = "http://search.yacy.de/yacysearch.json?query={0}".format(text)
      r = requests.get(api)
      response = r.json()
      response_dump = json.dumps(response)
      load = json.loads(response_dump)
      rand = load['items'][0]
      result = rand['link']
      title = rand['title']
      snippet = rand['snippet']
      await self.bot.say("Title: `{0}`".format(title))
      await self.bot.say("`{0}`".format(snippet))
      await self.bot.say(result)
    except Exception as e:
      await self.bot.say("Either no result was found or Google's jewAPI has hit the quota!\nTry again.")
      # await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  @commands.command(pass_context=True)
  async def dddd(self, ctx, *, user:str, direct=None):
    """make dank meme"""
    if len(user) > 25:
      await self.bot.say("ur names 2 long asshole")
      return
    if len(ctx.message.mentions) != 0 and len(ctx.message.mentions) == 1:
      user = ctx.message.mentions[0].name
    post_data = {'template_id': '', 'username': '', 'password' : '', 'text0' : '', 'text1' : '{0}'.format(user)}
    r = requests.post("https://api.imgflip.com/caption_image", data=post_data)
    response = r.json()
    response_dump = json.dumps(response)
    load = json.loads(response_dump)
    url = load['data']['url']
    msg = load['data']['url']
    if direct == "true":
      await self.bot.say(str(msg))
    elif direct == None:
      print(url)
      req = urllib.request.Request(url, None, {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'})
      t = urllib.request.urlopen(req)
      file = open('/root/discord/files/suicide.jpg', 'wb')
      file.write(t.read())
      file.close()
      await self.bot.send_file(ctx.message.channel, file.name)
      os.remove(file.name)
    else:
      print(url)
      req = urllib.request.Request(url, None, {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'})
      t = urllib.request.urlopen(req)
      file = open('/root/discord/files/suicide.jpg', 'wb')
      file.write(t.read())
      file.close()
      await self.bot.send_file(ctx.message.channel, file.name)
      os.remove(file.name)

  @commands.command(pass_context=True)
  async def badmeme(self, ctx, direct=None):
    """returns bad meme (bad api)"""
    try:
      r = requests.get("https://api.imgflip.com/get_memes")
      response = r.json()
      response_dump = json.dumps(response)
      load = json.loads(response_dump)
      url = load['data']['memes'][random.randint(0, 100)]['url']
      msg = load['data']['memes'][random.randint(0, 100)]['url']
      if direct == "true":
        await self.bot.say(str(msg))
      else:
        print(url)
        req = urllib.request.Request(url, None, {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'})
        t = urllib.request.urlopen(req)
        file = open('/root/discord/files/meme.jpg', 'wb')
        file.write(t.read())
        file.close()
        await self.bot.send_file(ctx.message.channel, file.name)
        os.remove(file.name)
    except Exception as e:
      await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  @commands.command(pass_context=True, aliases=['imagemagic', 'imagemagick', 'magic', 'magick'])
  async def magik(self, ctx, url:str=None, url2=None):
    """Apply magik to Image(s)\n .magik image_url or .magik image_url image_url_2"""
    try:
      if url == None:
        await self.bot.say("Error: Invalid Syntax\n`.magik <image_url> <image_url2>*`\n`* = Optional`")
        return
      if len(ctx.message.mentions) > 0 and url2 == None:
        user = ctx.message.mentions[0]
        if user.avatar == None:
          await self.bot.say(":no_entry: Mentioned User Has No Avatar")
          return
        await self.bot.send_typing(ctx.message.channel)
        await self.bot.say("ok, processing")
        avatar = "https://cdn.discordapp.com/avatars/{0}/{1}.jpg".format(user.id, user.avatar)
        rand = str(random.randint(0, 100))
        path = "/root/discord/files/magik_user_{0}.png".format(rand)
        await download(avatar, path)
        if os.path.getsize(path) == 127:
          await self.bot.say(":no_entry: Mentioned User 1's Avatar is Corrupt on Discord Servers!")
          return
        image = wand.image.Image(filename='/root/discord/files/magik_user_{0}.png'.format(rand))
        i = image.clone()
        i.transform(resize='800x800>')
        i.liquid_rescale(width=int(i.width*0.5), height=int(i.height*0.5), delta_x=1, rigidity=0)
        i.liquid_rescale(width=int(i.width*1.5), height=int(i.height*1.5), delta_x=2, rigidity=0)
        i.resize(i.width, i.height)
        i.save(filename='/root/discord/files/nmagik_user_{0}.png'.format(rand))
        await self.bot.send_file(ctx.message.channel, '/root/discord/files/nmagik_user_{0}.png'.format(rand))
        return
      elif url2 != None and len(ctx.message.mentions) > 0:
        user = ctx.message.mentions[0]
        if len(ctx.message.mentions) == 1:
          user2 = ctx.message.mentions[0]
        else:
          user2 = ctx.message.mentions[1]
        if user.avatar == None:
          await self.bot.say(":no_entry: Mentioned User 1 Has No Avatar")
          return
        if user2.avatar == None:
          await self.bot.say(":no_entry: Mentioned User 2 Has No Avatar")
          return
        await self.bot.say("ok, processing")
        avatar = "https://cdn.discordapp.com/avatars/{0}/{1}.jpg".format(user.id, user.avatar)
        avatar2 = "https://cdn.discordapp.com/avatars/{0}/{1}.jpg".format(user2.id, user2.avatar)
        rand = str(random.randint(0, 100))
        path = "/root/discord/files/magik_user_{0}.png".format(rand)
        path2 = "/root/discord/files/magik_user2_{0}.png".format(rand)
        await download(avatar, path)
        await download(avatar2, path2)
        if os.path.getsize(path) == 127:
          await self.bot.say(":no_entry: Mentioned User 1's Avatar is Corrupt on Discord Servers!")
          return
        elif os.path.getsize(path2) == 127:
          await self.bot.say(":no_entry: Mentioned User 2's Avatar is Corrupt on Discord Servers!")
          return
        d = '/root/discord/files/nmagik_user_{0}.png'.format(rand)
        d2 = '/root/discord/files/nmagik2_user_{0}.png'.format(rand)
        image = wand.image.Image(filename=path)
        i = image.clone()
        i.transform(resize='800x800>')
        i.liquid_rescale(width=int(i.width*0.5), height=int(i.height*0.5), delta_x=1, rigidity=0)
        i.liquid_rescale(width=int(i.width*1.5), height=int(i.height*1.5), delta_x=2, rigidity=0)
        i.resize(i.width, i.height)
        i.save(filename=d)
        image2 = wand.image.Image(filename=path2)
        i2 = image2.clone()
        i2.transform(resize='800x800>')
        i2.liquid_rescale(width=int(i.width*0.5), height=int(i.height*0.5), delta_x=1, rigidity=0)
        i2.liquid_rescale(width=int(i.width*1.5), height=int(i.height*1.5), delta_x=2, rigidity=0)
        i2.resize(i.width, i.height)
        i2.save(filename=d2)
        list_im = [d, d2]
        imgs    = [PIL.Image.open(i) for i in list_im]
        min_shape = sorted( [(np.sum(i.size), i.size ) for i in imgs])[0][1]
        imgs_comb = np.hstack( (np.asarray( i.resize(min_shape) ) for i in imgs ) )
        imgs_comb = PIL.Image.fromarray(imgs_comb)
        new_p = '/root/discord/files/nmagik_user_url2_{0}.png'.format(rand)
        imgs_comb.save(new_p)
        await self.bot.send_file(ctx.message.channel, new_p, filename='magik_2users.png')
        os.remove(path)
        os.remove(path2)
        os.remove(new_p)
        return
      if isimage(url) == False:
        await self.bot.say("Invalid or Non-Image!")
        return
      rand = str(random.randint(0, 500))
      rand2 = str(random.randint(0, 500))
      if url2 is None:
        await self.bot.say("ok, applying magik")
        with aiohttp.ClientSession() as session:
          location = '/root/discord/files/magik_{0}.png'.format(rand)
          async with session.get(url) as resp:
            data = await resp.read()
            with open(location, "wb") as f:
              f.write(data)
              f.close()
      elif url2 is not None:
        await self.bot.say("ok, applying magik")
        with aiohttp.ClientSession() as session:
          location = '/root/discord/files/magik_{0}.png'.format(rand)
          location2 = '/root/discord/files/magik2_{0}.png'.format(rand2)
          async with session.get(url) as resp:
            data = await resp.read()
            with open(location, "wb") as f:
              f.write(data)
              f.close()
          async with session.get(url2) as resp:
            data = await resp.read()
            with open(location2, "wb") as f:
              f.write(data)
              f.close()
      exif = {}
      image = wand.image.Image(filename='/root/discord/files/magik_{0}.png'.format(rand))
      exif.update((k[5:], v) for k, v in image.metadata.items()
        if k.startswith('exif:'))
      if url2 is not None:
        exif2 = {}
        image2 = wand.image.Image(filename='/root/discord/files/magik2_{0}.png'.format(rand2))
        exif2.update((k[5:], v) for k, v in image2.metadata.items()
          if k.startswith('exif:'))
      img = wand.image.Image(filename='/root/discord/files/magik_{0}.png'.format(rand))
      print(img.size)
      i = img.clone()
      if url2 is not None:
          with wand.image.Image(filename='/root/discord/files/magik2_{0}.png'.format(rand2)) as B:
            B.clone()
            B.transform(resize='800x800>')
            B.liquid_rescale(width=int(B.width*0.5), height=int(B.height*0.5), delta_x=1, rigidity=0)
            B.liquid_rescale(width=int(B.width*1.5), height=int(B.height*1.5), delta_x=2, rigidity=0)
            B.resize(B.width, B.height)
            B.save(filename='/root/discord/files/nmagik2_{0}.png'.format(rand))
            with wand.image.Image(filename='/root/discord/files/magik_{0}.png'.format(rand)) as A:
              A.clone()
              A.transform(resize='800x800>')
              A.liquid_rescale(width=int(A.width*0.5), height=int(A.height*0.5), delta_x=1, rigidity=0)
              A.liquid_rescale(width=int(A.width*1.5), height=int(A.height*1.5), delta_x=2, rigidity=0)
              A.resize(A.width, A.height)
              A.save(filename='/root/discord/files/nmagik1_{0}.png'.format(rand))
          list_im = ['/root/discord/files/nmagik1_{0}.png'.format(rand), '/root/discord/files/nmagik2_{0}.png'.format(rand)]
          imgs    = [PIL.Image.open(i) for i in list_im]
          min_shape = sorted( [(np.sum(i.size), i.size ) for i in imgs])[0][1]
          imgs_comb = np.hstack( (np.asarray( i.resize(min_shape) ) for i in imgs ) )
          imgs_comb = PIL.Image.fromarray(imgs_comb)
          new_p = '/root/discord/files/nmagik_{0}.png'.format(rand)
          imgs_comb.save(new_p)
      else:
        i.transform(resize='800x800>')
        i.liquid_rescale(width=int(i.width*0.5), height=int(i.height*0.5), delta_x=1, rigidity=0)
        i.liquid_rescale(width=int(i.width*1.5), height=int(i.height*1.5), delta_x=2, rigidity=0)
        i.resize(i.width, i.height)
        i.save(filename='/root/discord/files/nmagik_{0}.png'.format(rand))
      print(exif)
      if len(exif) != 0 and len(str(exif)) <= 2000 and url2 is None:
        await self.bot.say("Exif Data: ```{0}```".format(str(exif)))
      elif url2 is not None and len(exif) != 0 and len(str(exif)) <= 2000 and len(str(exif2)) <= 2000:
          await self.bot.say("Exif Data Image 1: ```{0}```".format(str(exif)))
          await self.bot.say("Exif Data Image 2: ```{0}```".format(str(exif2)))
      elif len(str(exif)) > 2000:
          await self.bot.say("Exif Data too long, truncated")
      else:
          pass
      await self.bot.send_file(ctx.message.channel, '/root/discord/files/nmagik_{0}.png'.format(rand))
      os.system("rm /root/discord/files/magik*")
      os.system("rm /root/discord/files/nmagik*")
    except Exception as e:
      if type(e).__name__ == "Forbidden":
        await self.bot.say("Sorry, I do not have permission to send files!")
      else:
        await self.bot.say("Invalid or Non-Image!")
      print(e)

  @commands.command(pass_context=True)
  async def gmagik(self, ctx, url:str=None, framerate:str=None):
    if url == None:
      await self.bot.say("Error: Invalid Syntax\n`.gmagik <gif_url> <frame_rate>*`\n`* = Optional`")
      return
    gif_url = url
    if len(glob.glob("/root/discord/files/gif/*")) > 0:
      os.system("rm /root/discord/files/gif/*")
    if isgif(gif_url) == False:
      await self.bot.say("Invalid or Non-GIF!")
      return
    await self.bot.send_typing(ctx.message.channel)
    await self.bot.say("ok, processing")
    with aiohttp.ClientSession() as session:
        location = '/root/discord/files/gif/1.gif'
        async with session.get(url) as resp:
          data = await resp.read()
          with open(location, "wb") as f:
            f.write(data)
            f.close()
    if os.path.getsize(location) > 3000000 and ctx.message.author.id != "130070621034905600":
      await self.bot.say("Sorry, GIF Too Large!")
      for image in glob.glob("/root/discord/files/gif/*.png"):
        os.remove(image)
      remove(gif1, gif2)
      return
    gifin = '/root/discord/files/gif/1.gif'
    gifout = '/root/discord/files/gif'
    def ef(gif, out):
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
    ef(gifin, gifout)
    if len(glob.glob("/root/discord/files/gif/*.png")) > 50 and ctx.message.author.id != "130070621034905600":
      await self.bot.say("Sorry, GIF has too many frames!")
      for image in glob.glob("/root/discord/files/gif/*.png"):
          os.remove(image)
      remove(gif1, gif2)
      return
    for image in glob.glob("/root/discord/files/gif/*.png"):
      im = wand.image.Image(filename=image)
      i = im.clone()
      i.transform(resize='800x800>')
      i.liquid_rescale(width=int(i.width*0.5), height=int(i.height*0.5), delta_x=1, rigidity=0)
      i.liquid_rescale(width=int(i.width*1.5), height=int(i.height*1.5), delta_x=2, rigidity=0)
      i.resize(i.width, i.height)
      i.save(filename=image)
    if framerate != None:
      subprocess.call(["ffmpeg", "-y", "-i", "/root/discord/files/gif/%d.png", "-r", "{0}".format(framerate), '/root/discord/files/gif/2.gif'])
    else:
      subprocess.call(["ffmpeg", "-y", "-i", "/root/discord/files/gif/%d.png", '/root/discord/files/gif/2.gif'])
    gif2 = "/root/discord/files/gif/2.gif"
    await self.bot.send_file(ctx.message.channel, gif2)
    for image in glob.glob("/root/discord/files/gif/*.png"):
      os.remove(image)
    remove(gif1, gif2)

  @commands.command(pass_context=True)
  async def caption(self, ctx, url:str=None, text:str=None, color=None, size=None, x:int=None, y:int=None):
    """Add caption to an image\n .caption text image_url"""
    try:
      if url == None:
        await self.bot.say("Error: Invalid Syntax\n`.caption <image_url> <text>** <color>* <size>* <x>* <y>*`\n`* = Optional`\n`** = Wrap text in quotes`")
        return
      if isimage(url) == False:
        await self.bot.say("Invalid or Non-Image!")
        return
      print(url)
      await self.bot.say("ok, processing")
      req = urllib.request.Request(url, None, {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'})
      t = urllib.request.urlopen(req)
      file = open('/root/discord/files/caption.png', 'wb')
      file.write(t.read())
      file.close()
      image = wand.image.Image(filename='/root/discord/files/caption.png')
      img = wand.image.Image(filename=file.name)
      i = img.clone()
      if size != None:
          color = wand.color.Color('{0}'.format(color))
          font = wand.font.Font(path='/root/discord/files/impact.ttf', size=int(size), color=color)
      elif color != None:
          color = wand.color.Color('{0}'.format(color))
          font = wand.font.Font(path='/root/discord/files/impact.ttf', size=40, color=color)
      else:
          color = wand.color.Color('red')
          font = wand.font.Font(path='/root/discord/files/impact.ttf', size=40, color=color)
      if x == None:
        x = None
        y = int(i.height/10)
      if x != None and x > 250:
        x = x/2
      if y != None and y > 250:
        y = y/2
      if x != None and x > 500:
        x = x/4
      if y != None and y > 500:
        y = y/4
      if x != None:
        i.caption(str(text), left=x, top=y, font=font, gravity='center')
      else:
        i.caption(str(text), top=y, font=font, gravity='center')
      i.save(filename='/root/discord/files/caption_.png')
      await self.bot.send_file(ctx.message.channel, '/root/discord/files/caption_.png')
    except Exception as e:
      await self.bot.say("Error: Invalid Syntax\n `.caption <image_url> <text>** <color>* <size>* <x>* <y>*`\n`* = Optional`\n`** = Wrap text in quotes`")
      print(e)

  @commands.command(pass_context=True)
  async def triggered(self, ctx, *, user:str=None):
    """Generate a Triggered Image for a User or Text"""
    if user == None:
      await self.bot.say("Error: Invalid Syntax\n`.triggered <discord_user>`")
      return
    if len(ctx.message.mentions) != 0:
      if "<@!" in user:
        u_id = user.replace("<@!", "").replace(">", "")
      else:
        u_id = user.replace("<@", "").replace(">", "")
      user = discord.Server.get_member(ctx.message.server, user_id=u_id).name
    img = wand.image.Image(filename='/root/discord/files/triggered.png')
    i = img.clone()
    color = wand.color.Color('red')
    font = wand.font.Font(path='/root/discord/files/impact.ttf', size=40, color=color)
    text = "Sorry for triggering you {0}".format(user)
    i.caption(text, top=155, font=font, gravity='center')
    i.save(filename='/root/discord/files/triggered_.png')
    await self.bot.send_file(ctx.message.channel, '/root/discord/files/triggered_.png')

  @commands.command(pass_context=True)
  async def heil(self, ctx, kek:str=None, direct=None):
    """Who will you worship?\n .heil hitler/hydra/megatron (add text here for direct)"""
    if kek == None and ctx.message.channel.id == "152162730244177920":
      await self.bot.say("**Sieg Heil!**\nhttps://mods.nyc/j/hitler")
    elif kek == None:
      await self.bot.say("**Sieg Heil!**")
      await self.bot.send_file(ctx.message.channel, '/root/discord/files/hitler.jpg')

    if direct is not None and kek == "hitler":
      await self.bot.say("**Sieg Heil!**\nhttps://mods.nyc/j/hitler")
    elif kek == "hitler":
      await self.bot.send_file(ctx.message.channel, '/root/discord/files/hitler.jpg')
    
    if direct is not None and kek == "hydra":
      await self.bot.say("**Hail Hydra**\nhttps://mods.nyc/g/hydra")
    elif kek == "hydra":
      await self.bot.say("**Hail Hydra**")
      await self.bot.send_file(ctx.message.channel, '/root/discord/files/hydra.gif')

    if direct is not None and kek == "megatron":
      await self.bot.say("**All Hail Megatron**\nhttps://mods.nyc/j/megatron")
    elif kek == "megatron":
      await self.bot.send_file(ctx.message.channel, '/root/discord/files/megatron.jpg')

  @commands.command(pass_context=True)
  async def aesthetics(self, ctx, *, text:str):
    """Returns inputed text in aesthetics"""
    final = ""
    pre = ' '.join(text)
    for char in pre:
      if not ord(char) in range(33, 127):
        final += char
        continue
      final += chr(ord(char) + 65248)
    await self.bot.say(final)

  @commands.command(pass_context=True)
  @checks.is_owner()
  async def rate_spam(self, ctx):
    shit = ", ".join(map(str, ctx.message.server.members)) 
    for s in shit:
      await self.bot.say("!rate {0} Dumb".format(s))

  @commands.command(pass_context=True)
  async def ascii(self, ctx, *, text:str):
    """Convert text into ASCII"""
    try:
      if len(text) > 1000:
        await self.bot.say("2 long asshole")
        return
      if text == "donger":
        text = "8====D"
      i = PIL.Image.new('RGB', (2000, 1000))
      img = ImageDraw.Draw(i)
      txt = figlet_format(text, font='starwars')
      img.text((20, 20), figlet_format(text, font='starwars'), fill=(0, 255, 0))
      text_width, text_height = img.textsize(figlet_format(text, font='starwars'))
      imgs = PIL.Image.new('RGB', (text_width + 30, text_height))
      ii = ImageDraw.Draw(imgs)
      ii.text((20, 20), figlet_format(text, font='starwars'), fill=(0, 255, 0))
      text_width, text_height = ii.textsize(figlet_format(text, font='starwars'))
      rand = str(random.randint(0, 100))
      path = "/root/discord/files/ascii_{0}.png".format(rand)
      imgs.save(path)
      idk = text
      if len(txt) > 2000:
        await self.gist(ctx, idk, txt)
      else:
        msg = "```fix\n"
        msg += txt
        msg += "```"
        await self.bot.say(msg)
      await self.bot.send_file(ctx.message.channel, path, filename='ascii.png')
    except Exception as e:
      await self.bot.say("invalid text asshole")
      # await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  @commands.command(pass_context=True)
  async def iascii(self, ctx, url:str):
    try:
      if isimage(url) == False:
        await self.bot.say("Not a Image/Invalid URL!")
        return
      r = requests.get(url, stream=True)
      rand = str(random.randint(0, 100))
      txt_path = '/root/discord/files/iascii_{0}.txt'.format(rand)
      final_path = '/root/discord/files/iascii2_{0}.png'.format(rand)
      mime = magic.from_buffer(next(r.iter_content(256)), mime=True).decode()
      if mime == "image/png":
        await self.bot.say("ok, processing")
        location = "/root/discord/files/iascii_{0}.png".format(rand)
        with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.read()
                with open(location, "wb") as f:
                    f.write(data)
                    f.close()
        jpg_path = '/root/discord/files/iascii_{0}.jpg'.format(rand)
        with wand.image.Image(filename=location, background=wand.color.Color('white')) as original:
            with original.convert('jpeg') as converted:
              converted.save(filename=jpg_path)
        os.system("jp2a {0} --output={1}".format(jpg_path, txt_path))
        image = text_image(txt_path)
        image.save(final_path)
        await self.bot.send_file(ctx.message.channel, final_path, finalname='iascii.png')
      elif mime == "image/jpeg":
        await self.bot.say("ok, processing")
        location = "/root/discord/files/iascii_{0}.jpg".format(rand)
        await download(url, location)
        os.system("jp2a {0} --output={1}".format(location, txt_path))
        image = text_image(txt_path)
        image.save(final_path)
        await self.bot.send_file(ctx.message.channel, final_path, filename='iascii.png')
    except Exception as e:
      await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  @commands.command(pass_context=True)
  async def gascii(self, ctx, url:str=None, liquid=None):
    """Gif to ASCII"""
    try:
      if url == None:
        await self.bot.say("Error: Invalid Syntax\n`.gascii <gif_url> <liquid_rescale>*`\n`* = Optional`")
        return
      gif_url = url
      gif_name = '/root/discord/files/gif/1.gif'
      new_gif_name = '/root/discord/files/gif/2.gif'
      if isgif(url) == False:
        await self.bot.say("Invalid or Non-GIF!")
        return
      await self.bot.say("ok, processing")
      location = '/root/discord/files/gif/1.gif'
      await download(url, location)
      if os.path.getsize(location) > 450000 and ctx.message.author.id != "130070621034905600":
        await self.bot.say("Sorry, GIF Too Large!")
        for image in glob.glob("/root/discord/files/gif/*.png"):
          os.remove(image)
        remove(gif1, gif2)
        return
      gif = AnimatedGif('/root/discord/files/gif/1.gif')
      gif.process_image()
      if len(glob.glob("/root/discord/files/gif/*.png")) > 35 and ctx.message.author.id != "130070621034905600":
        await self.bot.say("Sorry, GIF has too many frames!")
        for image in glob.glob("/root/discord/files/gif/*.png"):
          os.remove(image)
        remove(gif_name, new_gif_name)
        return
      if liquid != None:
        gif.liquid()
      gif.construct_frames()
      await self.bot.send_file(ctx.message.channel, '/root/discord/files/gif/2.gif')
      remove(gif_name, new_gif_name)
    except Exception as e:
      await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  @commands.command(pass_context=True)
  async def rip(self, ctx, name:str, *, text:str=None):
    location = "/root/discord/files/rip.png"
    if text != None:
      url = "http://www.tombstonebuilder.com/generate.php?top1=R.I.P&top3={0}&top4={1}".format(name, text).replace(" ", "%20")
    else:
      url = "http://www.tombstonebuilder.com/generate.php?top1=R.I.P&top3={0}".format(name).replace(" ", "%20")
    html.escape(url)
    await download(url, location)
    await self.bot.send_file(ctx.message.channel, location)

  @commands.command(pass_context=True)
  async def urban(self, ctx, *, word:str):
    urb = urbandict.define(word)
    msg = "Word: {0}\n".format(word)
    msg += "Definition: {0}\n".format(urb[0]['def'].replace("\n", ""))
    msg += "Example: {0}".format(urb[0]['example'].replace("\n", ""))
    if len(msg) > 1999:
      await self.bot.say("Sorry, the definition is above discord text limit!")
      return
    await self.bot.say(cool.format(msg))

  @commands.command(pass_context=True, aliases=['im', 'photo', 'img'])
  async def image(self, ctx, *, text:str):
    i = 0
    while i < 5:
      try:
        global api_count
        if len(google_api) == api_count or len(google_api) < api_count:
          api_count = 0
        print("Image API Count: "+str(api_count))
        key = google_api[api_count]
        api_count += 1
        api = "https://www.googleapis.com/customsearch/v1?key={0}&cx=015418243597773804934:it6asz9vcss&searchType=image&q={1}".format(key, text)
        # api = "http://search.yacy.de/yacysearch.json?contentdom=image&query={0}".format(text)
        r = requests.get(api)
        response = r.json()
        response_dump = json.dumps(response)
        load = json.loads(response_dump)
        rand = random.choice(load['items'])
        image = rand['link']
        rand = str(random.randint(0, 100))
        if isimage(image):
          location = '/root/discord/files/image_{0}.png'.format(rand)
          await download(image, location)
          await self.bot.say("<{0}>".format(image))
          await self.bot.send_file(ctx.message.channel, location, filename='image.png')
          os.remove(location)
          i = 5
        else:
          await self.bot.say("Sorry, no image found!")
      except Exception as e:
        # await self.bot.say("Google's jewAPI has hit the quota or no image was found!\nTry again.")
        # print(type(e).__name__ + ': ' + str(e))
        i += 1
        continue

  @commands.command(pass_context=True, aliases=['youtube', 'video'])
  async def yt(self, ctx, *, text:str=None):
    try:
      global api_count
      if text == None:
        await self.bot.say("Error: Invalid Syntax\n`.yt/youtube <text>`")
        return
      if len(google_api) == api_count or len(google_api) < api_count:
        api_count = 0
      key = google_api[api_count]
      api_count += 1
      api = "https://www.googleapis.com/customsearch/v1?key={0}&cx=015418243597773804934:cdlwut5fxsk&q={1}".format(key, text)
      r = requests.get(api)
      response = r.json()
      response_dump = json.dumps(response)
      load = json.loads(response_dump)
      rand = load['items'][0]
      link = rand['link']
      title = rand['title']
      snippet = rand['snippet']
      msg = "Title: `{0}`\n".format(title)
      msg += "Description: `{0}`\n".format(snippet)
      msg += "Video: {0}".format(link)
      await self.bot.say(msg)
    except Exception as e:
      await self.bot.say("Google's jewAPI has hit the quota or no video was found!\nTry again.")

  @commands.command(pass_context=True)
  async def resize(self, ctx, size:int=None, url:str=None):
    try:
      if size == None:
        await self.bot.say("Error: Invalid Syntax\n`.resize <size:int> <image_url>`")
        return
      if size > 6:
        await self.bot.say("Sorry, size must be between `1-6`")
        return
      rand = str(random.randint(0, 500))
      x = await self.bot.say("ok, resizing `{0}` by `{1}`".format(url, str(size)))
      if isimage(url):
        location = '/root/discord/files/enlarge_{0}.png'.format(rand)
        await download(url, location)
      else:
        await self.bot.say("Invalid URL/Image!")
        return
      if os.path.getsize(location) > 3000000:
        await self.bot.say("Sorry, image too large for waifu2x servers!")
        return
      await self.bot.edit_message(x, "25%")
      with wand.image.Image(filename='/root/discord/files/enlarge_{0}.png'.format(rand)) as img:
        i = img.clone()
        i.resize(width=i.width*size, height=i.height*size)
        i.save(filename='/root/discord/files/kenlarge_{0}.png'.format(rand))
      await self.bot.edit_message(x, "50%")
      headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'}
      files = {'file': ('enlarge.png', open('/root/discord/files/kenlarge_{0}.png'.format(rand), 'rb'))}
      r = requests.post('http://waifu2x.udp.jp/api', files=files, headers=headers, stream=True)
      await self.bot.edit_message(x, "75%")
      location2 = "/root/discord/files/nenlarge_{0}.png".format(rand)
      f = open(location2, "wb")
      r.raw.decode_content = True
      shutil.copyfileobj(r.raw, f)
      f.close()
      if os.path.getsize(location2) > 5000000:
        await self.bot.say("Sorry, image too large for discord!")
        return
      await self.bot.edit_message(x, "100%, uploading")
      await self.bot.send_file(ctx.message.channel, location2)
      await self.bot.say("Visit image link for accurate resize visual.")
      await asyncio.sleep(3)
      await self.bot.delete_message(x)
      os.system("rm /root/discord/files/enlarge*")
      os.system("rm /root/discord/files/nenlarge*")
      os.system("rm /root/discord/files/kenlarge*")
    except wand.exceptions.CorruptImageError:
      await self.bot.say("Error: `Invalid/Corrupt Image`")
      return
    except Exception as e:
      await self.bot.say("Error: Failed\n `Discord Failed To Upload or Waifu2x Servers Failed`")
      print(type(e).__name__ + ': ' + str(e))

  @commands.group(pass_context=True, invoke_without_command=True)
  async def meme(self, ctx, meme:str=None, line1:str=None, *, line2:str=None):
    """Generates a meme."""
    if meme != None and "http" not in meme and "https" not in meme:
      rand = str(random.randint(0, 100))
      path = "/root/discord/files/meme_{0}.png".format(rand)
      link = "http://memegen.link/{0}/{1}/{2}.jpg".format(meme, line1, line2)
      await download(link, path)
      await self.bot.send_file(ctx.message.channel, path)
      os.remove(path)
    elif "http" in meme or "https" in meme:
      msg = copy.copy(ctx.message)
      msg.content = ".meme custom {0} {1} {2}".format(meme, line1, line2)
      await self.bot.process_commands(msg)
    elif meme.startswith("<@") or meme.startswith("<@!"):
      msg = copy.copy(ctx.message)
      msg.content = ".meme user {0} {1} {2}".format(meme, line1, line2)
      await self.bot.process_commands(msg)
    else:
      await self.bot.say("Error: Invalid Syntax\n`meme` has 4 parameters\n`.meme <template> <line_one> <line_two> <style>*`\n* = Optional")
      return

  @meme.command(name="custom",pass_context=True)
  async def _custom(self, ctx, pic:str, line1:str, *, line2:str):
    """Generates a meme using a custom picture."""
      rand = random.randint(0, 100)
      path = "/root/discord/files/meme_custom{0}.jpg".format(rand)
      link = "http://memegen.link/custom/{0}/{1}.jpg?alt={2}".format(line1, line2, pic)
      await download(link, path)
      await self.bot.send_file(ctx.message.channel, path)
      os.remove(path)

  @meme.command(name="user",pass_context=True)
  async def _user(self, ctx, user:discord.User, line1:str, *, line2:str=None):
    """Generates a meme on a users avatar."""
    if line2 == None:
      line2 = ""
    url = "http://memegen.link/custom/{0}/{1}.jpg?alt={2}".format(line1, line2, user.avatar_url)
    path = "/root/discord/files/meme_user.jpg"
    await download(url, path)
    await self.bot.send_file(ctx.message.channel, path)

  @meme.group(name="templates", pass_context=True, invoke_without_command=True)
  async def _templates(self, ctx):
    await self.bot.say("Templates to choose from: <{0}>".format("http://memegen.link/templates/"))

  @commands.command(aliases=['r'])
  async def reverse(self, *, text:str):
    """Reverse Text\n.revese <text>"""
    msg = u"\u202E"
    msg += text.replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
    await self.bot.say(msg)

  @commands.command(pass_context=True, aliases=['identify', 'captcha', 'whatis'])
  async def i(self, ctx, *, url:str):
    """Identify an image/gif using Microsofts Captionbot API"""
    # await self.bot.say("ok, processing\n`{0}`".format(url))
    r = requests.post("https://www.captionbot.ai/api/message", json={"conversationId":"C6WnqkItfYh","waterMark":"","userMessage":url}).text
    msg = '`{0}`'.format(json.loads(json.loads(r))["UserMessage"])
    await self.bot.say(msg)

  @commands.command(pass_context=True, aliases=['discordemoticon', 'emoji', 'emoticon', 'emote'])
  async def e(self, ctx, *, emote:str):
    """Attempt to find a twitch emoticon and display in Discord"""
    try:
      path = "/root/discord/files/ammo.json"
      with open(path, 'r') as f:
       data = json.load(f)
      k = data[emote]['mention'].split(">1")
      if len(k) > 1:
        s = k[0]+">"
      else:
        s = k[0]
      em = s.replace("<<", "<")
      msg = em
      await self.bot.say(msg)
    except:
      await self.bot.say("Emote not found")

  @commands.command(pass_context=True)
  async def merge(self, ctx, url:str, url2:str):
    """Merge/Combine Two Photos"""
    if len(ctx.message.mentions) >= 1:
      user = ctx.message.mentions[0]
      if len(ctx.message.mentions) == 1:
        user2 = ctx.message.mentions[0]
      else:
        user2 = ctx.message.mentions[1]
      if user.avatar == None:
        await self.bot.say(":no_entry: Mentioned User 1 Has No Avatar")
        return
      if user2.avatar == None:
        await self.bot.say(":no_entry: Mentioned User 2 Has No Avatar")
        return
      await self.bot.say("ok, processing")
      avatar = "https://cdn.discordapp.com/avatars/{0}/{1}.jpg".format(user.id, user.avatar)
      avatar2 = "https://cdn.discordapp.com/avatars/{0}/{1}.jpg".format(user2.id, user2.avatar)
      rand = str(random.randint(0, 100))
      path = "/root/discord/files/merge_user_{0}.png".format(rand)
      path2 = "/root/discord/files/merge_user2_{0}.png".format(rand)
      await download(avatar, path)
      await download(avatar2, path2)
      if os.path.getsize(path) == 127:
        await self.bot.say(":no_entry: Mentioned User 1's Avatar is Corrupt on Discord Servers!")
        return
      elif os.path.getsize(path2) == 127:
        await self.bot.say(":no_entry: Mentioned User 2's Avatar is Corrupt on Discord Servers!")
        return
      list_im = [path, path2]
      imgs    = [PIL.Image.open(i) for i in list_im]
      min_shape = sorted( [(np.sum(i.size), i.size ) for i in imgs])[0][1]
      imgs_comb = np.hstack( (np.asarray( i.resize(min_shape) ) for i in imgs ) )
      imgs_comb = PIL.Image.fromarray(imgs_comb)
      new_p = '/root/discord/files/nmerge_{0}.png'.format(rand)
      imgs_comb.save(new_p)
      await self.bot.send_file(ctx.message.channel, new_p, filename='merge_user.png')
      os.remove(path)
      os.remove(path2)
      os.remove(new_p)
      return
    if isimage(url) == False:
      await self.bot.say("Invalid or Non-Image!")
      return
    elif isimage(url2) == False:
      await self.bot.say("Invalid or Non-Image!")
      return
    await self.bot.say("ok, processing")
    rand = str(random.randint(0, 100))
    path = '/root/discord/files/merge_{0}.png'.format(rand)
    path2 = '/root/discord/files/merge2_{0}.png'.format(rand)
    await download(url, path)
    await download(url2, path2)
    list_im = [path, path2]
    imgs    = [PIL.Image.open(i) for i in list_im]
    min_shape = sorted( [(np.sum(i.size), i.size ) for i in imgs])[0][1]
    imgs_comb = np.hstack( (np.asarray( i.resize(min_shape) ) for i in imgs ) )
    imgs_comb = PIL.Image.fromarray(imgs_comb)
    new_p = '/root/discord/files/nmerge_{0}.png'.format(rand)
    imgs_comb.save(new_p)
    await self.bot.send_file(ctx.message.channel, new_p, filename='merge.png')
    os.remove(path)
    os.remove(path2)
    os.remove(new_p)

  emoji_map = {
    "a": "🅰", "b": "🅱", "c": "©", "d": "↩", "e": "📧", "f": "🎏", "g": "⛽",
    "h": "♓", "i": "ℹ", "j": "🌶" or "🗾", "k": "🎋", "l": "👢", "m": "Ⓜ",
    "n": "♑", "o": "⭕" or "🔅", "p": "🅿", "q": "📯", "r": "®", "s": "💲" or "⚡",
    "t": "🌴", "u": "⛎", "v": "🖖" or "♈", "w": "〰" or "📈", "x": "❌" or "⚔", "y": "✌",
    "z": "Ⓩ", "1": "1⃣", "2": "2⃣", "3": "3⃣", "4": "4⃣", "5": "5⃣",
    "6": "6⃣", "7": "7⃣", "8": "8⃣", "9": "9⃣", "0": "0⃣", "$": "💲", "!": "❗", "?": "❓", " ": "　"
  }
  @commands.command(pass_context=True, aliases=['cancerify', 'em'])
  async def emojify(self, ctx, *, txt:str):
    txt = txt.lower()
    msg = ""
    for s in txt:
      if s in self.emoji_map:
        msg += "{0}".format(self.emoji_map[s])
      else:
        msg += s
    await self.bot.say(msg)

  @commands.command(pass_context=True, aliases=['toe', 'analyze'])
  async def tone(self, ctx, *, text:str):
    """Analyze Tone in Text"""
    payload = {'text':text}
    headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:46.0) Gecko/20100101 Firefox/46.0.2 Waterfox/46.0.2'}
    r = requests.post('https://tone-analyzer-demo.mybluemix.net/api/tone', data=payload, headers=headers)
    load = r.json()
    anger = load['document_tone']['tone_categories'][0]['tones'][0]['score']
    disgust = load['document_tone']['tone_categories'][0]['tones'][1]['score']
    fear = load['document_tone']['tone_categories'][0]['tones'][2]['score']
    joy = load['document_tone']['tone_categories'][0]['tones'][3]['score']
    sadness = load['document_tone']['tone_categories'][0]['tones'][4]['score']
    emotions_msg = "Anger: {0}\nDisgust: {1}\nFear: {2}\nJoy: {3}\nSadness: {4}".format(anger, disgust, fear, joy, sadness)
    analytical = load['document_tone']['tone_categories'][1]['tones'][0]['score']
    confident = load['document_tone']['tone_categories'][1]['tones'][1]['score']
    tentative = load['document_tone']['tone_categories'][1]['tones'][2]['score']
    language_msg = "Analytical: {0}\nConfidence: {1}\nTentitive: {2}".format(analytical, confident, tentative)
    openness = load['document_tone']['tone_categories'][2]['tones'][0]['score']
    conscientiousness = load['document_tone']['tone_categories'][2]['tones'][1]['score']
    extraversion = load['document_tone']['tone_categories'][2]['tones'][2]['score']
    agreeableness = load['document_tone']['tone_categories'][2]['tones'][3]['score']
    emotional_range = load['document_tone']['tone_categories'][2]['tones'][4]['score']
    social_msg = "Openness: {0}\nConscientiousness: {1}\nExtraversion (Stimulation): {2}\nAgreeableness: {3}\nEmotional Range: {4}".format(openness, conscientiousness, extraversion, agreeableness, emotional_range)
    await self.bot.say("\n**Emotions**"+code.format(emotions_msg)+"**Language Style**"+code.format(language_msg)+"**Social Tendencies**"+code.format(social_msg))

  @commands.command(pass_context=True, aliases=['text2img', 'texttoimage', 'text2image'])
  async def tti(self, ctx, *, txt:str):
    api = 'http://api.img4me.com/?font=arial&fcolor=FFFFFF&size=35&type=png&text={0}'.format(txt)
    path = '/root/discord/files/tti.png'
    r = requests.get(api)
    await download(r.text, path)
    await self.bot.send_file(ctx.message.channel, path)

  # @commands.command(pass_context=True, aliases=['needsmorejpeg', 'nmj', 'jpegify'])
  # async def jpeg(self, ctx, url:str):
  #   """Add more JPEG to an Image\nNeeds More JPEG!"""
  #   if len(ctx.message.mentions) != 0 and len(ctx.message.mentions) > 1:
  #     if "<@!" in url:
  #       u_id = url.replace("<@!", "").replace(">", "")
  #     else:
  #       u_id = url.replace("<@", "").replace(">", "")
  #     user = discord.Server.get_member(ctx.message.server, user_id=u_id)
  #     if user.avatar == None:
  #       await self.bot.say(":no_entry: Mentioned User 1 Has No Avatar")
  #       return
  #     avatar = '/root/discord/files/cache/{0}'.format(user.id)
  #     api = 'http://api.jpeg.li/v1/upload'
  #     path = '/root/discord/files/jpeg.jpg'
  #     files = {'file': ('avatar.jpg', open(avatar, 'rb'))}
  #     r = requests.post(api, files=files, stream=True)
  #     await download(r.json()['url'], path)
  #     await self.bot.send_file(ctx.message.channel, path)
  #   api = 'http://api.jpeg.li/v1/existing'
  #   path = '/root/discord/files/jpeg.jpg'
  #   payload = {'url':url}
  #   files = {'file': ('jpeg.jpg', open('/root/discord/files/jpeg.jpg', 'rb'))}
  #   r = requests.post(api, data=payload)
  #   load = r.json()
  #   await download(load['url'], path)
  #   api = 'http://api.jpeg.li/v1/upload'
  #   l = requests.post(api, files=files, stream=True)
  #   await download(l.json()['url'], path)
  #   files = {'file': ('jpeg.jpg', open(path, 'rb'))}
  #   x = requests.post(api, files=files, stream=True)
  #   await download(x.json()['url'], path)
  #   await self.bot.send_file(ctx.message.channel, path)

  #https://github.com/rickylqhan/macintoshplus
  @commands.command(pass_context=True, aliases=['vaporwave', 'vape', 'vapewave'])
  async def vw(self, ctx, url:str, *, txt:str=None):
    """Vaporwave an image!"""
    if isimage(url) == False:
      await self.bot.say("Invalid or Non-Image!")
      return
    if txt == None:
      txt = "vape wave"
    rand = str(random.randint(0, 100))
    path = '/root/discord/files/vapewave_image_{0}.png'.format(rand)
    await download(url, path)
    im = PIL.Image.open(path)
    k=0
    im = macintoshplus.insert_pic(random.choice(macintoshplus.pics), im, k=0, x=500, y=650)
    im = macintoshplus.insert_pic(random.choice(macintoshplus.pics), im, k=0, x=0, y=300)
    im = macintoshplus.insert_pic(random.choice(macintoshplus.pics), im, x=700, y=-100)
    im = macintoshplus.insert_pic(random.choice(macintoshplus.pics), im, x=0, y=650)
    im = macintoshplus.draw_text(txt, im, x=im.height/4, y=im.width/2, k=93/100)
    final_path = '/root/discord/files/vapewave_{0}.png'.format(rand)
    im.save(final_path)
    await self.bot.send_file(ctx.message.channel, final_path, filename='vapewave.png')

  # async def on_message(self, message):
  # if ("https" in message.content or "http" in message.content) and (".png" in message.content.lower() or ".gif" in message.content.lower() or ".jpg" in message.content.lower() or ".jpeg" in message.content.lower()):
  #   if message.author == bot.user:
  #     return
  #   image = re.findall("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", message.clean_content)
  #   print(image)
  #   if len(image) >= 1:
  #     image = image[0]
  #   else:
  #     return
  #   r = requests.post("https://www.captionbot.ai/api/message", json={"conversationId":"C6WnqkItfYh","waterMark":"","userMessage":image}).text
  #   await self.bot.send_message(message.channel, json.loads(json.loads(r))["UserMessage"])

def setup(bot):
    bot.add_cog(Fun(bot))

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
import linecache
import math
from io import BytesIO
from io import StringIO
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

with open(os.path.join(os.getenv('discord_path', '~/discord/'), "utils/config.json")) as f:
  config = json.load(f)

cool = "```xl\n{0}\n```"
code = "```py\n{0}\n```"
image_mimes = ['image/png', 'image/pjpeg', 'image/jpeg', 'image/x-icon']
google_api = []
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

async def bytes_download(link:str):
  with aiohttp.ClientSession() as session:
    async with session.get(link) as resp:
      data = await resp.read()
      b = BytesIO(data)
      b.seek(0)
      return b

def text_image(text_path, font_path=None):
  grayscale = 'L'
  with open(text_path) as text_file:
    lines = tuple(l.rstrip() for l in text_file.readlines())

  large_font = 20  # get better resolution with larger size
  font_path = font_path or os.path.join(os.getenv('files_path', 'files/'), 'cour.ttf')  # Courier New. works in windows. linux may need more explicit path
  try:
    font = PIL.ImageFont.truetype(font_path, size=large_font)
  except IOError:
    font = PIL.ImageFont.load_default()
    print('Could not use chosen font. Using default.')

  pt2px = lambda pt: int(round(pt * 96.0 / 72))  # convert points to pixels
  max_width_line = max(lines, key=lambda s: font.getsize(s)[0])
  test_string = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  max_height = pt2px(font.getsize(test_string)[1])
  max_width = pt2px(font.getsize(max_width_line)[0])
  height = max_height * len(lines)  # perfect or a little oversized
  width = int(round(max_width + 40))  # a little oversized
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
  path = '/tmp/iascii_{0}.png'.format(random.randint(0, 100))
  image.save(path)
  return path

def remove(old, new):
  subprocess.call(["rm", old])
  subprocess.call(["rm", new])

class Fun():
  def __init__(self, bot):
    self.bot = bot
    self.discord_path = bot.path.discord
    self.files_path = bot.path.files

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
    headers = {'Authorization': 'token '}
    async with aiohttp.post('https://api.github.com/gists', data=json.dumps(gist), headers=headers) as gh:
      if gh.status != 201:
        await self.bot.say('Could not create gist.')
      else:
        js = await gh.json()
        await self.bot.say('Uploaded to gist, URL: <{0[html_url]}>'.format(js))

  @commands.command(pass_context=True)
  async def kys(self, ctx, *, user:str):
    """rope"""
    user = user.replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere').strip("`")
    if len(ctx.message.mentions) != 0:
      user = ctx.message.mentions[0].name
    msg = "``` _________     \n|         |    \n|         0 <-- {0}    \n|        /|\\  \n|        / \\  \n|              \n|              \n```\n".format(user)
    msg += "**** ``" + str(user) + "``\n"    
    await self.bot.say(msg)

  @commands.command(pass_context=True, aliases=['go', 'googl', 'gogle'])
  async def google(self, ctx, *, text:str=None):
    i = 0
    f = True
    while i < 10:
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
        try:
          if load['error']:
            continue
        except KeyError:
          pass
        rand = load['items'][0]
        result = rand['link']
        title = rand['title']
        snippet = rand['snippet']
        await self.bot.say("**{0}**\n`{1}`\n{2}".format(title, snippet, result))
        i = 10
        f = False
      except Exception as e:
        i += 1
        continue
    if f and i == 10:
      await self.bot.say(":warning: `API Quota Reached`")

  @commands.command(pass_context=True)
  async def suicide(self, ctx, *, user:str, direct=None):
    """make dank meme"""
    if len(user) > 25:
      await self.bot.say("ur names 2 long asshole")
      return
    if len(ctx.message.mentions) != 0 and len(ctx.message.mentions) == 1:
      user = ctx.message.mentions[0].name
    post_data = {'template_id': '57570410', 'username': '', 'password' : '', 'text0' : '', 'text1' : '{0}'.format(user)}
    r = requests.post("https://api.imgflip.com/caption_image", data=post_data)
    response = r.json()
    response_dump = json.dumps(response)
    load = json.loads(response_dump)
    url = load['data']['url']
    if direct:
      await self.bot.say(url)
    else:
      b = await bytes_download(url)
      await self.bot.send_file(ctx.message.channel, b, filename='suicide.png')

  @commands.command(pass_context=True)
  async def badmeme(self, ctx, direct=None):
    """returns bad meme (shit api)"""
    r = requests.get("https://api.imgflip.com/get_memes")
    response = r.json()
    response_dump = json.dumps(response)
    load = json.loads(response_dump)
    url = load['data']['memes'][random.randint(0, 100)]['url']
    if direct:
      await self.bot.say(url)
    else:
      b = await bytes_download(url)
      await self.bot.send_file(ctx.message.channel, b)

  @commands.command(pass_context=True, aliases=['imagemagic', 'imagemagick', 'magic', 'magick'])
  async def magik(self, ctx, *urls:str):
    """Apply magik to Image(s)\n .magik image_url or .magik image_url image_url_2"""
    try:
      if len(urls) == 0 and len(ctx.message.attachments) == 0:
        await self.bot.say(":no_entry: Please input url(s), mention(s) or atachment(s).")
        return
      xx = await self.bot.say("ok, processing")
      img_urls = []
      scale = None
      content_msg = ''
      for attachment in ctx.message.attachments:
        img_urls.append(attachment['url'])
      if len(ctx.message.mentions) != 0:
        for mention in ctx.message.mentions:
          img_urls.append(mention.avatar_url)
      for url in urls:
        if url.startswith('<@'):
          continue
        try:
          if str(math.floor(float(url))).isdigit():
            scale = int(math.floor(float(url)))
            content_msg = '`Scale: {0}`\n'.format(scale)
            if scale > 5 and ctx.message.author.id != config['ownerid']:
              scale = 5
              content_msg = '`Scale: {0} (Limit: <= 5)`\n'.format(scale)
            continue
        except:
          pass
        if isimage(url) == False:
          if isgif(url):
            await self.bot.say(":warning: `magik` is for images, pleas use gmagik!")
          else:
            await self.bot.say('Invalid or Non-Image!')
          return
        img_urls.append(url)
      else:
        if len(img_urls) == 0:
          await self.bot.say(":no_entry: Please input url(s), mention(s) or atachment(s).")
          return
      yummy = []
      exif = {}
      count = 0
      for url in img_urls:
        b = await bytes_download(url)
        i = wand.image.Image(file=b, format='png').clone()
        exif.update({count:(k[5:], v) for k, v in i.metadata.items() if k.startswith('exif:')})
        count += 1
        i.transform(resize='800x800>')
        if scale == None:
          i.liquid_rescale(width=int(i.width*0.5), height=int(i.height*0.5), delta_x=1, rigidity=0)
          i.liquid_rescale(width=int(i.width*1.5), height=int(i.height*1.5), delta_x=2, rigidity=0)
        else:
          i.liquid_rescale(width=int(i.width*0.5), height=int(i.height*0.5), delta_x=1, rigidity=0)
          i.liquid_rescale(width=int(i.width*1.5), height=int(i.height*1.5), delta_x=scale, rigidity=0)
        i.resize(i.width, i.height)
        magikd = BytesIO()
        i.save(file=magikd)
        magikd.seek(0)
        yummy.append(magikd)
      if len(yummy) > 1:
        imgs = [PIL.Image.open(i).convert('RGBA') for i in yummy]
        min_shape = sorted([(np.sum(i.size), i.size) for i in imgs])[0][1]
        imgs_comb = np.hstack((np.asarray(i.resize(min_shape)) for i in imgs))
        imgs_comb = PIL.Image.fromarray(imgs_comb)
        ya = BytesIO()
        imgs_comb.save(ya, 'png')
      else:
        ya = yummy[0]
      for x in exif:
        if len(exif[x]) >= 2000:
          continue
        content_msg += '**Exif data for image #{0}**\n'.format(str(x+1))+code.format(exif[x])
      else:
        if len(content_msg) == 0:
          content_msg = None
      ya.seek(0)
      await self.bot.send_file(ctx.message.channel, ya, filename='magik.png', content=content_msg)
      await self.bot.delete_message(xx)
    except discord.errors.Forbidden:
      await self.bot.say(":warning: **I do not have permission to send files!**")

  @commands.command(pass_context=True)
  async def gmagik(self, ctx, url:str=None, framerate:str=None):
    # await self.bot.say("Gmagik Libraries lost in bot wipe (*accident*)\nGmagik will be back in the next day or two, thanks\n-NotSoSuper")
    # return
    if url == None:
      await self.bot.say("Error: Invalid Syntax\n`.gmagik <gif_url> <frame_rate>*`\n`* = Optional`")
      return
    gif_url = url
    gif_dir = self.files_path('gif/')
    if len(glob.glob(gif_dir+"*")) > 0:
      os.system("rm {0}*".format(gif_dir))
    if isgif(gif_url) == False:
      await self.bot.say("Invalid or Non-GIF!")
      return
    x = await self.bot.say("ok, processing")
    rand = str(random.randint(0, 100))
    gifin = gif_dir+'1_{0}.gif'.format(rand)
    gifout = gif_dir+'2_{0}.gif'.format(rand)
    gifout_dir = self.files_path('gif')
    await download(url, gifin)
    if os.path.getsize(gifin) > 3000000 and ctx.message.author.id != "130070621034905600":
      await self.bot.say("Sorry, GIF Too Large!")
      for image in glob.glob(gif_dir+"*.png"):
        os.remove(image)
      remove(gifin, gifout)
      return
    def ef(gif, out):
      frame = PIL.Image.open(gif)
      nframes = 0
      while frame:
        frame.save('%s/%s.png' % (out, nframes), 'GIF')
        nframes += 1
        try:
          frame.seek(nframes)
        except EOFError:
          break
      return True
    ef(gifin, gifout_dir)
    if len(glob.glob(gif_dir+"*.png")) > 50 and ctx.message.author.id != "130070621034905600":
      await self.bot.say("Sorry, GIF has too many frames!")
      for image in glob.glob(gif_dir+"*.png"):
        os.remove(image)
      remove(gifin, gifout)
      return
    for image in glob.glob(gif_dir+"*.png"):
      im = wand.image.Image(filename=image)
      i = im.clone()
      i.transform(resize='800x800>')
      i.liquid_rescale(width=int(i.width*0.5), height=int(i.height*0.5), delta_x=1, rigidity=0)
      i.liquid_rescale(width=int(i.width*1.5), height=int(i.height*1.5), delta_x=2, rigidity=0)
      i.resize(i.width, i.height)
      i.save(filename=image)
    if framerate != None:
      subprocess.call(["ffmpeg", "-y", "-i", gif_dir+"%d.png", "-r", "{0}".format(framerate), gifout])
    else:
      subprocess.call(["ffmpeg", "-y", "-i", gif_dir+"%d.png", gifout])
    await self.bot.send_file(ctx.message.channel, gifout, filename='gmagik.gif')
    for image in glob.glob(gif_dir+"*.png"):
      os.remove(image)
    await self.bot.delete_message(x)
    remove(gifin, gifout)

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
      xx = await self.bot.say("ok, processing")
      b = await bytes_download(url)
      img = wand.image.Image(file=b)
      i = img.clone()
      font_path = self.files_path('impact.ttf')
      if size != None:
        color = wand.color.Color('{0}'.format(color))
        font = wand.font.Font(path=font_path, size=int(size), color=color)
      elif color != None:
        color = wand.color.Color('{0}'.format(color))
        font = wand.font.Font(path=font_path, size=40, color=color)
      else:
        color = wand.color.Color('red')
        font = wand.font.Font(path=font_path, size=40, color=color)
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
      final = BytesIO()
      i.save(file=final)
      final.seek(0)
      await self.bot.delete_message(xx)
      await self.bot.send_file(ctx.message.channel, final, filename='caption.png')
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
    path = self.files_path('triggered.png')
    img = wand.image.Image(filename=path)
    i = img.clone()
    color = wand.color.Color('red')
    font = wand.font.Font(path=self.files_path('impact.ttf'), size=40, color=color)
    text = "Sorry for triggering you {0}".format(user)
    i.caption(text, top=155, font=font, gravity='center')
    final = BytesIO()
    i.save(file=final)
    final.seek(0)
    await self.bot.send_file(ctx.message.channel, final, filename='triggered.png')

  #jesus christ dont look at this code
  @commands.command(pass_context=True)
  async def heil(self, ctx, kek:str=None, direct=None):
    """Who will you worship?\n .heil hitler/hydra/megatron (add text here for direct)"""
    files_path = self.files_path('')
    if kek == None and ctx.message.channel.id == "152162730244177920":
      await self.bot.say("**Sieg Heil!**\nhttps://mods.nyc/j/hitler")
    elif kek == None:
      await self.bot.send_file(ctx.message.channel, files_path+'hitler.jpg', content="**Sieg Heil!**")
    if direct is not None and kek == "hitler":
      await self.bot.say("**Sieg Heil!**\nhttps://mods.nyc/j/hitler")
    elif kek == "hitler":
      await self.bot.send_file(ctx.message.channel, files_path+'hitler.jpg', content="**Sieg Heil!**")
    if direct is not None and kek == "hydra":
      await self.bot.say("**Hail Hydra**\nhttps://mods.nyc/g/hydra")
    elif kek == "hydra":
      await self.bot.send_file(ctx.message.channel, files_path+'hydra.gif', content="**Hail Hydra**")
    if direct is not None and kek == "megatron":
      await self.bot.say("**All Hail Megatron**\nhttps://mods.nyc/j/megatron")
    elif kek == "megatron":
      await self.bot.send_file(ctx.message.channel, files_path+'megatron.jpg', content='**All Hail Megatron**')

  @commands.command(pass_context=True, aliases=['aes'])
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

  @commands.command(pass_context=True, aliases=['expand'])
  async def ascii(self, ctx, *, text:str):
    """Convert text into ASCII"""
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
    final = BytesIO()
    imgs.save(final, 'png')
    final.seek(0)
    idk = text
    if len(txt) > 2000:
      await self.gist(ctx, idk, txt)
    else:
      msg = "```fix\n"
      msg += txt
      msg += "```"
      await self.bot.say(msg)
    try:
      await self.bot.send_file(ctx.message.channel, final, filename='ascii.png')
      os.remove(path)
    except discord.errors.Forbidden:
      await self.bot.say("Forbidden, no file permissions.")
      os.remove(path)
      return
    except Exception as e:
      print(e)

  @commands.command(pass_context=True)
  async def iascii(self, ctx, url:str):
    if isimage(url) == False:
      await self.bot.say("Not a Image/Invalid URL!")
      return
    r = requests.get(url, stream=True)
    rand = str(random.randint(0, 100))
    txt_path = self.files_path('iascii_{0}.txt'.format(rand))
    mime = magic.from_buffer(next(r.iter_content(256)), mime=True).decode()
    x = await self.bot.say("ok, processing")
    if mime == "image/png":
      b = await bytes_download(url)
      location = self.files_path('iascii_jpg_{0}.jpg'.format(rand))
      with wand.image.Image(file=b, background=wand.color.Color('white')) as original:
        with original.convert('jpeg') as converted:
          converted.save(filename=location)
      os.system("jp2a {0} --output={1}".format(location, txt_path))
      image = text_image(txt_path)
    elif mime == "image/jpeg":
      location = self.files_path("iascii_{0}.jpg".format(rand))
      await download(url, location)
      os.system("jp2a {0} --output={1}".format(location, txt_path))
      image = text_image(txt_path)
    await self.bot.delete_message(x)
    await self.bot.send_file(ctx.message.channel, image, filename='iascii.jpg')
    os.remove(image)
    os.remove(location)
    os.remove(txt_path)

  @commands.command(pass_context=True)
  async def gascii(self, ctx, url:str=None, liquid=None):
    """Gif to ASCII"""
    try:
      if url == None:
        await self.bot.say("Error: Invalid Syntax\n`.gascii <gif_url> <liquid_rescale>*`\n`* = Optional`")
        return
      gif_url = url
      gif_name = self.files_path('gif/1.gif')
      new_gif_name = self.files_path('gif/2.gif')
      if isgif(url) == False:
        await self.bot.say("Invalid or Non-GIF!")
        return
      x = await self.bot.say("ok, processing")
      location = self.files_path('gif/1.gif')
      await download(url, location)
      if os.path.getsize(location) > 450000 and ctx.message.author.id != "130070621034905600":
        await self.bot.say("Sorry, GIF Too Large!")
        for image in glob.glob(self.files_path("gif/*.png")):
          os.remove(image)
        remove(gif_name, new_gif_name)
        return
      gif = AnimatedGif(location)
      gif.process_image()
      if len(glob.glob(self.files_path("gif/*.png"))) > 35 and ctx.message.author.id != "130070621034905600":
        await self.bot.say("Sorry, GIF has too many frames!")
        for image in glob.glob(self.files_path("gif/*.png")):
          os.remove(image)
        remove(gif_name, new_gif_name)
        return
      if liquid != None:
        gif.liquid()
      gif.construct_frames()
      await self.bot.delete_message(x)
      await self.bot.send_file(ctx.message.channel, new_gif_name)
      remove(gif_name, new_gif_name)
    except Exception as e:
      await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  @commands.command(pass_context=True)
  async def rip(self, ctx, name:str=None, *, text:str=None):
    if name == None:
      name = ctx.message.author.name
    if len(ctx.message.mentions) >= 1:
      name = ctx.message.mentions[0].name
    if text != None:
      if len(text) > 22:
        one = text[:22]
        two = text[22:]
        url = "http://www.tombstonebuilder.com/generate.php?top1=R.I.P&top3={0}&top4={1}&top5={2}".format(name, one, two).replace(" ", "%20")
      else:
        url = "http://www.tombstonebuilder.com/generate.php?top1=R.I.P&top3={0}&top4={1}".format(name, text).replace(" ", "%20")
    else:
      if name[-1].lower() != 's':
        name += "'s"
      url = "http://www.tombstonebuilder.com/generate.php?top1=R.I.P&top3={0}&top4=Hopes and Dreams".format(name).replace(" ", "%20")
    html.escape(url)
    b = await bytes_download(url)
    await self.bot.send_file(ctx.message.channel, b, filename='rip.png')

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
    f = True
    while i < 10:
      try:
        global api_count
        if len(google_api) == api_count or len(google_api) < api_count:
          api_count = 0
        key = google_api[api_count]
        api_count += 1
        api = "https://www.googleapis.com/customsearch/v1?key={0}&cx=015418243597773804934:it6asz9vcss&searchType=image&q={1}".format(key, text)
        r = requests.get(api)
        response = r.json()
        response_dump = json.dumps(response)
        load = json.loads(response_dump)
        try:
          if load['error']:
            continue
        except KeyError:
          pass
        if len(load) == 0:
          await self.bot.say(":warning: `No image found!`")
          return
        rand = random.choice(load['items'])
        image = rand['link']
        rand = str(random.randint(0, 100))
        if isimage(image) or isgif(image):
          b = await bytes_download(image)
          await self.bot.send_file(ctx.message.channel, b, filename='image.png', content="<{0}>".format(image))
          i = 10
          f = False
        else:
          await self.bot.say(":warning: `No image found!`")
          return
      except discord.errors.Forbidden:
        await self.bot.say("no send_file permission asshole")
        return
      except:
        i += 1
        continue
    if f and i == 10:
      await self.bot.say(":warning: `API Quota Reached or Invalid Search`")

  @commands.command(pass_context=True, aliases=['youtube', 'video'])
  async def yt(self, ctx, *, text:str=None):
    if text == None:
      await self.bot.say("Error: Invalid Syntax\n`.yt/youtube <text>`")
      return
    i = 0
    f = True
    while i < 10:
      try:
        global api_count
        if len(google_api) == api_count or len(google_api) < api_count:
          api_count = 0
        key = google_api[api_count]
        api_count += 1
        api = "https://www.googleapis.com/customsearch/v1?key={0}&cx=015418243597773804934:cdlwut5fxsk&q={1}".format(key, text)
        r = requests.get(api)
        response = r.json()
        response_dump = json.dumps(response)
        load = json.loads(response_dump)
        try:
          if load['error']:
            continue
        except KeyError:
          pass
        rand = load['items'][0]
        link = rand['link']
        title = rand['title']
        snippet = rand['snippet']
        await self.bot.say('**{0}**\n`{1}`\n{2}'.format(title, snippet, link))
        i = 10
        f = False
      except:
        i += 1
        continue
    if f and i == 10:
      await self.bot.say(":warning: `API Quota Reached`")

  @commands.command(pass_context=True, aliases=['re'])
  async def resize(self, ctx, size=None, url:str=None):
    try:
      try:
        if int(size) or float(size):
          pass
      except ValueError:
        s_url = url
        s_size = size
        size = s_url
        url = s_size
      if isimage(url) == False and isgif(url) == False:
        await self.bot.say("Invalid URL/Image!")
        return
      sigh = str(size).split('.')
      if len(sigh) == 1:
        size = int(size)
      else:
        size = float(size)
      if size == None:
        await self.bot.say("Error: Invalid Syntax\n`.resize <size:int> <image_url>`")
        return
      if size > 10:
        await self.bot.say("Sorry, size must be between `0-10`")
        return
      rand = str(random.randint(0, 500))
      x = await self.bot.say("ok, resizing `{0}` by `{1}`".format(url, str(size)))
      b = await bytes_download(url)
      if sys.getsizeof(b) > 3000000:
        await self.bot.say("Sorry, image too large for waifu2x servers!")
        return
      await self.bot.edit_message(x, "25%, resizing")
      headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'}
      files = {'file': ('enlarge.png', b)}
      payload = {'scale': size, 'style': 'art', 'noise': 3, 'file': ('enlarge.png', b)}
      await self.bot.edit_message(x, "50%, w2x")
      try:
        with aiohttp.Timeout(10):
          r = await aiohttp.post('http://waifu2x.me/convert', data=payload, headers=headers)
        # r = requests.post('http://waifu2x.me/convert', files=files, data=payload, headers=headers, stream=True)
        txt = await r.text()
        download_url = 'http://waifu2x.me/{0}'.format(txt)
        final = None
      except asyncio.TimeoutError:
        idk = []
        if size == 1:
          idk.append(2)
        if size == 2:
          idk.append(2)
        if size == 3:
          idk.append(1.6)
          idk.append(2)
        if size == 4:
          idk.append(2)
          idk.append(2)
        if size == 5:
          idk.append(1.6)
          idk.append(2)
          idk.append(2)
        if size == 6:
          idk.append(2)
          idk.append(2)
          idk.append(2)
        if size == 7:
          idk.append(2)
          idk.append(2)
          idk.append(2)
          idk.append(1.6)
        if size == 8:
          idk.append(2)
          idk.append(2)
          idk.append(2)
          idk.append(2)
        if size == 9:
          idk.append(2)
          idk.append(2)
          idk.append(2)
          idk.append(2)
          idk.append(1.6)
        if size == 10:
          idk.append(2)
          idk.append(2)
          idk.append(2)
          idk.append(2)
          idk.append(2)
        for s in idk:
          if s == 2:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'}
            files = {'file': ('enlarge.png', b)}
            payload = {'scale': 2, 'style': 'art', 'noise': 1}
            r = requests.post('http://waifu2x.udp.jp/api', files=files, data=payload, headers=headers, stream=True)
            location2 = self.files_path("nenlarge_{0}.png".format(rand))
            final = BytesIO()
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, final)
          elif s == 1.6:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'}
            files = {'file': ('enlarge.png', b)}
            payload = {'scale': 1.6, 'style': 'art', 'noise': 1}
            r = requests.post('http://waifu2x.udp.jp/api', files=files, data=payload, headers=headers, stream=True)
            final = BytesIO()
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, final)
          final.seek(0)
      if final == None:
        final = await bytes_download(download_url)
      if sys.getsizeof(final) > 8388608:
        await self.bot.say("Sorry, image too large for discord!")
        return
      await self.bot.edit_message(x, "100%, uploading")
      i = 0
      while sys.getsizeof(final) == 88 and i < 5:
       final = await bytes_download(download_url)
       await asyncio.sleep(0.3)
       if sys.getsizeof(final) != 0:
        i = 5
      else:
        i += 1
      await self.bot.send_file(ctx.message.channel, final, filename='enlarge.png', content='Visit image link for accurate resize visual.')
      await asyncio.sleep(3)
      await self.bot.delete_message(x)
    except Exception as e:
      await self.bot.say(code.format(e))
      await self.bot.say("Error: Failed\n `Discord Failed To Upload or Waifu2x Servers Failed`")

  @commands.group(pass_context=True, invoke_without_command=True)
  async def meme(self, ctx, meme:str=None, line1:str=None, *, line2:str=None):
    """Generates a meme."""
    if meme == None:
      await self.bot.say("Error: Invalid Syntax\n`meme` has 4 parameters\n`.meme <template> <line_one> <line_two> <style>*`\n* = Optional")
      return
    if line1 == None:
      await self.bot.say("Error: Invalid Syntax\n`meme` has 4 parameters\n`.meme <template> <line_one> <line_two> <style>*`\n* = Optional")
      return
    if line2 == None:
      line2 = ''
    if meme.startswith("http") == False:
      link = "http://memegen.link/{0}/{1}/{2}.jpg".format(meme, line1, line2)
      b = await bytes_download(link)
      await self.bot.send_file(ctx.message.channel, b, filename='meme_custom.png')
    elif meme.startswith("http"):
      msg = copy.copy(ctx.message)
      msg.content = ".meme custom {0} {1} {2}".format(meme, line1, line2)
      await self.bot.process_commands(msg)
    elif len(ctx.message.mentions) >= 1:
      link = "http://memegen.link/custom/{0}/{1}.jpg?alt={2}".format(line1, line2, ctx.message.mentions[0].avatar_url)
      b = await bytes_download(link)
      await self.bot.send_file(ctx.message.channel, b, filename='meme.png')

  @meme.command(name="custom",pass_context=True)
  async def _custom(self, ctx, pic:str, line1:str, *, line2:str=None):
    """Generates a meme using a custom picture."""
    if not ".gif" in pic[-5:]:
      if line2 == None:
        line2 = ""
      link = "http://memegen.link/custom/{0}/{1}.jpg?alt={2}".format(line1, line2, pic)
      b = await bytes_download(link)
      await self.bot.send_file(ctx.message.channel, b, filename='meme_custom.png')
    else:
      await self.bot.say("You can't use gifs for memes!")

  @meme.command(name="user",pass_context=True)
  async def _user(self, ctx, user:discord.User, line1:str, *, line2:str=None):
    """Generates a meme on a users avatar."""
    if line2 == None:
      line2 = ""
    i = "http://memegen.link/custom/{0}/{1}.jpg?alt={2}".format(line1, line2, user.avatar_url)
    b = await bytes_download(i)
    await self.bot.send_file(ctx.message.channel, b, filename='meme_user.png')

  @commands.command(aliases=['r'])
  async def reverse(self, *, text:str):
    """Reverse Text\n.revese <text>"""
    s = text.split()
    kek = ''
    for x in s:
      kek += u"\u202E " + x
    kek = kek.replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
    await self.bot.say(kek)

  emote_regex = re.compile(r"<:(.*):([0-9]+)>", re.IGNORECASE)
  @commands.command(pass_context=True, aliases=['emoji', 'hugemoji', 'hugeemoji'])
  async def e(self, ctx, *ems:str):
    """Returns a large emoji image"""
    try:
      if len(ems) == 1:
        em = ems[0]
        em = em.lower()
        em = em.encode("unicode_escape").decode()
        if "\\U000" in em and em.count("\\U000") == 1:
          em = em.replace("\\U000", '')
        elif em.count("\\U000") == 2:
          em = em.split("\\U000")
          em = '{0}-{1}'.format(em[1], em[2])
        else:
          em = em.replace("\\u", '')
        path = self.files_path('emoji/{0}.png'.format(em))
        if em == ':b1:':
          path = self.files_path('b1.png')
        if os.path.isfile(path) == False:
          match = self.emote_regex.match(ems[0])
          if match == None or len(match.groups()) == 0:
            await self.bot.say(":warning: `Emoji Invalid/Not Found`")
            return
          emote = 'https://cdn.discordapp.com/emojis/{0}.png'.format(str(match.group(2)))
          path = await bytes_download(emote)
          if sys.getsizeof(path) == 88:
            await self.bot.say(":warning: `Emoji Invalid/Not Found`")
            return
        await self.bot.send_file(ctx.message.channel, path, filename='emoji.png')
      else:
        list_imgs = []
        count = -1
        for em in ems:
          count += 1
          em = em.lower()
          em = em.encode("unicode_escape").decode()
          if "\\U000" in em and em.count("\\U000") == 1:
            em = em.replace("\\U000", '')
          elif em.count("\\U000") == 2:
            em = em.split("\\U000")
            em = '{0}-{1}'.format(em[1], em[2])
          else:
            em = em.replace("\\u", '')
          path = self.files_path('emoji/{0}.png'.format(em))
          if os.path.isfile(path) == False:
            match = self.emote_regex.match(ems[count])
            emote = 'https://cdn.discordapp.com/emojis/{0}.png'.format(str(match.group(2)))
            path = await bytes_download(emote)
            if sys.getsizeof(path) == 88:
              continue
          list_imgs.append(path)
        imgs = [PIL.Image.open(i).convert('RGBA') for i in list_imgs]
        min_shape = sorted([(np.sum(i.size), i.size) for i in imgs])[0][1]
        imgs_comb = np.hstack((np.asarray(i.resize(min_shape)) for i in imgs))
        imgs_comb = PIL.Image.fromarray(imgs_comb)
        png_info = imgs[0].info
        b = BytesIO()
        imgs_comb.save(b, 'png', **png_info)
        b.seek(0)
        try:
          await self.bot.send_file(ctx.message.channel, b, filename='merged_emotes.png')
        except:
          await self.bot.say('sorry, merged file 2 big (> 10 mb)')
    except Exception as e:
      await self.bot.say(code.format(e))

  @commands.command(pass_context=True, aliases=['steamemoji', 'steame'])
  async def se(self, ctx, em:str):
    """Returns a steam emoji image"""
    em = em.lower()
    url = "https://steamcommunity-a.akamaihd.net/economy/emoticon/{0}".format(em)
    if em == ':b1:':
      path = self.files_path('b1.png')
    else:
      b = await bytes_download(url)
    if not b:
      await self.bot.say(":warning: `Emoticon download failed`")
      return
    if sys.getsizeof(b) == 88:
      await self.bot.say(":warning: `Emoticon Not Found/Invalid`\n Remember to do :steam_emoticon:")
      return
    await self.bot.send_file(ctx.message.channel, b, filename='steam.png')

  @commands.command(pass_context=True)
  async def b1(self, ctx):
    """cool"""
    await self.bot.send_file(ctx.message.channel, self.files_path('b1.png'))

  @commands.command(pass_context=True)
  async def merge(self, ctx, *urls:str):
    """Merge/Combine Two Photos"""
    urls = [x for x in urls]
    count = 0
    for x in ctx.message.mentions:
      count += 1
      if x.avatar == None:
        await self.bot.say(":no_entry: Mentioned user {0} has no avatar".format(str(count)))
        return
      urls.append(x.avatar_url)
      urls.remove(x.mention)
    for x in ctx.message.attachments:
      urls.append(x['url'])
    count = 0
    for x in urls:
      count += 1
      if isimage(x) == False:
        await self.bot.say("Link {0} is Invalid or Non-Image!".format(str(count)))
        return
    xx = await self.bot.say("ok, processing")
    count = 0
    list_im = []
    for url in urls:
      count += 1
      b = await bytes_download(url)
      if sys.getsizeof(b) == 215:
        await self.bot.say(":no_entry: Mentioned user {0}'s avatar is corrupt on discord servers!".format(str(count)))
        return
      list_im.append(b)
    imgs = [PIL.Image.open(i).convert('RGBA') for i in list_im]
    min_shape = sorted([(np.sum(i.size), i.size) for i in imgs])[0][1]
    imgs_comb = np.hstack((np.asarray(i.resize(min_shape)) for i in imgs))
    imgs_comb = PIL.Image.fromarray(imgs_comb)
    final = BytesIO()
    imgs_comb.save(final, 'png')
    final.seek(0)
    await self.bot.delete_message(xx)
    await self.bot.send_file(ctx.message.channel, final, filename='merge.png')

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
    # load = tone_analyzer.tone(text=text)
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
    r = requests.get(api)
    b = await bytes_download(r.text)
    await self.bot.send_file(ctx.message.channel, b, filename='tti.png')

  @commands.command(pass_context=True, aliases=['needsmorejpeg', 'nmj', 'jpegify'])
  async def jpeg(self, ctx, url:str, amount:int=5):
    """Add more JPEG to an Image\nNeeds More JPEG!"""
    if url.startswith('<@') and len(ctx.message.mentions) != 0:
      url = ctx.message.mentions[0].avatar_url
    api = 'http://api.jpeg.li/v1/existing'
    for x in amount:
      payload = {
        'url': url
      }
      r = requests.post(api, data=payload)
      url = r.json()['url']
    b = await bytes_download(url)
    await self.bot.send_file(ctx.message.channel, b, filename='needsmorejpeg.jpg')

  @commands.command(pass_context=True, aliases=['vaporwave', 'vape', 'vapewave'])
  async def vw(self, ctx, url:str, *, txt:str=None):
    """Vaporwave an image!"""
    if isimage(url) == False:
      await self.bot.say("Invalid or Non-Image!")
      return
    if txt == None:
      txt = "vape wave"
    b = await bytes_download(url)
    im = PIL.Image.open(b)
    k = 0
    im = macintoshplus.insert_pic(random.choice(macintoshplus.pics), im, k=0, x=500, y=650)
    im = macintoshplus.insert_pic(random.choice(macintoshplus.pics), im, k=0, x=0, y=300)
    im = macintoshplus.insert_pic(random.choice(macintoshplus.pics), im, x=700, y=-100)
    im = macintoshplus.insert_pic(random.choice(macintoshplus.pics), im, x=0, y=650)
    im = macintoshplus.draw_text(txt, im, x=im.height/4, y=im.width/2, k=93/100)
    final = BytesIO()
    im.save(final, 'png')
    final.seek(0)
    await self.bot.send_file(ctx.message.channel, final, filename='vapewave.png')

  @commands.command(pass_context=True)
  async def jagroshisgay(self, ctx, *, txt:str):
    x = await self.bot.say(txt)
    txt = u"\u202E " + txt
    await self.bot.edit_message(x, txt)

  @commands.command(pass_context=True, aliases=['achievement', 'ach'])
  async def mc(self, ctx, *, txt:str):
    """Generate a Minecraft Achievement"""
    api = "https://mcgen.herokuapp.com/a.php?i=1&h=Achievement-{0}&t={1}".format(ctx.message.author.name, txt)
    b = await bytes_download(api)
    i = 0
    while sys.getsizeof(b) == 88 and i != 10:
      b = await bytes_download(api)
      if sys.getsizeof(b) != 0:
        i = 10
      else:
        i += 1
    if i == 10 and sys.getsizeof(b) == 88:
      await self.bot.say("Minecraft Achievement Generator API is bad, pls try again")
      return
    await self.bot.send_file(ctx.message.channel, b, filename='achievement.png')

  @commands.command(aliases=['cow'])
  async def cowsay(self, *, txt:str):
    msg = subprocess.check_output(["cowsay"], input = txt.encode("utf-8"))
    msg = msg.decode().replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
    await self.bot.say("```\n"+msg+"```")

  @commands.command(aliases=['dragon'])
  async def dragonsay(self, *, txt:str):
    msg = subprocess.check_output(["cowsay", '-f', 'dragon'], input = txt.encode("utf-8"))
    msg = msg.decode().replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
    await self.bot.say("```\n"+msg+"```")

  @commands.command(aliases=['sheep'])
  async def sheepsay(self, *, txt:str):
    msg = subprocess.check_output(["cowsay", '-f', 'sheep'], input = txt.encode("utf-8"))
    msg = msg.decode().replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
    await self.bot.say("```\n"+msg+"```")

  @commands.command(aliases=['dino'])
  async def dinosay(self, *, txt:str):
    msg = subprocess.check_output(["cowsay", '-f', 'stegosaurus'], input = txt.encode("utf-8"))
    msg = msg.decode().replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
    await self.bot.say("```\n"+msg+"```")

  @commands.command(aliases=['pony'])
  async def ponysay(self, *, txt:str):
    msg = subprocess.check_output(["cowsay", '-f', 'unipony-smaller'], input = txt.encode("utf-8"))
    msg = msg.decode().replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
    await self.bot.say("```\n"+msg+"```")

  @commands.command(aliases=['mech'])
  async def mechsay(self, *, txt:str):
    msg = subprocess.check_output(["cowsay", '-f', 'mech-and-cow'], input = txt.encode("utf-8"))
    msg = msg.decode().replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
    await self.bot.say("```\n"+msg+"```")

  @commands.command(aliases=['dragoncow', 'dragonandcow'])
  async def dragoncowsay(self, *, txt:str):
    msg = subprocess.check_output(["cowsay", '-f', 'dragon-and-cow'], input = txt.encode("utf-8"))
    msg = msg.decode().replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
    await self.bot.say("```\n"+msg+"```")

  # thanks RoadCrosser#3657
  @commands.group(pass_context=True, aliases=['eye'], invoke_without_command=True)
  async def eyes(self, ctx, url:str=None, eye:str=None, resize:str=None):
    try:
      if len(ctx.message.mentions) >= 1:
        url = ctx.message.mentions[0].avatar_url
      elif url == None and len(ctx.message.attachments) >= 1:
        url = ctx.message.attachments[0]['url']
      elif url == None:
        url = ctx.message.author.avatar_url
      try:
        if isimage(url) == False and isgif(url) == False:
          await self.bot.say("Invalid or Non-Image!")
          return
      except requests.exceptions.MissingSchema:
        await self.bot.say("bad url")
        return
      except Exception as e:
        await self.bot.say(e)
        return
      resize_amount = None
      monocle = False
      flipped = False
      flipped_count = 1
      if eye != None:
        eye = eye.lower()
      if eye == None or eye == 'default' or eye == '0':
        eye_location = self.files_path('eye.png')
      elif eye == 'spongebob' or eye == 'blue' or eye == '1':
        eye_location = self.files_path('spongebob_eye.png')
      elif eye == 'big' or eye == '2':
        eye_location = self.files_path('big_eye.png')
        resize_amount = 110
      elif eye == 'small' or eye == '3':
        eye_location = self.files_path('small_eye.png')
        resize_amount = 110
      elif eye == 'money' or eye == '4':
        eye_location = self.files_path('money_eye.png')
      elif eye == 'blood' or eye == 'bloodshot' or eye == '5':
        eye_location = self.files_path('bloodshot_eye.png')
        resize_amount = 200
      elif eye == 'red' or eye == '6':
        eye_location = self.files_path('red_eye.png')
        resize_amount = 200
      elif eye == 'meme' or eye == 'illuminati' or eye == 'triangle' or eye == '7':
        eye_location = self.files_path('illuminati_eye.png')
        resize_amount = 150
      elif eye == 'googly' or eye == 'googlyeye' or eye == 'plastic' or eye == '8':
        eye_location = self.files_path('googly_eye.png')
        resize_amount = 200
      elif eye == 'monocle' or eye == 'fancy' or eye == '9':
        eye_location = self.files_path('monocle_eye.png')
        resize_amount = 80
        monocle = True
      elif eye == 'flip' or eye == 'flipped' or eye == 'reverse' or eye == 'reversed' or eye == '10':
        eye_location = self.files_path('eye.png')
        eye_flipped_location = self.files_path('eye_flipped.png')
        flipped = True
      else:
        eye_location = self.files_path('eye.png')
      if resize_amount == None:
        resize_amount = 130
      try:
        if resize != None:
          sigh = str(resize).split('.')
          if len(sigh) == 1:
            resize = int(resize)
          else:
            resize = float(resize)
          if resize == 0:
            resize_amount = 120
          else:
            resize_amount = resize*100
      except ValueError:
        resize_amount = 120
      def posnum(num): 
        if num < 0 : 
          return - (num)
        else:
          return num
      def find_coeffs(pa, pb):
        matrix = []
        for p1, p2 in zip(pa, pb):
          matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0]*p1[0], -p2[0]*p1[1]])
          matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1]*p1[0], -p2[1]*p1[1]])
        A = np.matrix(matrix, dtype=np.float)
        B = np.array(pb).reshape(8)
        res = np.dot(np.linalg.inv(A.T*A)*A.T, B)
        return np.array(res).reshape(8)
      x = await self.bot.say("ok, processing")
      b = await bytes_download(url)
      img = PIL.Image.open(b).convert("RGBA")
      eyes = PIL.Image.open(eye_location).convert("RGBA")
      data = {"url": url}
      headers = {"Content-Type":"application/json","Ocp-Apim-Subscription-Key": ''}
      async with aiohttp.ClientSession() as session:
        async with session.post('https://api.projectoxford.ai/face/v1.0/detect?returnFaceId=false&returnFaceLandmarks=true&returnFaceAttributes=headPose', headers=headers, data=json.dumps(data)) as r:
          faces = await r.json()
      if "error" in faces:
        await self.bot.say(":warning: `Error occured in the API, could not process image url`")
        await self.bot.delete_message(x)
        return
      if len(faces) == 0:
        await self.bot.say(":no_entry: `Face not detected`")
        await self.bot.delete_message(x)
        return
      eye_list = []
      for f in faces:
        if monocle == True:
          eye_list += ([((f['faceLandmarks']['pupilRight']['x'],f['faceLandmarks']['pupilRight']['y']),f['faceRectangle']['height'],(f['faceAttributes']['headPose']))])
        else:
          eye_list += (((f['faceLandmarks']['pupilLeft']['x'],f['faceLandmarks']['pupilLeft']['y']),f['faceRectangle']['height'],(f['faceAttributes']['headPose'])),((f['faceLandmarks']['pupilRight']['x'],f['faceLandmarks']['pupilRight']['y']),f['faceRectangle']['height'],(f['faceAttributes']['headPose'])))
      for e in eye_list:
        width, height = eyes.size
        h = e[1]/resize_amount*50
        width = h/height*width
        if flipped:
          if (flipped_count % 2 == 0):
            s_image = wand.image.Image(filename=eye_flipped_location)
          else:
            s_image = wand.image.Image(filename=eye_location)
          flipped_count += 1
        else:
          s_image = wand.image.Image(filename=eye_location)
        i = s_image.clone()
        i.resize(int(width), int(h))
        s_image = BytesIO()
        i.save(file=s_image)
        s_image.seek(0)
        inst = PIL.Image.open(s_image)
        yaw = e[2]['yaw']
        pitch = e[2]['pitch']
        width, height = inst.size
        pyaw = int(yaw/180*height)
        ppitch = int(pitch/180*width)
        new = PIL.Image.new('RGBA', (width+posnum(ppitch)*2, height+posnum(pyaw)*2), (255, 255, 255, 0))
        new.paste(inst, (posnum(ppitch), posnum(pyaw)))
        width, height = new.size
        coeffs = find_coeffs([(0, 0), (width, 0), (width, height), (0, height)], [(ppitch, pyaw), (width-ppitch, -pyaw), (width+ppitch, height+pyaw), (-ppitch, height-pyaw)])
        inst = new.transform((width, height), PIL.Image.PERSPECTIVE, coeffs, PIL.Image.BICUBIC).rotate(-e[2]['roll'], expand=1, resample=PIL.Image.BILINEAR)
        eyel = PIL.Image.new('RGBA', img.size, (255, 255, 255, 0))
        width, height = inst.size
        if monocle:
          eyel.paste(inst, (int(e[0][0]-width/2), int(e[0][1]-height/3.7)))
        else:
          eyel.paste(inst, (int(e[0][0]-width/2), int(e[0][1]-height/2)))
        img = PIL.Image.alpha_composite(img, eyel)
      final = BytesIO()
      img.save(final, "png")
      final.seek(0)
      await self.bot.send_file(ctx.message.channel, final, filename="eyes.png")
      await self.bot.delete_message(x)
    except Exception as e:
      exc_type, exc_obj, tb = sys.exc_info()
      f = tb.tb_frame
      lineno = tb.tb_lineno
      filename = f.f_code.co_filename
      linecache.checkcache(filename)
      line = linecache.getline(filename, lineno, f.f_globals)
      await self.bot.say(code.format('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)))
      os.remove(location)
      os.remove(final_location)
      os.remove(s_image_loc)

  @eyes.command(name='list', pass_context=True, invoke_without_command=True)
  async def eyes_list(self, ctx):
    eyes = ['Default - 0', 'Spongebob - 1', 'Big - 2', 'Small - 3', 'Money - 4', 'Bloodshot - 5', 'Red - 6', 'Illuminati - 7', 'Googly - 8', 'Monocle - 9', 'Flipped - 10']
    thing = []
    for s in eyes:
      thing.append('`'+s+'`')
    await self.bot.say("In order to use, you must do `eyes image_url eye_type (name or number)`\n**Eye types**\n"+', '.join(thing))

  @commands.command(pass_context=True, aliases=['identify', 'captcha', 'whatis'])
  async def i(self, ctx, *, url:str):
    """Identify an image/gif using Microsofts Captionbot API"""
    r = requests.post("https://www.captionbot.ai/api/message", json={"conversationId":"","waterMark":"","userMessage":url})
    r = requests.get("https://www.captionbot.ai/api/message?waterMark=&conversationId=").json()
    msg = '`{0}`'.format(json.loads(r)['BotMessages'][-1])
    await self.bot.say(msg)

  @commands.command(pass_context=True, aliases=['mentionspam'])
  @checks.admin_or_perm(manage_server=True)
  async def ms(self, ctx, amount:int, id:str, channel:discord.Channel=None):
    if amount > 100:
      await self.bot.say("2 many mentions asshole")
      return
    try:
      await self.bot.delete_message(ctx.message)
    except:
      pass
    user = discord.Server.get_member(ctx.message.server, id)
    if user == None:
      await self.bot.say("invalid user id")
      return
    channels_readable = []
    for s in ctx.message.server.channels:
      if s.type == discord.ChannelType.voice:
        continue
      if user.permissions_in(s).read_messages and user.permissions_in(s).send_messages:
        channels_readable.append(s)
    count = 0
    for i in range(amount):
      if channel == None:
        for s in channels_readable:
          if count == amount:
            break
          x = await self.bot.send_message(s, '{0}'.format(user.mention))
          await self.bot.delete_message(x)
          count += 1
          await asyncio.sleep(0.21)
      else:
        x = await self.bot.send_message(channel, '{0}'.format(user.mention))
        await self.bot.delete_message(x)
        await asyncio.sleep(0.21)
    x = await self.bot.say('done')
    await asyncio.sleep(5)
    await self.bot.delete_message(x)

  # yeah, hardcoded paths for life on this one
  @commands.group(pass_context=True, invoke_without_command=True, aliases=['texttospeech', 'text2speech'])
  async def tts(self, ctx, *, txt:str):
    """Text to speech"""
    rand = random.randint(0, 99999)
    ogg_name = 'tts_{0}.ogg'.format(rand)
    path = '/var/www/vhosts/mods.nyc/bot.mods.nyc/ogg_files/{0}'.format(ogg_name)
    html = '<audio controls autoplay><source src="https://bot.mods.nyc/ogg_files/{0}" type="audio/ogg"></audio>'.format(ogg_name)
    html_file_name = 'tts_{0}.html'.format(rand)
    html_file = '/var/www/vhosts/mods.nyc/bot.mods.nyc/tts/{0}'.format(html_file_name)
    with open(html_file, 'wb') as f:
      f.write(html.encode())
      f.close()
    url_msg = 'https://bot.mods.nyc/tts/{0}'.format(html_file_name)
    url = 'https://text-to-speech-demo.mybluemix.net/api/synthesize?voice=en-US_AllisonVoice&text={0}&X-WDC-PL-OPT-OUT=1&download=true'.format(txt.replace(' ', '%20'))
    await download(url, path)
    await self.bot.say(url_msg)

  voice_list = ['`Allison - English/US (Expressive)`', '`Michael English/US`', '`Lisa English/US`', '`Kate English/UK`', '`Renee French/FR`', '`Birgit German/DE`', '`Dieter German/DE`', '`Francesca Italian/IT`', '`Emi Japanese/JP`', '`Isabela Portuguese/BR`', '`Enrique Spanish`', '`Laura Spanish`', '`Sofia Spanish/NA`']
  @tts.command(name='custom', pass_context=True, invoke_without_command=True, aliases=['texttospeech', 'text2speech'])
  async def tts_custom(self, ctx, voice:str, *, txt:str):
    """Text to speech"""
    voice = voice.lower()
    vv = None
    if voice == 'allison':
      vv = 'en-US_AllisonVoice'
    elif voice == 'michael':
      vv = 'en-US_MichaelVoice'
    elif voice == 'lisa':
      vv = 'en-US_LisaVoice'
    elif voice == 'kate':
      vv = 'en-GB_KateVoice'
    elif voice == 'renee':
      vv = 'fr-FR_ReneeVoice'
    elif voice == 'birgit':
      vv = 'de-DE_BirgitVoice'
    elif voice == 'dieter':
      vv = 'de-DE_DieterVoice'
    elif voice == 'francesca':
      vv = 'it-IT_FrancescaVoice'
    elif voice == 'emi':
      vv = 'ja-JP_EmiVoice'
    elif voice == 'isabela':
      vv = 'pt-BR_IsabelaVoice'
    elif voice == 'enrique':
      vv = 'es-ES_EnriqueVoice'
    elif voice == 'laura':
      vv = 'es-ES_LauraVoice'
    elif voice == 'sofia':
      vv = 'es-US_SofiaVoice'
    if vv == None:
      await self.bot.say("**Invalid Voice**\nHere's a list of voices you can use `format: tts custom <voice> <text>`\n"+', '.join(self.voice_list))
      return
    rand = random.randint(0, 99999)
    ogg_name = 'tts_{0}.ogg'.format(rand)
    path = '/var/www/vhosts/mods.nyc/bot.mods.nyc/ogg_files/{0}'.format(ogg_name)
    html = '<audio controls autoplay><source src="https://bot.mods.nyc/ogg_files/{0}" type="audio/ogg"></audio>'.format(ogg_name)
    html_file_name = 'tts_{0}.html'.format(rand)
    html_file = '/var/www/vhosts/mods.nyc/bot.mods.nyc/tts/{0}'.format(html_file_name)
    with open(html_file, 'wb') as f:
      f.write(html.encode())
      f.close()
    url_msg = 'https://bot.mods.nyc/tts/{0}'.format(html_file_name)
    url = 'https://text-to-speech-demo.mybluemix.net/api/synthesize?voice={1}&text={0}&X-WDC-PL-OPT-OUT=1&download=true'.format(txt.replace(' ', '%20'), vv)
    await download(url, path)
    await self.bot.say(url_msg)

  @tts.command(name='list', invoke_without_command=True)
  async def tts_list(self):
    await self.bot.say("**List of custom voices**\nFormat: `tts custom <voice> <text>`\n"+', '.join(self.voice_list))

  @commands.command(pass_context=True, aliases=['wm'])
  async def watermark(self, ctx, url:str, mark:str=None):
    if isimage(url) == False:
      await self.bot.say("Invalid or Non-Image!")
      return
    b = await bytes_download(url)
    if mark == 'brazzers' or mark == None:
      watermark_path = self.files_path('brazzers.png')
    else:
      if isimage(mark) == False:
        await self.bot.say("Invalid or Non-Image for Watermark!")
        return
      wmm = await bytes_download(mark)
    final = BytesIO()
    with wand.image.Image(filename=b) as img:
      with wand.image.Image(file=wmm) as wm:
        img.watermark(image=wm, left=int(img.width/15), top=int(img.height/10))
      img.save(file=final)
    final.seek(0)
    await self.bot.send_file(ctx.message.channel, final, filename='watermark.png')

def setup(bot):
  bot.add_cog(Fun(bot))
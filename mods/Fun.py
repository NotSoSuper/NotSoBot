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

cool = "```xl\n{0}\n```"
code = "```py\n{0}\n```"

PIXEL_ON = 0  # PIL color to use for "on"
PIXEL_OFF = 255  # PIL color to use for "off"

#https://stackoverflow.com/questions/29760402/converting-a-txt-file-to-an-image-in-python
def text_image(text_path, font_path=None):
    """Convert text file to a grayscale image with black characters on a white background.

    arguments:
    text_path - the content of this file will be converted to an image
    font_path - path to a font file (for example impact.ttf)
    """
    grayscale = 'L'
    # parse the file into lines
    with open(text_path) as text_file:  # can throw FileNotFoundError
        lines = tuple(l.rstrip() for l in text_file.readlines())

    # choose a font (you can see more detail in my library on github)
    large_font = 20  # get better resolution with larger size
    font_path = font_path or '/root/discord/files/cour.ttf'  # Courier New. works in windows. linux may need more explicit path
    try:
        font = PIL.ImageFont.truetype(font_path, size=large_font)
    except IOError:
        font = PIL.ImageFont.load_default()
        print('Could not use chosen font. Using default.')

    # make the background image based on the combination of font and lines
    pt2px = lambda pt: int(round(pt * 96.0 / 72))  # convert points to pixels
    max_width_line = max(lines, key=lambda s: font.getsize(s)[0])
    # max height is adjusted down because it's too large visually for spacing
    test_string = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    max_height = pt2px(font.getsize(test_string)[1])
    max_width = pt2px(font.getsize(max_width_line)[0])
    height = max_height * len(lines)  # perfect or a little oversized
    width = int(round(max_width + 40))  # a little oversized
    image = PIL.Image.new(grayscale, (width, height), color=PIXEL_OFF)
    draw = PIL.ImageDraw.Draw(image)

    # draw each line of text
    vertical_position = 5
    horizontal_position = 5
    line_spacing = int(round(max_height * 0.8))  # reduced spacing seems better
    for line in lines:
        draw.text((horizontal_position, vertical_position),
                  line, fill=PIXEL_ON, font=font)
        vertical_position += line_spacing
    # crop the text
    c_box = PIL.ImageOps.invert(image).getbbox()
    image = image.crop(c_box)
    return image

class Fun():
  def __init__(self,bot):
    self.bot = bot

  @commands.command(pass_context=True)
  async def kek(self, ctx, *, user):
    """rope"""
    if "@" not in str(user):
        msg = "**text** ``" + str(user) + "``\nhttps://example.org"
        msg2 = "``` _________     \n|         |    \n|         0 <-- {0}    \n|        /|\\  \n|        / \\  \n|              \n|              \n```".format(str(user))
    else:
        msg = "**text** " + str(user) + "\nhttps://example.org" 
        msg2 = "``` _________     \n|         |    \n|         0 <-- {0}   \n|        /|\\  \n|        / \\  \n|              \n|              \n```".format(str(user))
    await self.bot.say(msg2)
    await self.bot.say(msg)

  @commands.command(pass_context=True)
  async def google(self, *text):
    """Creates a google link"""
    if text == ():
        await self.bot.say("Ex: `.google noodles`")
        return
    text = "+".join(text)
    await self.bot.say("https://www.google.com/#q=" + text)

  @commands.command(pass_context=True)
  async def dmeme(self, ctx, *, name, direct=None):
    """make dank meme"""
    try:
        if len(name) > 25:
            await self.bot.say("ur names 2 long asshole")
            return
        post_data = {'template_id': '', 'username': '', 'password' : '', 'text0' : 'top text', 'text1' : '@{0} bottom text'.format(str(name))}
        r = requests.post("https://api.imgflip.com/caption_image", data=post_data)
        response = r.json()
        response_dump = json.dumps(response)
        load = json.loads(response_dump)
        url = load['data']['url']
        msg = load['data']['url']
        if direct == "true":
            await self.bot.say(str(msg))
        elif direct == ():
            print(url)
            req = urllib.request.Request(url, None, {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'})
            t = urllib.request.urlopen(req)
            file = open('/root/discord/files/test.jpg', 'wb')
            file.write(t.read())
            file.close()
            await self.bot.send_file(ctx.message.channel, file.name)
            os.remove(file.name)
        else:
            print(url)
            req = urllib.request.Request(url, None, {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'})
            t = urllib.request.urlopen(req)
            file = open('/root/discord/files/test.jpg', 'wb')
            file.write(t.read())
            file.close()
            await self.bot.send_file(ctx.message.channel, file.name)
            os.remove(file.name)
    except Exception as e:
        await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  @commands.command(pass_context=True)
  async def meme(self, ctx, direct=None):
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

  @commands.command(pass_context=True)
  async def magik(self, ctx, url, url2=None):
    """Apply magik to Image(s)\n .magik image_url or .magik image_url image_url_2"""
    try:
        print(url)
        extensions = ['.png', '.jpg', '.jpeg', '.JPG', '.PNG', '.JPEG']
        if any(x in url for x in extensions) and url2 is None:
            await self.bot.say("ok, applying magik")
            with aiohttp.ClientSession() as session:
                location = '/root/discord/files/magik.jpg'
                async with session.get(url) as resp:
                    data = await resp.read()
                    with open(location, "wb") as f:
                        f.write(data)
        elif url2 is not None and any(x in url2 for x in extensions):
            await self.bot.say("ok, applying magik")
            with aiohttp.ClientSession() as session:
                location = '/root/discord/files/magik.jpg'
                location2 = '/root/discord/files/magik2.jpg'
                async with session.get(url) as resp:
                    data = await resp.read()
                    with open(location, "wb") as f:
                        f.write(data)
                async with session.get(url2) as resp:
                    data = await resp.read()
                    with open(location2, "wb") as f:
                        f.write(data)
        else:
            await self.bot.say("Not an image!")
            return
        exif = {}
        image = wand.image.Image(filename='/root/discord/files/magik.jpg')
        exif.update((k[5:], v) for k, v in image.metadata.items()
            if k.startswith('exif:'))
        if url2 is not None:
            exif2 = {}
            image2 = wand.image.Image(filename='/root/discord/files/magik2.jpg')
            exif2.update((k[5:], v) for k, v in image2.metadata.items()
                if k.startswith('exif:'))
        img = wand.image.Image(filename='/root/discord/files/magik.jpg')
        print(img.size)
        i = img.clone()
        r = random.randint(1,4)
        if url2 is not None:
            with wand.image.Image(filename='/root/discord/files/magik2.jpg') as B:
                B.clone()
                B.liquid_rescale(width=int(B.width*0.5), height=int(B.height*0.5), delta_x=1, rigidity=0)
                B.liquid_rescale(width=int(B.width*1.5), height=int(B.height*1.5), delta_x=2, rigidity=0)

                with wand.image.Image(filename='/root/discord/files/magik.jpg') as A:
                    A.clone()
                    A.transform(resize='800x800>')
                    A.liquid_rescale(width=int(A.width*0.5), height=int(A.height*0.5), delta_x=1, rigidity=0)
                    A.liquid_rescale(width=int(A.width*1.5), height=int(A.height*1.5), delta_x=2, rigidity=0)
                    A.resize(A.width, A.height)
                    A.composite_channel('default_channels', A, 'over', 0, 0 )
                    A.composite_channel('default_channels', B, 'over', 0, 0 )
                    A.save(filename='/root/discord/files/magik_.png')                
        else:
            params = random.uniform(0.5, 2)
            i.transform(resize='800x800>')
            i.liquid_rescale(width=int(i.width*0.5), height=int(i.height*0.5), delta_x=1, rigidity=0)
            i.liquid_rescale(width=int(i.width*1.5), height=int(i.height*1.5), delta_x=2, rigidity=0)
            i.resize(i.width, i.height)
            # i.rotate(90 * r)
            # i.negate()
            i.save(filename='/root/discord/files/magik_.png')
        print(exif)
        if len(str(exif)) <= 2000 and url2 is None:
            await self.bot.say("Exif Data: ```{0}```".format(str(exif)))
        elif url2 is not None and len(str(exif)) <= 2000 and len(str(exif2)) <= 2000:
            await self.bot.say("Exif Data Image 1: ```{0}```".format(str(exif)))
            await self.bot.say("Exif Data Image 2: ```{0}```".format(str(exif2)))
        else:
            await self.bot.say("Exif Data too long, truncated")
        await self.bot.send_file(ctx.message.channel, '/root/discord/files/magik_.png')
    except Exception as e:
        await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  @commands.command(pass_context=True)
  async def caption(self, ctx, url, text:str, color=None, size=None):
    """Add caption to an image\n .caption text image_url"""
    try:
        print(url)
        extensions = ['.png', '.jpg', '.jpeg', '.JPG']
        if any(x in url for x in extensions):
            await self.bot.say("ok, processing")
            req = urllib.request.Request(url, None, {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'})
            t = urllib.request.urlopen(req)
            file = open('/root/discord/files/caption.jpg', 'wb')
            file.write(t.read())
            file.close()
        else:
            await self.bot.say("Not an image!")
            return
        image = wand.image.Image(filename='/root/discord/files/caption.jpg')
        img = wand.image.Image(filename=file.name)
        i = img.clone()
        if size != None:
            color = wand.color.Color('{0}'.format(color))
            font = wand.font.Font(path='files/impact.ttf', size=int(size), color=color)
        elif color != None:
            color = wand.color.Color('{0}'.format(color))
            font = wand.font.Font(path='/root/discord/files/impact.ttf', size=40, color=color)
        else:
            color = wand.color.Color('red')
            font = wand.font.Font(path='/root/discord/files/impact.ttf', size=40, color=color)

        i.caption(str(text), left=0, top=0, width=int(i.width/2), height=int(i.height/2),font=font, gravity='center')
        i.save(filename='/root/discord/files/caption_.png')
        await self.bot.send_file(ctx.message.channel, '/root/discord/files/caption_.png')
        os.remove('/root/discord/files/caption_.png')
    except Exception as e:
        await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  @commands.command(pass_context=True)
  async def heil(self, ctx, kek=None, direct=None):
    """Who will you worship?\n .heil hitler/hydra/megatron (add text here for direct)"""
    if kek == () and ctx.message.channel.id == "152162730244177920":
        await self.bot.say("**Sieg Heil!**\nhttps://mods.nyc/j/hitler")
    elif kek == ():
        await self.bot.send_file(ctx.message.channel, '/root/discord/files/hitler.jpg')

    if direct is not None and str(kek) == "hitler":
        await self.bot.say("**Sieg Heil!**\nhttps://mods.nyc/j/hitler")
    elif str(kek) == "hitler":
        await self.bot.send_file(ctx.message.channel, '/root/discord/files/hitler.jpg')
    
    if direct is not None and str(kek) == "hydra":
        await self.bot.say("**Hail Hydra**\nhttps://mods.nyc/g/hydra")
    elif str(kek) == "hydra":
        await self.bot.say("**Hail Hydra**")
        await self.bot.send_file(ctx.message.channel, '/root/discord/files/hydra.gif')

    if direct is not None and str(kek) == "megatron":
        await self.bot.say("**All Hail Megatron**\nhttps://mods.nyc/j/megatron")
    elif str(kek) == "megatron":
        await self.bot.send_file(ctx.message.channel, '/root/discord/files/megatron.jpg')

  @commands.command(pass_context=True)
  async def off(self, ctx, name):
    """turn off someone."""
    await self.bot.say("ok, tuned off {0}".format(str(name)))

  @commands.command(pass_context=True)
  async def aesthetics(self, ctx, *, text:str):
    """Returns inputed text in aesthetics"""
    msg = " ".join(text)
    await self.bot.say(msg)

  @commands.command(pass_context=True)
  async def iascii(self, ctx, url):
    try:
        extensions = ['.png', '.jpg', '.jpeg', '.JPG', '.PNG', '.JPEG']
        jextensions = ['.jpg', '.jpeg', '.JPG', '.JPEG']
        pextensions = ['.png', '.PNG']
        if any(x in url for x in extensions) == False:
            await self.bot.say("Not a Image/Invalid URL!")
            return
        if any(x in url for x in pextensions):
            await self.bot.say("ok, processing")
            location = "/root/discord/files/iascii.png"
            with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    data = await resp.read()
                    with open(location, "wb") as f:
                        f.write(data)
            with wand.image.Image(filename='/root/discord/files/iascii.png', background=wand.color.Color('white')) as original:
                with original.convert('jpeg') as converted:
                    converted.save(filename='/root/discord/files/iascii.jpg')
            os.system("jp2a /root/discord/files/iascii.jpg --output=/root/discord/files/iascii.txt")
            image = text_image('/root/discord/files/iascii.txt')
            image.save('/root/discord/files/iascii2.png')
            await self.bot.send_file(ctx.message.channel, "/root/discord/files/iascii2.png") 
        elif any(x in url for x in jextensions):
            await self.bot.say("ok, processing")
            location = "/root/discord/files/iascii.jpg"
            with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    data = await resp.read()
                    with open(location, "wb") as f:
                        f.write(data)
            os.system("jp2a /root/discord/files/iascii.jpg --output=/root/discord/files/iascii.txt")
            image = text_image('/root/discord/files/iascii.txt')
            image.save('/root/discord/files/iascii2.png')
            await self.bot.send_file(ctx.message.channel, "/root/discord/files/iascii2.png")
    except Exception as e:
        await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

def setup(bot):
    bot.add_cog(Fun(bot))
#! /usr/bin/env python

import sys
import os
import threading
import traceback
import re
import discord
import logging
import asyncio
import requests
import random
import aiohttp
import urllib.request
import json
import execjs
from sys import argv, path
from threading import Timer
from cleverbot import Cleverbot
from discord.ext import commands
from discord.enums import Status
from discord.message import Message
from discord.user import User
from discord.server import Server
from discord.client import Client
from random import choice
from re import sub
from lxml.html import fromstring

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

API_PAGE = 'http://api.4chan.org/{}/1.json'
URL = 'http://boards.4chan.org/{}/res/{}#p{}'

def format(element):
    '''Return the passed lxml.Element formatted in plain text.'''
    # i hate lxml

    formatted_element = list()

    text = [element.text, element.tail]

    if element.tag == 'br':
        text[0] = u'\n'

    text = filter(lambda x: x, text)

    text = u' '.join(text)

    formatted_element.append(text)

    for child in element:
        formatted_child = format(child)

        formatted_element.append(formatted_child)

    formatted_element = u' '.join(formatted_element)
    formatted_element = formatted_element.strip()
    formatted_element = sub(u' +', u' ', formatted_element)

    return formatted_element


def get_posts(board):
    '''Return all posts of the board's front page.'''
    url = API_PAGE.format(board)
    # url = 'http://api.4chan.org/b/1.json'

    response = requests.get(url)

    threads = response.json()
    threads = threads['threads']
    threads = map(lambda x: x['posts'], threads)

    parsed_posts = list()

    for thread in threads:
        op = thread[0]

        for post in thread:
            url = URL.format(board, op['no'], post['no'])

            try:
                content = post['com']
            except KeyError:
                content = ''
            else:
                content = fromstring(content)
                content = format(content)

            parsed_posts.append({
                'content': content,
                'url': url,
            })

    return parsed_posts


def get_discord_posts(board):
    '''All posts that are in discords chat limits'''
    posts = get_posts(board)

    posts = filter(lambda x: x['content'], posts)
    posts = filter(lambda x: len(x['content']) <= 1999, posts)

    return posts


def r_f_discord_post(board):
    '''Random formatted post that is within discord limits'''
    posts = get_discord_posts(board)
    posts = tuple(post['content'] for post in posts)

    post = choice(posts)
    return post

def restart_program():
    python = sys.executable
    os.execl(python, python, * sys.argv)

path.insert(0, '.')

description = '''idk'''
owner = "Your Discord UID"
bot = commands.Bot(command_prefix='.', description=description)
client = discord.Client()

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await bot.change_status(discord.Game(name="changeme"))

@bot.command()
async def chan():
    """Replies random 4chan post."""
    boards = ['b', 'pol', 'v', 's4s']
    post = r_f_discord_post(random.choice(boards))
    post = '{}'.format(post)
    await bot.say(post)

@bot.command(pass_context=True)
async def update(ctx):
    """Restart/Update Bot"""
    if ctx.message.author.id == owner:
        await bot.say("ok brb, updating")
        restart_program()

@bot.command(pass_context=True)
async def status(ctx, status):
    """Changes bots status"""
    if status != ():
        await bot.change_status(discord.Game(name="{0}".format(str(status))))
    name="".join(status)
    await bot.say("ok, status changed to ``" + name + "``")

@bot.command(pass_context=True)
async def kys(ctx, user):
    """rope"""
    if "@" not in str(user):
        msg = "**change me or remove** ``" + str(user) + "``\ntext"
        msg2 = "``` _________     \n|         |    \n|         0 <-- {0}    \n|        /|\\  \n|        / \\  \n|              \n|              \n```".format(str(user))
    else:
        msg = "**change me** " + str(user) + "\ntext" 
        msg2 = "``` _________     \n|         |    \n|         0 <-- {0}   \n|        /|\\  \n|        / \\  \n|              \n|              \n```".format(str(user))
    await bot.say(msg2)
    await bot.say(msg)

cleverbot_b = False
@bot.event
async def on_message(message):
    print(message.content.lower())
    cb = Cleverbot()
    if message.author == bot.user:
        return
    cb_channels = ['Channel ids you want cleverbot to reply in']
    one = ['Checks every message for text', 'example']
    two = ['change']
    three = ['me']
    # stops cleverbot ads from surfacing
    cb_ads = ['iOS', 'cleverbot', 'download', '.com', '.net', 'Android', 'angry', 'app', 'apps', 'Phone', 'pocket', 'SMS', 'Suprise']
    if replies_disabled == False:
        if any(x in message.content.lower() for x in one):
            msg = 'message to be said if a word in the filter is found {0} <-- mention the author of the person who said the word in the filter \n new line wooo'.format(message.author.mention)
            await bot.send_message(message.channel, msg)
        if any(x in message.content.lower() for x in two):
            msg = 'change me'
            await bot.send_message(message.channel, msg)
        if any(x in message.content.lower() for x in three) and 'if you want, stops specific words from triggering filter ex: ones that contain the filter word in another word such as cook and cookie' not in message.content.lower():
            msg = "change me"
            await bot.send_message(message.channel, msg)
    if cleverbot_b == True and any(x in message.channel.id for x in cb_channels):
        channel = discord.Object(id='{0}'.format(message.channel.id))
        msg = cb.ask(str(message))
        if any(x in msg for x in cb_ads):
            print("cleverbot ad, not responding")
        else:
            await bot.send_message(channel, msg)
    await bot.process_commands(message)

@bot.command(pass_context=True)
async def cb(ctx, option):
    """Enable/Disable Cleverbot"""
    global cleverbot_b
    cleverbot_b = False
    if ctx.message.author.id == owner and str(option) == "1":
        await bot.say("ok, enabled cleverbot")
        print("Cleverbot Enabled")
        cleverbot_b = True
    elif ctx.message.author.id == owner and str(option) == "0":
        await bot.say("ok, disabled cleverbot")
        print("Cleverbot Disabled")
        cleverbot_b = False
    else:
        await bot.say("bork, something went wrong")

@bot.command(pass_context=True)
async def say(ctx, text):
    """have me say something (owner only cuz exploits)???"""
    if ctx.message.author.id == owner:
        await bot.say(str(text))

@bot.command()
async def invite():
    """returns invite link for bot"""
    msg = 'Invite me to your server with this `url:` https://discordapp.com/oauth2/authorize?client_id=change to your bots clientid&scope=bot'
    await bot.say(msg)

replies_disabled = True #Disabled by default, this is the replies the filter would catch and respond in on_message
@bot.command(pass_context=True)
async def replies(ctx, command):
    """Enabled/Disabled replies"""
    global replies_disabled
    if ctx.message.author.id == owner and command == 'false':
        replies_disabled = True
        await bot.say("ok, disabled amazing replies")
    elif ctx.message.author.id == owner and command == 'true':
        replies_disabled = False
        await bot.say("ok, enabled amazing replies")

@bot.command(pass_context=True)
async def google(self, *text):
    """Creates a google link"""
    if text == ():
        await self.bot.say("Ex: `.google noodles`")
        return
    text = "+".join(text)
    await self.bot.say("https://www.google.com/#q=" + text)

@bot.command(pass_context=True, no_pm=True)
async def server(ctx):
    """server info"""
    server = ctx.message.server
    online = str(len([m.status for m in server.members if str(m.status) == "online" or str(m.status) == "idle"]))
    total = str(len(server.members))

    data = "```\n"
    data += "Name: {}\n".format(server.name)
    data += "ID: {}\n".format(server.id)
    data += "Region: {}\n".format(str(server.region))
    data += "Users: {}/{}\n".format(online, total)
    data += "Channels: {}\n".format(str(len(server.channels)))
    data += "Roles: {}\n".format(str(len(server.roles)))
    data += "Created: {}\n".format(str(server.created_at))
    data += "Owner: {}#{}\n".format(server.owner.name, server.owner.discriminator)
    data += "Icon: {}\n".format(server.icon_url)
    data += "```"
    await bot.say(data)

@bot.command(pass_context=True)
async def eval(self, code):
    """eval JS code in Node.JS"""
    # if str(runtime) == "js":
    #     execute = execjs.eval(str(code))
    #     await bot.say(execute)
    # elif str(runtime) == "node":
    #     node = execjs.get("Node")
    #     execute = node.eval(str(code))
    #     print("works")
    #     await bot.say(execute)
    # else:
    code_clean = "{0}".format(code.strip("```"))
    node = execjs.get("Node")
    execute = node.eval(str(code_clean))
    try:
        await bot.say(execute)
    except Exception as e: bot.say("```{0}".format(str(e)))

@bot.command(pass_context=True)
async def maymay(ctx, name, direct=None):
    """make dank meme \n .maymay name """
    if len(name) > 25:
        await bot.say("Your name is too long")
        return
    post_data = {'template_id': 'templete of the meme you want to caption', 'username': 'change me to imgflip username', 'password' : 'imgflip password', 'text0' : 'change me', 'text1' : '@{0} change me'.format(str(name))}
    r = requests.post("https://api.imgflip.com/caption_image", data=post_data)
    response = r.json()
    response_dump = json.dumps(response)
    load = json.loads(response_dump)
    url = load['data']['url']
    msg = load['data']['url']
    if direct == "true":
        await bot.say(str(msg))
    elif direct == ():
        print(url)
        req = urllib.request.Request(url, None, {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'})
        t = urllib.request.urlopen(req)
        file = open('maymay.jpg', 'wb')
        file.write(t.read())
        file.close()
        await bot.send_file(ctx.message.channel, file.name)
        os.remove(file.name)
    else:
        print(url)
        req = urllib.request.Request(url, None, {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'})
        t = urllib.request.urlopen(req)
        file = open('maymay.jpg', 'wb')
        file.write(t.read())
        file.close()
        await bot.send_file(ctx.message.channel, file.name)
        os.remove(file.name)

@bot.command(pass_context=True)
async def meme(ctx, direct=None):
    """returns bad meme (rlly bad api)"""
    r = requests.get("https://api.imgflip.com/get_memes")
    response = r.json()
    response_dump = json.dumps(response)
    load = json.loads(response_dump)
    url = load['data']['memes'][random.randint(0, 100)]['url']
    msg = load['data']['memes'][random.randint(0, 100)]['url']
    if direct == "true":
        await bot.say(str(msg))
    else:
        print(url)
        req = urllib.request.Request(url, None, {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'})
        t = urllib.request.urlopen(req)
        file = open('meme.jpg', 'wb')
        file.write(t.read())
        file.close()
        await bot.send_file(ctx.message.channel, file.name)
        os.remove(file.name)

bot.run('your bots token')

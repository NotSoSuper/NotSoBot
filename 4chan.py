#! /usr/bin/env python

import sys
import os
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
import time
import pymysql
from sys import argv, path
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
from utils import checks

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='/root/discord/files/discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

def restart_program():
    python = sys.executable
    os.execl(python, python, * sys.argv)

# --------------------------Bot Stuff Under Here--------------------------
path.insert(0, '.')

description = '''NotSoSuper\'s Super Duper Bot'''
owner = "130070621034905600"
bot = commands.Bot(command_prefix=commands.when_mentioned_or('.'), description=description, help_attrs={'name':"iamabadhelpcommand", 'enabled':False, 'hidden':True})
code = "```py\n{0}\n```"
cool = "```xl\n{0}\n```"
starttime = time.time()
starttime2 = time.ctime(int(time.time()))

if os.path.isfile("/root/discord/utils/blacklist.txt"):
    pass
else:
    with open("/root/discord/utils/blacklist.txt","a") as f:
        f.write("")

modules = [
    'mods.Moderation',
    'mods.Utils',
    'mods.Info',
    'mods.Fun',
    'mods.Chan'
]

@bot.event
async def on_ready():
    try:
        for cog in modules:
            try:
                bot.load_extension(cog)
            except Exception as e:
                print('Failed to load extension {}\n{}: {}'.format(cog, type(e).__name__, e))
        print('Logged in as')
        print(bot.user.name + "#" + bot.user.discriminator)
        print(bot.user.id)
        print('------')
        await bot.change_status(discord.Game(name=""))
    except Exception as e:
        print(type(e).__name__ + ': ' + str(e))

cleverbot_b = False
leaderboards = True
message_logging = True
blacklist_logging = True
command_logging = True
replies_disabled = True
say_errors_on_message = False

@bot.event
async def on_message(message):
    if message_logging == True:
        connection = pymysql.connect(host='',
                             user='',
                             password='',
                             db='',
                             charset='',
                             cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO `messages` (`server`, `time`, `channel`, `author`, `content`) VALUES (%s, %s, %s, %s, %s)"
                if message.channel.is_private:
                    cursor.execute(sql, ("Private Message", message.timestamp, "N/A", "{0} <{1}>".format(message.author.name, message.author.id) ,"{0}".format(message.content)))
                else:
                    cursor.execute(sql, (message.server.name, message.timestamp, message.channel.name, "{0} <{1}>".format(message.author.name, message.author.id) ,"{0}".format(message.content)))
            connection.commit()
        finally:
            connection.close()
    try:
        # print("({0}, #{1}) {2} <{3}>: {4}".format(message.server.name, message.channel.name, message.author.name, message.author.id, message.content))
        cb = Cleverbot()
        if message.author == bot.user:
            return
        cb_channels = ['150813303822614528', '173799905662337025', '161146445129318405', '175676162784100352'] #1. gmod, 4. flex
        kek = ['kek']
        amirite = ['amirite', 'am i right', 'right', 'right?', 'amiright']
        cb_ads = ['iOS', 'cleverbot', 'download', '.com', '.net', 'Android', 'angry', 'app', 'apps', 'Phone', 'pocket', 'SMS', 'Suprise']
        if replies_disabled == False:
            if any(x in message.content.lower() for x in kek) and '.kek' not in message.content.lower():
                msg = 'kek {0} *text* \nhttps://example.org\nhttps://example.org'.format(message.author.mention)
                await bot.send_message(message.channel, msg)
            if any(x in message.content.lower() for x in amirite):
                msg = 'ye you are right'
                await bot.send_message(message.channel, msg)
                await bot.send_message(message.channel, msg)
            if message.content.lower() == "change" and message.channel.id == "152162730244177920":
                await bot.send_message(message.channel, "**text**\nhttps://example.org")
            elif message.content.lower() == "cancer":
                await bot.send_message(message.channel, "**text**")
                await bot.send_file(message.channel, "/root/discord/cancer.gif")
        if cleverbot_b == True and any(x in message.channel.id for x in cb_channels):
            channel = discord.Object(id='{0}'.format(message.channel.id))
            msg = cb.ask(str(message))
            if any(x in msg for x in cb_ads):
                print("cleverbot ad, trying again")
                await bot.send_message(channel, msg)
            else:
                await bot.send_message(channel, msg)
        if random.randint(0, 1500) < 500:
            bot.send_typing(message.channel)
        if "<@" + message.author.id + ">" in open('/root/discord/utils/blacklist.txt').read() and message.channel.is_private == False:
            if blacklist_logging == True and message.channel.is_private == False:
                connection = pymysql.connect(host='',
                             user='',
                             password='',
                             db='',
                             charset='',
                             cursorclass=pymysql.cursors.DictCursor)
                try:
                    with connection.cursor() as cursor:
                        sql = "INSERT INTO `blacklist_log` (`server`, `user`, `time`) VALUES (%s, %s, %s)"
                        if message.channel.is_private:
                            cursor.execute(sql, ("Private Message", "{0} <{1}>".format(message.author.name, message.author.id), message.timestamp))
                        else:
                            cursor.execute(sql, ("{0} #{1}".format(message.server.name, message.channel.name),"{0} <{1}>".format(message.author.name, message.author.id), message.timestamp))
                    connection.commit()
                finally:
                    connection.close()
            return
        else:
            await bot.process_commands(message)
    except Exception as e:
        print(e)
        if say_errors_on_message == True:
            if message.channel.is_private:
                await bot.send_message(message.author, code.format(type(e).__name__ + ': ' + str(e)))
            else:
                await bot.send_message(message.channel, code.format(type(e).__name__ + ': ' + str(e)))

@bot.event
async def on_command(command, ctx):
    if command_logging == True:
        connection = pymysql.connect(host='',
                             user='',
                             password='',
                             db='',
                             charset='',
                             cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO `command_logs` (`server`, `time`, `channel`, `author`, `command`, `message`) VALUES (%s, %s, %s, %s, %s, %s)"
                if ctx.message.channel.is_private:
                    cursor.execute(sql, ("Private Message", ctx.message.timestamp, "N/A", "{0} <{1}>".format(ctx.message.author.name, ctx.message.author.id), ctx.invoked_with, ctx.message.content))
                else:
                    cursor.execute(sql, (ctx.message.server.name, ctx.message.timestamp, ctx.message.channel.name, "{0} <{1}>".format(ctx.message.author.name, ctx.message.author.id), ctx.invoked_with, ctx.message.content))
            connection.commit()
        finally:
            connection.close()
    try:
        msg = "User: {0} <{1}>\n".format(ctx.message.author, ctx.message.author.id).replace("'", "")
        msg += "Time: {0}\n".format(ctx.message.timestamp)
        msg += "Command: {0}\n".format(ctx.invoked_with)
        if ctx.message.channel.is_private:
            msg += "Server: Private Message\n"
        else:
            msg += "Server: {0}\n".format(ctx.message.server.name).replace("'", "")
            msg += "Channel: {0}\n".format(ctx.message.channel.name).replace("'", "")
        msg += "Context Message: {0}".format(ctx.message.content).replace("'", "")
        target = discord.Object(id='176568820452950016')
        await bot.send_message(target, cool.format(msg))
        if ctx.message.channel.is_private == False and ctx.message.server.name == "name" and ctx.channel.name != "test":
            await asyncio.sleep(120)
            async for message in bot.logs_from(ctx.message.channel, limit=50):
                if message.author == bot.user:
                    await asyncio.ensure_future(bot.delete_message(message))
                    await asyncio.sleep(0.4)
    except Exception as e:
        print(e)

@bot.event
async def on_command_error(exception, ctx):
    if isinstance(exception, commands.CommandNotFound):
        await bot.send_message(ctx.message.channel, "Error: Command `{0}` Not Found!".format(ctx.invoked_with))

class Default():
    def __init__(self, bot):
        self.bot = bot
    @commands.command(pass_context=True)
    @checks.is_owner()
    async def cb(self, ctx):
        """Enable/Disable Cleverbot"""
        global cleverbot_b
        if cleverbot_b == False:
            await self.bot.say("ok, enabled cleverbot")
            print("Cleverbot Enabled")
            cleverbot_b = True
        elif cleverbot_b == True:
            await self.bot.say("ok, disabled cleverbot")
            print("Cleverbot Disabled")
            cleverbot_b = False
        else:
            await self.bot.say("bork @NotSoSuper")

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def replies(self, ctx):
        """Disabled meme replies"""
        global replies_disabled
        if replies_disabled == False:
            replies_disabled = True
            await self.bot.say("ok, disabled amazing meme replies")
        elif replies_disabled == True:
            replies_disabled = False
            await self.bot.say("ok, enabled amazing meme replies")

@bot.command()
@checks.is_owner()
async def load(*,module:str):
    module = "mods." + module
    if module in modules:
        msg = await bot.say("ok, loading `{0}`".format(module))
        bot.load_extension(module)
        await bot.edit_message(msg, "ok, loaded `{0}`".format(module))
    else:
        await bot.say("You can't load {0}, it doesn't exist!".format(module))

@bot.command()
@checks.is_owner()
async def unload(*,module:str):
    module = "mods." + module
    if module in modules:
        msg = await bot.say("ok, unloading `{0}`".format(module))
        bot.unload_extension(module)
        await bot.edit_message(msg, "ok, unloaded `{0}`".format(module))
    else:
        await bot.say("You can't unload `{0}`, it doesn't exist!".format(module))

@bot.command()
@checks.is_owner()
async def reload(*,module:str):
    mod = "mods." + module
    if module == "all":
        for mod in modules:
            msg = await bot.say("ok, reloading `{0}`".format(mod))
            bot.unload_extension(mod)
            bot.load_extension(mod)
        await bot.edit_message(msg, "ok, reloaded `everything`")
    elif mod in modules:
        msg = await bot.say("ok, reloading {0}".format(mod))
        bot.unload_extension(mod)
        bot.load_extension(mod)
        await bot.edit_message(msg, "ok, reloaded `{0}`".format(module))
    else:
        await bot.say("You can't reload {0}, it doesn't exist!".format(module))

@bot.command(pass_context=True)
@checks.is_owner()
async def update(ctx):
    try:
        await bot.say("ok brb, restarting")
        restart_program()
    except Exception as e:
        await bot.say(code.format(type(e).__name__ + ': ' + str(e)))

@bot.command(pass_context=True)
@checks.is_owner()
async def die(ctx):
    try:
        await bot.say("Logging out")
        await bot.logout()
    except Exception as e:
        await bot.say(code.format(type(e).__name__ + ': ' + str(e)))

bot.add_cog(Default(bot))
bot.run('token')
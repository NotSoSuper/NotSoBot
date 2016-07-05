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
import datetime
from sys import argv, path
from discord.ext import commands
from discord.enums import Status
from discord.message import Message
from discord.user import User
from discord.server import Server
from discord.client import Client
from random import choice
from re import sub
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
timestamp = time.strftime('%H:%M:%S')
starttime = time.time()
starttime2 = time.ctime(int(time.time()))

if os.path.isfile("/root/discord/utils/blacklist.txt"):
  pass
else:
  with open("/root/discord/utils/blacklist.txt","a") as f:
    f.write("")

dirp = "/root/discord/files/gif"
filel = os.listdir(dirp)
for filen in filel:
  os.remove(dirp+"/"+filen)

connection = pymysql.connect(host='',
             user='',
             password='',
             db='',
             charset='',
             cursorclass=pymysql.cursors.DictCursor)

cursor = connection.cursor()

modules = [
    'mods.Moderation',
    'mods.Utils',
    'mods.Info',
    'mods.Fun',
    'mods.Chan',
    'mods.Tags',
    'mods.Logs',
    'mods.Wc',
    'mods.AI'
]

@bot.event
async def on_ready():
  try:
    for cog in modules:
      try:
        bot.load_extension(cog)
      except Exception as e:
        print('Failed to load mod {0}\n{1}: {2}'.format(cog, type(e).__name__, e))
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
message_delete_logging = True
message_edit_logging = True
blacklist_logging = False
command_logging = True
replies_disabled = True
say_errors_on_message = False
command_errors = False
cooldown = {}

@bot.event
async def on_message(message):
  try:
    if message.author == bot.user:
      return
    if message.author.bot:
      return
    if "<@" + message.author.id + ">" in open('/root/discord/utils/blacklist.txt').read():
      if blacklist_logging == True:
        sql = "INSERT INTO `blacklist_log` (`server`, `user`, `time`) VALUES (%s, %s, %s)"
        if message.channel.is_private:
          cursor.execute(sql, ("Private Message", "{0} <{1}>".format(message.author.name, message.author.id), message.timestamp))
        else:
          cursor.execute(sql, ("{0} #{1}".format(message.server.name, message.channel.name),"{0} <{1}>".format(message.author.name, message.author.id), message.timestamp))
        connection.commit()
      return
    elif message.channel.id in open('/root/discord/utils/cblacklist.txt').read() and message.channel.is_private == False and ".blacklist" not in message.content:
      if blacklist_logging == True:
        sql = "INSERT INTO `blacklist_log` (`server`, `user`, `time`) VALUES (%s, %s, %s)"
        cursor.execute(sql, ("Channel Blacklist {0} #{1}".format(message.server.name, message.channel.name),"{0} <{1}>".format(message.author.name, message.author.id), message.timestamp))
        connection.commit()
      return
    else:
      prefix = '.'
      if message.channel.is_private == False:
        prefix_set = False
        sql = "SELECT prefix FROM `prefix` WHERE server={0}"
        sql = sql.format(message.server.id)
        sql_channel = "SELECT prefix,channel FROM `prefix_channel` WHERE server={0} AND channel={1}"
        sql_channel = sql_channel.format(message.server.id, message.channel.id)
        cursor.execute(sql_channel)
        result = cursor.fetchall()
        if message.content.startswith(".prefix") == False and len(result) != 0:
          for s in result:
            if s['channel'] == message.channel.id:
              setattr(bot, "command_prefix", s['prefix'])
              prefix_set = True
              break
        elif message.content.startswith(".prefix") == False and prefix_set == False:
          cursor.execute(sql)
          result = cursor.fetchall()
          if len(result) != 0:
            setattr(bot, "command_prefix", result[0]['prefix'])
            prefix = result[0]['prefix']
      utc = datetime.datetime.utcnow()
      utc_ = int(utc.strftime("%s"))
      if message.author.id in cooldown and message.content.startswith(prefix):
        time = cooldown[message.author.id]
        if utc_ > time:
          del cooldown[message.author.id]
          pass
        else:
          secc = int(time) - int(utc_)
          await bot.send_message(message.channel, ":no_entry: **Cooldown**it `Cannot use again for another {0} secconds`".format(str(secc)))
          return
      elif message.content.startswith(prefix):
        cooldown.update({message.author.id:utc_+5})
      await bot.process_commands(message)
      setattr(bot, "command_prefix", commands.when_mentioned_or('.'))
    if message_logging == True:
      sql = "INSERT INTO `messages` (`server`, `time`, `channel`, `author`, `content`) VALUES (%s, %s, %s, %s, %s)"
      if message.channel.is_private:
        cursor.execute(sql, ("Private Message", message.timestamp, "N/A", "{0} <{1}>".format(message.author.name, message.author.id) ,"{0}".format(message.content)))
      else:
        cursor.execute(sql, (message.server.name, message.timestamp, message.channel.name, "{0} <{1}>".format(message.author.name, message.author.id) ,"{0}".format(message.content)))
      connection.commit()
    # print("({0}, #{1}) {2} <{3}>: {4}".format(message.server.name, message.channel.name, message.author.name, message.author.id, message.content))
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
    sql = "INSERT INTO `command_logs` (`server`, `time`, `channel`, `author`, `command`, `message`) VALUES (%s, %s, %s, %s, %s, %s)"
    if ctx.message.channel.is_private:
      cursor.execute(sql, ("Private Message", ctx.message.timestamp, "N/A", "{0} <{1}>".format(ctx.message.author.name, ctx.message.author.id), ctx.invoked_with, ctx.message.content))
    else:
      cursor.execute(sql, (ctx.message.server.name, ctx.message.timestamp, ctx.message.channel.name, "{0} <{1}>".format(ctx.message.author.name, ctx.message.author.id), ctx.invoked_with, ctx.message.content))
    connection.commit()
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
    target = discord.Object(id='178313681786896384')
    await bot.send_message(target, cool.format(msg))
    # if ctx.message.channel.is_private == False and ctx.message.server.name == "Dank Memes" and ctx.message.channel.name != "test":
    #   await asyncio.sleep(120)
    #   async for message in bot.logs_from(ctx.message.channel, limit=50):
    #      if message.author == bot.user:
    #        await asyncio.ensure_future(bot.delete_message(message))
    #        await asyncio.sleep(0.4)
  except Exception as e:
    print(e)

@bot.event
async def on_message_delete(message):
  if message_delete_logging == True:
    sql = "INSERT INTO `message_delete_logs` (`server`, `time`, `channel`, `author`, `message`) VALUES (%s, %s, %s, %s, %s)"
    if message.channel.is_private:
      cursor.execute(sql, ("Private Message", message.timestamp, "N/A", "{0} <{1}>".format(message.author.name, message.author.id), message.content))
    else:
      cursor.execute(sql, (message.server.name, message.timestamp, message.channel.name, "{0} <{1}>".format(message.author.name, message.author.id), message.content))
    connection.commit()
  try:
    msg = "User: {0} <{1}>\n".format(message.author, message.author.id).replace("'", "")
    msg += "Time: {0}\n".format(message.timestamp)
    if message.channel.is_private:
      msg += "Server: Private Message\n"
    else:
      msg += "Server: {0}\n".format(message.server.name).replace("'", "")
      msg += "Channel: {0}\n".format(message.channel.name).replace("'", "")
    msg += "Deleted Message: {0}\n".format(message.content)
    target = discord.Object(id='182241816530124800')
    await bot.send_message(target, cool.format(msg))
  except Exception as e:
    print(e)

@bot.event
async def on_message_edit(ctx, message):
  if ctx.content == message.content:
    return
  if ctx.author == bot.user:
    return
  if message_edit_logging == True:
    sql = "INSERT INTO `message_edit_logs` (`server`, `time`, `channel`, `author`, `before`, `after`) VALUES (%s, %s, %s, %s, %s, %s)"
    if message.channel.is_private:
      cursor.execute(sql, ("Private Message", message.timestamp, "N/A", "{0} <{1}>".format(message.author.name, ctx.author.id), ctx.content, message.content))
    else:
      cursor.execute(sql, (message.server.name, message.timestamp, message.channel.name, "{0} <{1}>".format(message.author.name, message.author.id), ctx.content, message.content))
    connection.commit()
  try:
    msg = "User: {0} <{1}>\n".format(ctx.author, ctx.author.id).replace("'", "")
    msg += "Time: {0}\n".format(ctx.timestamp)
    if ctx.channel.is_private:
      msg += "Server: Private Message\n"
    else:
      msg += "Server: {0}\n".format(ctx.server.name).replace("'", "")
      msg += "Channel: {0}\n".format(ctx.channel.name).replace("'", "")
    msg += "Before: {0}\n".format(ctx.content)
    msg += "After: {0}".format(message.content).replace("'", "")
    target = discord.Object(id='182243859420413952')
    await bot.send_message(target, cool.format(msg))
  except Exception as e:
    print(e)

def prRed(prt): print("\033[91m {}\033[00m" .format(prt))
def prGreen(prt): print("\033[92m {}\033[00m" .format(prt))
def prYellow(prt): print("\033[93m {}\033[00m" .format(prt))
def prLightPurple(prt): print("\033[94m {}\033[00m" .format(prt))
def prPurple(prt): print("\033[95m {}\033[00m" .format(prt))
def prCyan(prt): print("\033[96m {}\033[00m" .format(prt))
def prLightGray(prt): print("\033[97m {}\033[00m" .format(prt))
def prBlack(prt): print("\033[98m {}\033[00m" .format(prt))

@bot.event
async def on_error(event, *args, **kwargs):
  prRed("Error!")
  Current_Time = datetime.datetime.utcnow().strftime("%b/%d/%Y %H:%M:%S UTC")
  prGreen(Current_Time)
  prRed(traceback.format_exc())
  error =  '```py\n{}\n```'.format(traceback.format_exc())
  await bot.send_message(bot.get_channel("180073721048989696"), "```py\n{}```".format(Current_Time + "\n"+ "ERROR!") + "\n" +  error)

async def send_cmd_help(ctx):
  if ctx.invoked_subcommand:
    pages = bot.formatter.format_help_for(ctx, ctx.invoked_subcommand)
    for page in pages:
      await bot.send_message(ctx.message.channel, page.replace("\n","fix\n",1))
  else:
    pages = bot.formatter.format_help_for(ctx, ctx.command)
    for page in pages:
      await bot.send_message(ctx.message.channel, page.replace("\n","fix\n",1))

@bot.event
async def on_command_error(e, ctx):
  if isinstance(e, commands.MissingRequiredArgument):
    await send_cmd_help(ctx)
  elif isinstance(e, commands.BadArgument):
    await send_cmd_help(ctx)
  elif isinstance(e, checks.No_Perms):
    await bot.send_message(ctx.message.channel, ":no_entry: `No Permission`")
  elif isinstance(e, checks.No_Owner):
    await bot.send_message(ctx.message.channel, ":no_entry: `Owner Only`")
  elif isinstance(e, checks.No_Mod):
    await bot.send_message(ctx.message.channel, ":no_entry: `Moderator or Above Only`")
  elif isinstance(e, checks.No_Admin):
    await bot.send_message(ctx.message.channel, ":no_entry: `Administrator Only`")
  elif isinstance(e, checks.No_Role):
    await bot.send_message(ctx.message.channel, ":no_entry: `Custom Role Specific Only`")
  elif isinstance(e, checks.No_ServerandPerm):
    await bot.send_message(ctx.message.channel, ":no_entry: `Server specific command or no permission`")
  elif command_errors == True and isinstance(e, commands.CommandNotFound):
    await bot.send_message(ctx.message.channel, ":warning: Command `{0}` Not Found!".format(ctx.invoked_with))

@bot.command(pass_context=True, hidden=True)
@checks.is_owner()
async def debug(ctx, *, code : str):
  code = code.strip('` ')
  python = '```py\n{}\n```'
  result = None
  try:
    result = eval(code)
  except Exception as e:
    await bot.say(python.format(type(e).__name__ + ': ' + str(e)))
    return
  if asyncio.iscoroutine(result):
    result = await result
  await bot.say(python.format(result))

@bot.group(pass_context=True, aliases=['setprefix', 'changeprefix'], invoke_without_command=True, no_pm=True)
@checks.admin_or_perm(manage_server=True)
async def prefix(ctx, txt:str=None):
  """Change the Bots Prefix for the Server"""
  if txt == None:
    sql = "SELECT prefix FROM `prefix` WHERE server={0}"
    sql = sql.format(ctx.message.server.id)
    sql_channel = "SELECT prefix FROM `prefix_channel` WHERE server={0} AND channel={1}"
    sql_channel = sql_channel.format(ctx.message.server.id, ctx.message.channel.id)
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.execute(sql_channel)
    result2 = cursor.fetchall()
    if len(result) == 0:
      server_prefix = '.'
    else:
      server_prefix = result[0]['prefix']
    if len(result2) == 0:
      channel_prefix = None
    else:
      channel_prefix = result2[0]['prefix']
    msg = "Server Prefix: `{0}`\n".format(server_prefix)
    if channel_prefix != None:
      msg += "Channel Prefix: `{0}`".format(channel_prefix)
    await bot.say(msg)
    return
  sql = "INSERT INTO `prefix` (`server`, `prefix`, `id`) VALUES (%s, %s, %s)"
  update_sql = 'UPDATE `prefix` SET prefix="{0}" WHERE server={1}'
  update_sql = update_sql.format(txt, ctx.message.server.id)
  check = "SELECT server FROM `prefix` WHERE server={0}"
  check = check.format(ctx.message.server.id)
  cursor.execute(check)
  result = cursor.fetchall()
  if len(result) == 0:
    cursor.execute(sql, (ctx.message.server.id, txt, ctx.message.author.id))
    connection.commit()
    await bot.say(":white_check_mark: Set Bot Prefix to \"{0}\" for the server\n".format(txt))
  else:
    cursor.execute(update_sql)
    connection.commit()
    await bot.say(":white_check_mark: Updated Bot Prefix to \"{0}\" for the server".format(txt))

@prefix.command(pass_context=True, name='channel')
@checks.admin_or_perm(manage_server=True)
async def _prefix_channel(ctx, txt:str, channel:discord.Channel=None):
  """Change the Bots Prefix for the current Channel"""
  if channel == None:
    channel = ctx.message.channel
  sql = "INSERT INTO `prefix_channel` (`server`, `prefix`, `channel`, `id`) VALUES (%s, %s, %s, %s)"
  update_sql = 'UPDATE `prefix_channel` SET prefix="{0}" WHERE server={1} AND channel={2}'
  update_sql = update_sql.format(txt, ctx.message.server.id, ctx.message.channel.id)
  check = "SELECT * FROM `prefix_channel` WHERE server={0} AND channel={1}"
  check = check.format(ctx.message.server.id, channel.id)
  cursor.execute(check)
  result = cursor.fetchall()
  if len(result) == 0:
    cursor.execute(sql, (ctx.message.server.id, txt, channel.id, ctx.message.author.id))
    connection.commit()
    await bot.say(":white_check_mark: Set Bot Prefix to \"{0}\" for the current channel".format(txt))
  else:
    cursor.execute(update_sql)
    connection.commit()
    await bot.say(":white_check_mark: Updated Bot Prefix to \"{0}\" for the current channel".format(txt))

@prefix.command(pass_context=True, name='reset')
@checks.admin_or_perm(manage_server=True)
async def _prefix_reset(ctx, what:str=None, channel:discord.Channel=None):
  """Reset All Custom Set Prefixes For the Bot"""
  if what == "server":
    sql = "DELETE FROM `prefix` WHERE server={0}"
    sql = sql.format(ctx.message.server.id)
    check = "SELECT * FROM `prefix` WHERE server={0}"
    check = check.format(ctx.message.server.id)
    cursor.execute(check)
    result = cursor.fetchall()
    if len(result) == 0:
      await bot.say(":no_entry: Current Channel does **not** have a Custom Prefix set!\nMention the channel after \"reset channel\" for a specific channel.")
      return
    else:
      cursor.execute(sql)
      connection.commit()
      await bot.say(":exclamation: Reset Server Prefix\nThis does not reset channel Prefixes, run \"all\" after reset to reset all Prefixes.")
  elif what == "channel":
    if channel == None:
      channel = ctx.message.channel
    sql = "DELETE FROM `prefix_channel` WHERE server={0} AND channel={1}"
    sql = sql.format(ctx.message.server.id, channel.id)
    check = "SELECT * FROM `prefix_channel` WHERE server={0} AND channel={1}"
    check = check.format(ctx.message.server.id, channel.id)
    cursor.execute(check)
    result = cursor.fetchall()
    if len(result) == 0:
      await bot.say(":no_entry: Current channel does **not** have a custom Prefix Set!\nMention the channel after \"reset channel\" for a specific channel.")
      return
    else:
      cursor.execute(sql)
      connection.commit()
      await bot.say(":exclamation: Reset current channels Custom Prefix!\nThis does **not** reset all Custom Channel Prefixes, \"reset channels\" to do so.")
      return
  elif what == "channels":
    sql = "DELETE FROM `prefix_channel` WHERE server={0}"
    sql = sql.format(ctx.message.server.id)
    check = "SELECT * FROM `prefix_channel` WHERE server={0}"
    check = check.format(ctx.message.server.id)
    cursor.execute(check)
    result = cursor.fetchall()
    if len(result) == 0:
      await bot.say(":no_entry: Server Does **not** gave a Custom Prefix set for any channel!\nMention the Channel after \"reset channel\" for a specific channel.")
      return
    else:
      cursor.execute(sql)
      connection.commit()
      await bot.say(":exclamation: Reset all channels custom prefixes!")
      return
  elif what == "all" or what == "everything":
    sql = "DELETE FROM `prefix_channel` WHERE server={0}"
    sql = sql.format(ctx.message.server.id)
    sql2 = "DELETE FROM `prefix` WHERE server={0}"
    sql2 = sql2.format(ctx.message.server.id)
    cursor.execute(sql)
    cursor.execute(sql2)
    connection.commit()
    await bot.say(":warning: Reset All Custom Server Prefix Settings!")
    return
  else:
    await bot.say(":no_entry: Invalid Option\nOptions: `server, channel, channels, all/everything`")

@bot.command()
@checks.is_owner()
async def load(*,module:str):
  module = "mods." + module
  if module in modules:
    msg = await bot.say("ok, loading `{0}`".format(module))
    bot.load_extension(module)
    await bot.edit_message(msg, "ok, loaded `{0}`".format(module))
  else:
    await bot.say("You can't load a module that doesn't exist!")

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
    msg = await bot.say("ok, reloading `{0}`".format(mod))
    bot.unload_extension(mod)
    bot.load_extension(mod)
    await bot.edit_message(msg, "ok, reloaded `{0}`".format(module))
  else:
    await bot.say("You can't reload a module that doesn't exist!")

@bot.command(pass_context=True)
@checks.is_owner()
async def update(ctx):
  await bot.say("ok brb, killing my self")
  restart_program()

@bot.command(pass_context=True)
@checks.is_owner()
async def die(ctx):
  await bot.say("Drinking bleach.....")
  await bot.logout()

bot.run('')
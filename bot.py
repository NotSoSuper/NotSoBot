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
from discord.ext import commands
from random import choice
from re import sub
from utils import checks

def restart_program():
  python = sys.executable
  os.execl(python, python, * sys.argv)

# --------------------------Bot Stuff Under Here--------------------------
sys.path.insert(0, '.')

description = '''NotSoSuper\'s Super Duper Bot'''
owner = "130070621034905600"
# You'll need to update stuff in mods/Info.py and mods/Stats.py if you don't wanna have 4 shards like the main version.
sharding = False
shard_id = 0
shard_count = 4
if sharding:
  bot = commands.Bot(command_prefix=commands.when_mentioned_or('.'), description=description, help_attrs={'name':"iamabadhelpcommand", 'enabled':False, 'hidden':True}, shard_id=shard_id, shard_count=shard_count)
else:
  bot = commands.Bot(command_prefix=commands.when_mentioned_or('.'), description=description, help_attrs={'name':"iamabadhelpcommand", 'enabled':False, 'hidden':True})
code = "```py\n{0}\n```"
cool = "```xl\n{0}\n```"
diff = "```diff\n{0}\n```"
timestamp = time.strftime('%H:%M:%S')
starttime = time.time()
starttime2 = time.ctime(int(time.time()))

class Object(object):
  pass

def discord_path(path):
  return os.path.join(os.getenv('discord_path', '~/discord/'), path)

def files_path(path):
  return os.path.join(os.getenv('files_path', 'files/'), path)

bot.path = Object()
bot.path.discord = discord_path
bot.path.files = files_path

if os.path.isfile(discord_path("utils/blacklist.txt")):
  pass
else:
  with open(discord_path("utils/blacklist.txt"), "a") as f:
    f.write('')

dirp = files_path('gif')
filel = os.listdir(dirp)
for filen in filel:
  os.remove(dirp+"/"+filen)

bot.mysql = Object()
bot.mysql.connection = pymysql.connect(host='',
                     user='',
                     password='',
                     db='',
                     charset='',
                     cursorclass=pymysql.cursors.DictCursor)
bot.mysql.cursor = bot.mysql.connection.cursor()

cursor = bot.mysql.cursor
connection = bot.mysql.connection

async def queue_message(channel_id:str, msg:str):
  message_id = random.randint(0, 1000000)
  payload = {'key':'verysecretkey', 'id': message_id, 'channel_id': channel_id, 'message': msg}
  try:
    r = requests.post(':eyes:/queue', data=payload, timeout=5)
  except (requests.packages.urllib3.exceptions.MaxRetryError, requests.packages.urllib3.exceptions.NewConnectionError):
    await asyncio.sleep(5)
    return

bot.queue_message = queue_message

def write_last_time():
  path = files_path('last_time_{0}.txt'.format(bot.shard_id))
  utc = datetime.datetime.utcnow()
  utc_ = utc.strftime("%s")
  with open(path, 'wb') as f:
    f.write(utc_.encode())
    f.close()

def get_last_time():
  path = files_path('last_time_{0}.txt'.format(bot.shard_id))
  try:
    return int(open(path, 'r').read())
  except:
    return False

# 'mods.Pager', 'mods.Lua'
modules = [
  # 'mods.Api',
  'mods.Moderation',
  'mods.Utils',
  'mods.Info',
  'mods.Fun',
  'mods.Chan',
  'mods.Repl',
  'mods.Stats',
  'mods.Tags',
  'mods.Logs',
  'mods.Wc',
  'mods.AI',
  'mods.Changes',
  'mods.Markov',
  'mods.Verification',
  'mods.Nsfw'
]
on_ready_write = False
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
    utc = datetime.datetime.utcnow()
    utc_ = int(utc.strftime("%s"))
    if get_last_time() == False:
      downtime = 0
    else:
      downtime = str(utc_ - get_last_time())
    time_msg = time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(get_last_time()))
    current_time_msg = time.strftime('%m/%d/%Y %H:%M:%S')
    msg = '`[Shard {0}]` {1} is now <@&211726904774885377> and <@&211736213890007040>, <@&211727098149076995> since **{2}** for **{3}** second(s) (Current Time: **{4}**).'.format(bot.shard_id, bot.user.mention, time_msg, downtime, current_time_msg)
    await queue_message('211247117816168449', msg)
    global on_ready_write
    on_ready_write = True
    write_last_time()
  except Exception as e:
    print(type(e).__name__ + ': ' + str(e))

with open(discord_path("utils/config.json")) as f:
  config = json.load(f)

message_logging = True
message_delete_logging = True
message_edit_logging = True
blacklist_logging = False
command_logging = True
replies_disabled = True
say_errors_on_message = False
command_errors = False
cooldown = {}
cooldown_sent = {}

@bot.event
async def on_message(message):
  if message.author == bot.user:
    return
  if message.author.bot:
    return
  if "<@" + message.author.id + ">" in open(discord_path('utils/blacklist.txt')).read() or "<@!" + message.author.id + ">" in open(discord_path('utils/blacklist.txt')).read():
    if blacklist_logging == True:
      sql = "INSERT INTO `blacklist_log` (`server`, `user`, `time`) VALUES (%s, %s, %s)"
      if message.channel.is_private:
        cursor.execute(sql, ("Private Message", "{0} <{1}>".format(message.author.name, message.author.id), message.timestamp))
      else:
        cursor.execute(sql, ("{0} #{1}".format(message.server.name, message.channel.name),"{0} <{1}>".format(message.author.name, message.author.id), message.timestamp))
      connection.commit()
    return
  elif message.channel.id in open(discord_path('utils/cblacklist.txt')).read() and message.channel.is_private == False and message.content.startswith(".blacklist") == False:
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
      if message.content.startswith(prefix+"prefix") == False and len(result) != 0:
        for s in result:
          if s['channel'] == message.channel.id:
            setattr(bot, "command_prefix", commands.when_mentioned_or(s['prefix']))
            prefix = s['prefix']
            prefix_set = True
            break
      elif message.content.startswith(prefix+"prefix") == False and prefix_set == False:
        cursor.execute(sql)
        result = cursor.fetchall()
        if len(result) != 0:
          setattr(bot, "command_prefix", commands.when_mentioned_or(result[0]['prefix']))
          prefix = result[0]['prefix']
    def lolthing(s):
      count = 0
      for x in s:
        if count == 2:
          break
        if x == prefix:
          count += 1
      if count == 1:
        return True
      return False
    command = None
    if message.content.startswith(prefix) and lolthing(message.content) and message.content != prefix:
      message.content = message.content.strip()
      cc = message.content.split(prefix)
      try:
        if len(cc[1].split()) == 1:
          command = cc[1]
        else:
          command = cc[1]
          command = command.split()[0]
      except Exception as e:
        await queue_message('180073721048989696', '{0}\n{1}'.format(e, message.content))
      if command in bot.commands and message.author.id not in cooldown:
        try:
          await bot.send_typing(message.channel)
        except:
          pass
      if command in bot.commands and message.author.id != config['ownerid']:
        utc = datetime.datetime.utcnow()
        utc_ = int(utc.strftime("%s"))
        if message.author.id in cooldown:
          time = cooldown[message.author.id]
          secc = int(time) - int(utc_)
          if utc_ > time or secc == 0:
            del cooldown[message.author.id]
            pass
          else:
            if message.channel.id in cooldown_sent:
              time_ = cooldown_sent[message.channel.id]
              secc_ = int(time) - int(utc_)
              if utc_ > time_ or secc_ == 0:
                del cooldown_sent[message.channel.id]
                pass
              else:
                return
            cooldown_sent.update({message.channel.id:utc_+5})
            await bot.send_message(message.channel, ":no_entry: **Cooldown** `Cannot use again for another {0} seconds`".format(str(secc)))
            return
        else:
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

@bot.event
async def on_command(command, ctx):
  if command_logging == True:
    sql = "INSERT INTO `command_logs` (`server`, `time`, `channel`, `author`, `command`, `message`) VALUES (%s, %s, %s, %s, %s, %s)"
    if ctx.invoked_with == 'img':
      ctx.invoked_with = 'image'
    if ctx.invoked_with == 'im':
      ctx.invoked_with = 'image'
    if ctx.invoked_with == 'magic':
      ctx.invoked_with = 'magik'
    if ctx.message.channel.is_private:
      cursor.execute(sql, ("Private Message", ctx.message.timestamp, "N/A", "{0} <{1}>".format(ctx.message.author.name, ctx.message.author.id), ctx.invoked_with, ctx.message.content))
    else:
      cursor.execute(sql, (ctx.message.server.name, ctx.message.timestamp, ctx.message.channel.name, "{0} <{1}>".format(ctx.message.author.name, ctx.message.author.id), ctx.invoked_with, ctx.message.content))
    connection.commit()
  msg = "User: {0} <{1}>\n".format(ctx.message.author, ctx.message.author.id).replace("'", "")
  msg += "Command: {0}\n".format(ctx.invoked_with)
  if ctx.message.channel.is_private:
    msg += "Server: Private Message\n"
  else:
    msg += "Server: {0}\n".format(ctx.message.server.name).replace("'", "")
    msg += "Channel: {0}\n".format(ctx.message.channel.name).replace("'", "")
  msg += "Shard ID: {0}\n".format(str(bot.shard_id))
  if len(ctx.message.mentions) != 0:
    for s in ctx.message.mentions:
      ctx.message.content = ctx.message.content.replace(s.mention, '@'+s.name).replace('<@!{0}>'.format(s.id), '@'+s.name)
  msg2 = "`Context Message:` {0}".format(ctx.message.content)
  for attachment in ctx.message.attachments:
    msg2 += ' '+attachment['url']
  await queue_message('178313681786896384', '`[{0}]` '.format(time.strftime("%I:%M:%S %p"))+cool.format(msg)+msg2)

@bot.event
async def on_message_delete(message):
  if message.author == bot.user:
    return
  if message_delete_logging == True:
    sql = "INSERT INTO `message_delete_logs` (`server`, `time`, `channel`, `author`, `message`) VALUES (%s, %s, %s, %s, %s)"
    if message.channel.is_private:
      cursor.execute(sql, ("Private Message", message.timestamp, "N/A", "{0} <{1}>".format(message.author.name, message.author.id), message.content))
    else:
      cursor.execute(sql, (message.server.name, message.timestamp, message.channel.name, "{0} <{1}>".format(message.author.name, message.author.id), message.content))
    connection.commit()
  msg = "User: {0} <{1}>\n".format(message.author, message.author.id).replace("'", "")
  if message.channel.is_private:
    msg += "Server: Private Message\n"
  else:
    msg += "Server: {0}\n".format(message.server.name).replace("'", "")
    msg += "Channel: {0}\n".format(message.channel.name).replace("'", "")
  if len(message.mentions) != 0:
    for s in message.mentions:
      message.content = message.content.replace(s.mention, '@'+s.name).replace('<@!{0}>'.format(s.id), '@'+s.name)
  msg2 = "`Deleted Message:` {0}\n".format(message.content)
  await queue_message('182241816530124800', '`[{0}]` '.format(time.strftime("%I:%M:%S %p"))+cool.format(msg)+msg2)

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
  msg = "User: {0} <{1}>\n".format(ctx.author, ctx.author.id).replace("'", "")
  if ctx.channel.is_private:
    msg += "Server: Private Message\n"
  else:
    msg += "Server: {0}\n".format(ctx.server.name).replace("'", "")
    msg += "Channel: {0}\n".format(ctx.channel.name).replace("'", "")
  if len(ctx.mentions) != 0:
    for s in ctx.mentions:
      ctx.content = ctx.content.replace(s.mention, '@'+s.name).replace('<@!{0}>'.format(s.id), '@'+s.name)
  if len(message.mentions) != 0:
    for s in message.mentions:
      message.content = message.content.replace(s.mention, '@'+s.name).replace('<@!{0}>'.format(s.id), '@'+s.name)
  msg2 = "`Before:` {0}\n".format(ctx.content)
  msg2 += "`After:` {0}".format(message.content)
  await queue_message('182243859420413952', '`[{0}]` '.format(time.strftime("%I:%M:%S %p"))+cool.format(msg)+msg2)

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
  await queue_message("180073721048989696", error)

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
  elif isinstance(e, checks.No_Sup):
    await bot.send_message(ctx.message.channel, ":no_entry: `Command only for \"Superior Servers Staff\" Server")
  elif isinstance(e, checks.No_ServerandPerm):
    await bot.send_message(ctx.message.channel, ":no_entry: `Server specific command or no permission`")
  elif isinstance(e, checks.Nsfw):
    await bot.send_message(ctx.message.channel, ":underage: `NSFW command, please add [nsfw] in your channel topic or move to a channel named nsfw!`")
  elif command_errors == True and isinstance(e, commands.CommandNotFound):
    await bot.send_message(ctx.message.channel, ":warning: Command `{0}` Not Found!".format(ctx.invoked_with))

@bot.event
async def on_server_join(server):
  msg = '+ SERVER JOIN\n\n'
  msg += "! Server: {0} <{1}>\n".format(server.name, server.id)
  msg += "- Owner: {0} <{1}>\n".format(server.owner.name, server.owner.id)
  msg += "! Channels: {0}\n".format(len(server.channels))
  msg += "- Members: {0}\n".format(len(server.members))
  c = None
  for channel in server.channels:
    if server.me.permissions_in(channel).create_instant_invite == True:
      c = channel
      break
  if c == None:
    msg += "! Invite: No permission :("
  else:
    invite = await bot.create_invite(c)
    msg += "! Invite: {0}".format(invite)
  await queue_message('211247117816168449', '`[{0}]` '.format(time.strftime("%m/%d/%Y|%I:%M:%S %p"))+diff.format(msg))

@bot.event
async def on_server_remove(server):
  sql = "DELETE FROM `prefix_channel` WHERE server={0}"
  sql = sql.format(server.id)
  sql2 = "DELETE FROM `prefix` WHERE server={0}"
  sql2 = sql2.format(server.id)
  cursor.execute(sql)
  cursor.execute(sql2)
  connection.commit()
  msg = '- SERVER LEAVE\n'
  msg += "! Server: {0} <{1}>\n".format(server.name, server.id)
  msg += "+ Owner: {0} <{1}>".format(server.owner.name, server.owner.id)
  await queue_message('211247117816168449', '`[{0}]` '.format(time.strftime("%m/%d/%Y|%I:%M:%S %p"))+diff.format(msg))

@bot.event
async def on_socket_raw_receive(message):
  if on_ready_write:
    write_last_time()
    await asyncio.sleep(1)

@bot.event
async def on_resumed():
  time_msg = time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(get_last_time()))
  current_time_msg = time.strftime('%m/%d/%Y %H:%M:%S')
  utc = datetime.datetime.utcnow()
  utc_ = int(utc.strftime("%s"))
  if get_last_time() == None:
    downtime = 0
  else:
    downtime = str(utc_ - get_last_time())
  msg = '`[Shard {0}]` {1} has now <@&211727010932719627> after being <@&211727098149076995> since **{2}** for **{3}** second(s) (Current Time: **{4}**)'.format(bot.shard_id, bot.user.mention, time_msg, downtime, current_time_msg)
  await queue_message('211247117816168449', msg)

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
      msg += "**Current** Channel Prefix: `{0}`".format(channel_prefix)
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
    await bot.say(":white_check_mark: Set bot prefix to \"{0}\" for the server\n".format(txt))
  else:
    cursor.execute(update_sql)
    connection.commit()
    await bot.say(":white_check_mark: Updated bot prefix to \"{0}\" for the server".format(txt))

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
    await bot.say(":white_check_mark: Set bot prefix to \"{0}\" for the current channel".format(txt))
  else:
    cursor.execute(update_sql)
    connection.commit()
    await bot.say(":white_check_mark: Updated bot prefix to \"{0}\" for the current channel".format(txt))

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
      await bot.say(":no_entry: Current server does **not** have a custom prefix set!")
      return
    else:
      cursor.execute(sql)
      connection.commit()
      await bot.say(":exclamation: Reset server prefix\nThis does not reset channel prefixes, run \"all\" after reset to reset all prefixes *or* \"channels\" to reset all custom channel prefixes.")
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
      await bot.say(":no_entry: {0} does **not** have a custom prefix Set!\nMention the channel after \"reset channel\" for a specific channel.".format(channel.mention))
      return
    else:
      cursor.execute(sql)
      connection.commit()
      await bot.say(":exclamation: Reset {0}'s prefix!\nThis does **not** reset all custom channel prefixes, \"reset channels\" to do so.".format(channel.mention))
      return
  elif what == "channels":
    sql = "DELETE FROM `prefix_channel` WHERE server={0}"
    sql = sql.format(ctx.message.server.id)
    check = "SELECT * FROM `prefix_channel` WHERE server={0}"
    check = check.format(ctx.message.server.id)
    cursor.execute(check)
    result = cursor.fetchall()
    if len(result) == 0:
      await bot.say(":no_entry: Server does **not** reset a custom prefix set for any channel!\nMention the channel after \"reset channel\" for a specific channel.")
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
    await bot.say(":warning: Reset All custom server prefix settings!")
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
  try:
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
  except Exception as e:
    await bot.say(code.format(e))

@bot.command(pass_context=True)
@checks.is_owner()
async def update(ctx, idk:str=None):
  if idk != None and idk == 'all' or idk == 'nodes' or idk == 'shards':
    await bot.say("ok brb, restarting all shards\n`Current Shard: {0}`".format(str(bot.shard_id)))
    os.system('pm2 restart all')
  else:
    await bot.say("ok brb")
    restart_program()

@bot.command(pass_context=True)
@checks.is_owner()
async def die(ctx):
  await bot.logout()

@bot.command(pass_context=True)
async def complain(ctx, *, message:str):
  await queue_message("186704399677128704", "User: {0}\nServer: `{1} <{2}>`\nChannel: `{3} <{4}>`\n Time: `{5}`\n Message: ```{6}```".format(ctx.message.author.mention, ctx.message.server.name, ctx.message.server.id, ctx.message.channel.name, ctx.message.channel.id, ctx.message.timestamp, message))
  await bot.say("ok, left complaint")

import atexit
@atexit.register
def bot_shutdown():
  cursor.close()
  connection.close()

bot.run(os.getenv('bot_token'))
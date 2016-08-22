import asyncio
import discord
import pymysql
import json
import aiohttp
from time import strftime
from discord.ext import commands
from utils import checks

class Changes():
  def __init__(self, bot):
    self.bot = bot
    self.connection = bot.mysql.connection
    self.cursor = bot.mysql.cursor

  async def gist(self, ctx, type:int, idk:str, content:str):
    if type == 1:
      gist = {
        'description': 'Name logs for user: "{2}" | \nUploaded from NotSoSuper\'s Bot by: {0} <{1}>.'.format(ctx.message.author.name, ctx.message.author.id, idk),
        'public': True,
        'files': {
            'name_logs_{0}.txt'.format(idk): {
                'content': content
            }
        }
      }
    elif type == 2:
      gist = {
        'description': 'Server Name Logs for server: "{2}" | \nUploaded from NotSoSuper\'s Bot by: {0} <{1}>.'.format(ctx.message.author.name, ctx.message.author.id, idk),
        'public': True,
        'files': {
            'server_name_logs_{0}.txt'.format(idk): {
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

  # when you see the cancer code you wont even understand it, i dont anymore either (why im not touching it)!
  @commands.command(pass_context=True, aliases=['name', 'namelogs'])
  async def names(self, ctx, user:str=None):
    """Show all the logs the bot has of the users name or nickname"""
    if user == None:
      user = ctx.message.author
    else:
      if user.isdigit():
        user = discord.Server.get_member(ctx.message.server, user_id=user)
        if user == None:
          for server in self.bot.servers:
            for member in server.members:
              if member.id == user:
                user = member
        if user == None:
          await self.bot.say("Sorry, no user was found with that ID on any servers I'm on!")
          return
      else:
        if len(ctx.message.mentions) != 0:
          user = ctx.message.mentions[0]
        else:
          user = ctx.message.author
    sql = "SELECT name,time,nickname,server FROM `names` WHERE id={0}"
    sql = sql.format(user.id)
    self.cursor.execute(sql)
    result = self.cursor.fetchall()
    if len(result) == 0:
      await self.bot.say(":no_entry: \"{0}\" does not have any name changes recorded!".format(user.name))
      return
    results = ""
    names_added = []
    for s in result:
      already_there = False
      s['name'] = s['name'].replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
      if len(names_added) != 0:
        for x in names_added:
          if x == s['name']:
            already_there = True
      if already_there:
        continue
      names_added.append(s['name'])
      if s['nickname'] == '1':
        if s['server'] == ctx.message.server.id:
          if s['name'] == user.nick:
            results += "**Current** [Nickname] \"{0}\" `{1}`\n".format(s['name'], s['time'])
          else:
            results += "[Nickname] \"{0}\" `{1}`\n".format(s['name'], s['time'])
      else:
        if s['name'] == user.name:
          results += "**Current** \"{0}\" `{1}`\n".format(s['name'], s['time'])
        else:
          results += "\"{0}\" `{1}`\n".format(s['name'], s['time'])
    idk = True
    if user.nick != None and user.nick not in names_added:
      results += "\"{0}\" `{1}`\n".format(user.nick, 'Current')
      idk = False
    if user.name not in names_added and idk:
      results += "\"{0}\" `{1}`\n".format(user.name, 'Current')
    if len(results) == 0:
      await self.bot.say(":no_entry: \"{0}\" does not have any name changes recorded!".format(user.name))
      return
    if len(results) >= 2500:
      await self.bot.say("**Name/Nickname Logs for** `{0}`\n".format(user.name))
      await self.bot.say("\n :warning: Results too long (>= 2500)\n**Uploaded**")
      await self.gist(ctx, 1, user.name, results)
      return
    await self.bot.say("**Name/Nickname Logs for** `{0}`\n".format(user.name)+results)

  @commands.command(pass_context=True, aliases=['servernames', 'sname'])
  async def snames(self, ctx):
    """Show all the logs the bot has of the users name or nickname"""
    server = ctx.message.server
    sql = "SELECT name,time FROM `server_names` WHERE id={0}"
    sql = sql.format(server.id)
    self.cursor.execute(sql)
    result = self.cursor.fetchall()
    if len(result) == 0:
      await self.bot.say(":no_entry: Server \"{0}\" does not have any name changes recorded!".format(server.name))
      return
    results = ""
    for s in result:
      s['name'] = s['name'].replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
      if s['name'] == ctx.message.server.name:
        results += "**Current** \"{0}\" `{1}`\n".format(s['name'], s['time'])
      else:
        results += "\"{0}\" `{1}`\n".format(s['name'], s['time'])
    if len(results) >= 2500:
      await self.bot.say("\n :warning: Results too long (>= 2500)\n**Uploaded**")
      await self.bot.say("**Server Name Logs for** `{0}`\n".format(server.name))
      await self.gist(ctx, 2, ctx.message.server.name, results)
      return
    await self.bot.say("**Server Name Logs for** `{0}`\n".format(server.name)+results)

  async def on_member_update(self, before, after):
    if before == self.bot.user:
      return
    time = strftime("%m-%d-%Y|%I:%M (EST)")
    if before.name != after.name:
      if before.name == after.name:
        return
      check = 'SELECT * FROM `names` WHERE id={0}'
      check = check.format(before.id)
      self.cursor.execute(check)
      if len(self.cursor.fetchall()) == 0:
        sql = "INSERT INTO `names` (`id`, `name`, `nickname`, `time`, `server`) VALUES (%s, %s, %s, %s, %s)"
        self.cursor.execute(sql, (before.id, before.name, '0', time, before.server.id))
        self.connection.commit()
      sql = "INSERT INTO `names` (`id`, `name`, `nickname`, `time`, `server`) VALUES (%s, %s, %s, %s, %s)"
      self.cursor.execute(sql, (before.id, after.name, '0', time, before.server.id))
      self.connection.commit()
    if before.nick != None or (before.nick == None and after.nick != None):
      if before.nick != None:
        if before.nick == after.nick:
          return
        if after.nick == None:
          return
      sql = "INSERT INTO `names` (`id`, `name`, `nickname`, `time`, `server`) VALUES (%s, %s, %s, %s, %s)"
      self.cursor.execute(sql, (before.id, after.nick, '1', time, before.server.id))
      self.connection.commit()

  async def on_server_update(self, before, after):
    if before == self.bot.user:
      return
    time = strftime("%m-%d-%Y|%I:%M (EST)")
    if before.name != after.name:
      check = 'SELECT * FROM `server_names` WHERE id={0}'
      check = check.format(before.id)
      self.cursor.execute(check)
      if len(self.cursor.fetchall()) == 0:
        sql = "INSERT INTO `server_names` (`id`, `name`, `time`) VALUES (%s, %s, %s)"
        self.cursor.execute(sql, (before.id, before.name, time))
        self.connection.commit()
      sql = "INSERT INTO `server_names` (`id`, `name`, `time`) VALUES (%s, %s, %s)"
      self.cursor.execute(sql, (before.id, after.name, time))
      self.connection.commit()

def setup(bot):
  bot.add_cog(Changes(bot))
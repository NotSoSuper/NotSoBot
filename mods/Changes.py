import asyncio
import discord
import pymysql
from time import strftime
from discord.ext import commands
from utils import checks

connection = pymysql.connect(host='',
                     user='',
                     password='',
                     db='',
                     charset='',
                     cursorclass=pymysql.cursors.DictCursor)
cursor = connection.cursor()

class Changes():
  def __init__(self, bot):
    self.bot = bot

  @commands.command(pass_context=True, aliases=['name', 'namelogs'])
  async def names(self, ctx, user:discord.User=None):
    """Show all the logs the bot has of the users name or nickname"""
    if user == None:
      user = ctx.message.author
    sql = "SELECT name,time,nickname FROM `names` WHERE id={0}"
    sql = sql.format(user.id)
    cursor.execute(sql)
    result = cursor.fetchall()
    if len(result) == 0:
      await self.bot.say("\"{0}\" does not have any name changes recorded!".format(user.name))
      return
    results = ""
    for s in result:
      s['name'] = s['name'].replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
      if s['nickname'] == '1':
        results += "[Nickname] \"{0}\" `{1}`\n".format(s['name'], s['time'])
      else:
        results += "\"{0}\" `{1}`\n".format(s['name'], s['time'])
    if len(results) >= 2500:
      results = results[:2400]
      results += "\n :warning: Results Truncated (>= 2500)"
    await self.bot.say("**Name/Nickname Logs for** `{0}`\n".format(user.name)+results)

  @commands.command(pass_context=True, aliases=['servernames', 'sname'])
  async def snames(self, ctx):
    """Show all the logs the bot has of the users name or nickname"""
    server = ctx.message.server
    sql = "SELECT name,time FROM `server_names` WHERE id={0}"
    sql = sql.format(server.id)
    cursor.execute(sql)
    result = cursor.fetchall()
    if len(result) == 0:
      await self.bot.say("Server \"{0}\" does not have any name changes recorded!".format(server.name))
      return
    results = ""
    for s in result:
      s['name'] = s['name'].replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
      results += "\"{0}\" `{1}`\n".format(s['name'], s['time'])
    if len(results) >= 2500:
      results = results[:2400]
      results += "\n :warning: Results Truncated (>= 2500)"
    await self.bot.say("**Server Name Logs for** `{0}`\n".format(server.name)+results)

  async def on_member_update(self, before, after):
    if before == self.bot.user:
      return
    time = strftime("%m-%d-%Y|%I:%M (EST)")
    if before.name != after.name:
      if before.name == after.name:
        return
      sql = "INSERT INTO `names` (`id`, `name`, `nickname`, `time`) VALUES (%s, %s, %s, %s)"
      cursor.execute(sql, (before.id, after.name, '0', time))
      connection.commit()
    if before.nick != None or (before.nick == None and after.nick != None):
      if before.nick != None:
        if before.nick == after.nick:
          return
        if after.nick == None:
          return
      sql = "INSERT INTO `names` (`id`, `name`, `nickname`, `time`) VALUES (%s, %s, %s, %s)"
      cursor.execute(sql, (before.id, after.nick, '1', time))
      connection.commit()

  async def on_server_update(self, before, after):
    if before == self.bot.user:
      return
    time = strftime("%m-%d-%Y|%I:%M (EST)")
    if before.name != after.name:
      sql = "INSERT INTO `server_names` (`id`, `name`, `time`) VALUES (%s, %s, %s)"
      cursor.execute(sql, (before.id, after.name, time))
      connection.commit()
    else:
      return

def setup(bot):
  bot.add_cog(Changes(bot))
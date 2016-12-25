import discord
import asyncio
import random
import re
import sys, linecache
from discord.ext import commands
from mods.cog import Cog
from utils import checks

#thanks swadicalrag for the markov module

class Markov(Cog):
  def __init__(self, bot):
    super().__init__(bot)
    self.cursor = bot.mysql.cursor
    self.cache = {}
    self.files_path = bot.path.files
    self.servers = ['110373943822540800']
    self.users = {'130070621034905600': '110373943822540800'}

  async def add_markov(self, path, txt):
    split = re.split(r"\s+", txt)
    for s in split:
      if len(s) >= 200:
        split.remove(s)
    msg = ' '.join(split).replace('`', '').replace("'", r"\'").replace(':', '').replace('\\', r'\\').replace('{', r'\{').replace('}', r'\}')
    learn_code = "markov.learn(`{0}`);".format(msg)
    code = "var markov_ultra = require('markov-ultra');var markov = new markov_ultra['default']('{0}', 6000000000);{1}".format(path, learn_code)
    await self.bot.run_process(['node', '-e', code])

  async def on_message(self, message):
    if message.channel.is_private:
      return
    elif message.author.bot or message.content.startswith(('!', '.', '!!', '`', '-', '=', ',', '/', '?')):
      return
    if message.server.id in self.servers:
      path = self.files_path('markov/{0}/'.format(message.server.id))
      await self.add_markov(path, message.content)
    if message.author.id in self.users.keys() and self.users[message.author.id] == message.server.id:
      path = self.files_path('markov/{0}_{1}/'.format(message.author.id, message.server.id))
      await self.add_markov(path, message.content)

  @commands.group(pass_context=True, aliases=['mark', 'm'], no_pm=True, invoke_without_command=True)
  async def markov(self, ctx, *, text:str=None):
    for m in ctx.message.mentions:
      user = m
      text = text.replace(user.mention, '')
      break
    else:
      user = False
    if user:
      if user.id not in self.users.keys():
        return
      elif self.users[user.id] != ctx.message.server.id:
        return
    if ctx.message.server.id not in self.servers:
      return
    path = self.files_path('markov/{0}/'.format('{0}_{1}'.format(ctx.message.author.id, ctx.message.server.id) if user else ctx.message.server.id))
    code = "var markov_ultra = require('markov-ultra');var markov = new markov_ultra['default']('{0}', 6000000000);console.log(markov.generate(2, 2000{1}))".format(path, ', `{0}`'.format(text) if text else '')
    result = await self.bot.run_process(['node', '-e', code], True)
    if result and result != '' and result != '\n':
      await self.bot.say(str(result).replace('http//', 'http://').replace('https//', 'https://').replace('\\\\', '\\'))
    else:
      await self.bot.say(':warning: **Markov Failed**.')

  @markov.command(name='generate', pass_context=True)
  @checks.is_owner()
  async def markov_generate(self, ctx, user:str=None):
    try:
      _x = await self.bot.send_message(ctx.message.channel, 'ok, this ~~might~~ will take a while')
      if user:
        user = self.bot.funcs.find_member(ctx.message.server, user, 2)
        if not user:
          await self.bot.say('Invalid User.')
          return
      markov_path = self.files_path('markov/{0}/'.format('{0}_{1}'.format(ctx.message.author.id, ctx.message.server.id) if user else ctx.message.server.id))
      if user:
        code_path = self.files_path('markov/generated/{0}.js'.format(user.name.lower()))
        sql = 'SELECT * FROM `messages` WHERE server={0} AND user_id={1} LIMIT 60000'.format(ctx.message.server.id, user.id)
      else:
        code_path = self.files_path('markov/generated/{0}.js'.format(ctx.message.server.name.lower()))
        sql = 'SELECT * FROM `messages` WHERE server={0} LIMIT 400000'.format(ctx.message.server.id)
      await self.bot.edit_message(_x, 'Fetching messages.')
      result = self.cursor.execute(sql).fetchall()
      await self.bot.edit_message(_x, 'Generating code.')
      msgs = []
      for x in result:
        if x['message'].startswith(('!', '.', '!!', '`', '-', '=', ',', '/', '?')):
          continue
        user = ctx.message.server.get_member(x['user_id'])
        if user and user.bot:
          continue
        msgs.append(x['message'])
      learn_code = []
      for msg in msgs:
        if msg == '':
          continue
        split = re.split(r"\s+", msg)
        for s in split:
          if len(s) >= 200:
            split.remove(s)
        msg = ' '.join(split).replace('`', '').replace("'", r"\'").replace(':', '').replace('\\', r'\\').replace('{', r'\{').replace('}', r'\}')
        learn_code.append("markov.learn(`{0}`);".format(msg))
      code = """'use strict';
var markov_ultra = require('markov-ultra');
var markov = new markov_ultra['default']('{0}', 6000000000);
{1}
""".format(markov_path, '\n'.join(learn_code))
      await self.bot.edit_message(_x, 'Code generated, saving.')
      f = open(code_path, 'w')
      f.write(code)
      f.close()
      await self.bot.edit_message(_x, ':white_check_mark: Done, `{0}`'.format(code_path))
    except:
      exc_type, exc_obj, tb = sys.exc_info()
      f = tb.tb_frame
      lineno = tb.tb_lineno
      filename = f.f_code.co_filename
      linecache.checkcache(filename)
      line = linecache.getline(filename, lineno, f.f_globals)
      await self.bot.say('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

def setup(bot):
  bot.add_cog(Markov(bot))
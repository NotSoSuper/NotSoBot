import asyncio
import sys
import os
import execjs
import aiohttp
import urllib.request
import traceback
import json
import discord
import time
import copy
import re
import subprocess
import io
import requests
import random
from datetime import datetime
from selenium import webdriver
from depot.manager import DepotManager
from sys import argv, path
from discord.message import Message
from discord.user import User
from discord.ext import commands
from discord.enums import Status
from utils import checks
from re import search

cool = "```xl\n{0}\n```"
code = "```py\n{0}\n```"
color_roles = ['red', 'green', 'blue', 'purple', 'orange', 'black', 'white', 'cyan', 'lime', 'pink', 'yellow', 'lightred', 'lavender', 'salmon', 'darkblue', 'darkpurple']

class Utils():
  def __init__(self,bot):
    self.bot = bot

  @commands.command(pass_context=True)
  async def status(self, ctx, *, status:str):
      """changes bots status"""
      if status != ():
          await self.bot.change_status(discord.Game(name="{0}".format(status)))
      await self.bot.say("ok, status changed to ``" + status + "``")

  @commands.command(pass_context=True)
  @checks.is_owner()
  async def say(self, ctx, *, text:str):
      """have me say something (owner only cuz exploits)???"""
      await self.bot.say(text)

  @commands.command(pass_context=True)
  async def evaljs(self, *, code:str):
      """eval JS code in Node.JS"""
      code_clean = "{0}".format(code.strip("```"))
      node = execjs.get("Node")
      execute = node.eval(code_clean)
      try:
          result = node.eval(code_clean)
          await self.bot.say(code.format(result))
      except execjs.ProgramError as e:
          await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  @commands.command(pass_context=True)
  @checks.is_owner()
  async def loop(self, ctx, times : int, *, command):
      """Loop a command a x times."""
      try:
        msg = copy.copy(ctx.message)
        msg.content = command
        for i in range(times):
            await self.bot.process_commands(msg)
      except Exception as e:
          await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  @commands.command(pass_context=True)
  async def ping(self, ctx):
      """Ping the bot server."""
      try:
          pingtime = time.time()
          pingmsg = await self.bot.say("ok, pinging.")
          ping = time.time() - pingtime
          await self.bot.edit_message(pingmsg, "ok, it took %.01f" % (ping) + " seconds to ping the server!\nlook how slow python is")
      except Exception as e:
          await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  color_roles = ['red', 'green', 'blue', 'purple', 'orange', 'black', 'white', 'cyan', 'lime', 'pink', 'yellow', 'lightred', 'lavender', 'salmon', 'darkblue', 'darkpurple']
  @commands.command(pass_context=True, no_pm=True)
  @commands.bot_has_permissions(manage_roles=True)
  async def color(self, ctx, color:str=None):
      """Set your color!"""
      try:
        if ctx.message.server is None: return
        if color is None:
          await self.bot.say("You didn\'t input a color, here\'s a list\n```{0}```\nUse .color <color_name>".format(", ".join(color_roles)))
          return
        color = color.lower()
        roles = list((map(str, ctx.message.author.roles)))
        server_roles = list((map(str, ctx.message.server.roles)))
        server_color_roles = [i for e in server_roles for i in color_roles if e == i]
        if len(server_color_roles) != len(color_roles):
          await self.bot.say(":warning: Server either does not have color roles or all the bots color roles\nAsk an Administrator to run the addcolors command\nor make sure you have all the roles in the colors command.")
          return
        role = discord.utils.find(lambda r: r.name.startswith(color), list(ctx.message.server.roles))
        fix = list(set(' '.join(map(str, ctx.message.author.roles)).split(' ')) & set(color_roles))
        fix.append("aaa")
        erole = discord.utils.find(lambda r: r.name.startswith(fix[0]), list(ctx.message.server.roles))
        if any([color == x for x in color_roles]) == False and color != "none":
          await self.bot.say("You have input an invalid color, here\'s a list\n```{0}```\nUse .color <color_name>".format(", ".join(color_roles)))
          return
        if color != "none":
          if erole != None:
            await self.bot.remove_roles(ctx.message.author, erole)
            await asyncio.sleep(0.25)
            await self.bot.add_roles(ctx.message.author, role)
            await self.bot.say("Changing {0}'s color to `{1}`".format(ctx.message.author.mention, color))
          else:
            await asyncio.sleep(0.25)
            await self.bot.add_roles(ctx.message.author, role)
            await self.bot.say("Added color `{0}` to {1}".format(color, ctx.message.author.mention))
        elif color == "none" and any([roles == x for x in color_roles]):
          await asyncio.sleep(0.25)
          await self.bot.remove_roles(ctx.message.author, erole)
          await self.bot.say("Removed color from {0}".format(ctx.message.author.mention))
        else:
          if erole != None:
            await asyncio.sleep(0.25)
            await self.bot.remove_roles(ctx.message.author, erole)
            await self.bot.say("Removed color from {0}".format(ctx.message.author.mention))
          else:
            await self.bot.say("You don't have a color to remove!")
      except Exception as e:
        await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  @commands.command(pass_context=True)
  @commands.bot_has_permissions(manage_roles=True)
  async def uncolor(self, ctx):
      """Removes color if set."""
      try:
        if ctx.message.server is None: return
        roles = list((map(str, ctx.message.author.roles)))
        server_roles = list((map(str, ctx.message.server.roles)))
        server_color_roles = [i for e in server_roles for i in color_roles if e == i]
        if len(server_color_roles) != len(color_roles):
          await self.bot.say(":warning: Server either does not have color roles or all the bots color roles\nAsk an Administrator to run the addcolors command\nor make sure you have all the roles in the colors command.")
          return
        fix = list(set(' '.join(map(str, ctx.message.author.roles)).split(' ')) & set(color_roles))
        fix.append("aaa")
        erole = discord.utils.find(lambda r: r.name.startswith(fix[0]), list(ctx.message.server.roles))
        if erole != None:
          await self.bot.remove_roles(ctx.message.author, erole)
          await self.bot.say("ok, removed color `{0}` from {1}".format(erole, ctx.message.author.mention))
        else:
          await self.bot.say("You don't have a color to remove!")
      except Exception as e:
          await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  @commands.command(pass_context=True)
  @commands.bot_has_permissions(manage_roles=True)
  async def colors(self, ctx):
      """Returns color roles available to use in '.color' command."""
      if ctx.message.server is None: return
      await self.bot.say("Role Colors Available\n```{0}```\nUse .color <color_name> to set your color!".format(", ".join(color_roles)))

  @commands.command(pass_context=True)
  @commands.bot_has_permissions(manage_roles=True)
  @checks.admin_or_perm(manage_roles=True)
  async def addcolor(self, ctx, name, color:discord.Colour):
      """Add a color role with the inputted name and Hex Color"""
      try:
          if ctx.message.server is None: return
          roles = list(map(str, ctx.message.server.roles))
          permissions = discord.Permissions.none()
          for s in roles:
            if re.search(r'^' + s + r'$', name):
              await self.bot.say("There's already a role with this name!")
              return
          await self.bot.create_role(server=ctx.message.server, permissions=permissions, name=name, color=color)
          await self.bot.say("Added role with name `{0}` and color `{1}`".format(name, color))
      except Exception as e:
          await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  @commands.command(pass_context=True)
  @checks.admin_or_perm(manage_roles=True)
  async def addcolors(self, ctx):
      """Add color roles to current server"""
      try:
        server_roles = list((map(str, ctx.message.server.roles)))
        server_color_roles = [i for e in server_roles for i in color_roles if e == i]
        if len(server_color_roles) == len(color_roles):
          await self.bot.say(":warning: Server already has the color roles!")
          return
        color = discord.Colour(int("FF0000", 16))
        color2 = discord.Colour.green()
        color3 = discord.Colour(int("9E00FF", 16))
        color4 = discord.Colour.blue()
        color5 = discord.Colour.orange()
        color6 = discord.Colour(int("0F0000", 16))
        color7 = discord.Colour(int("FFFFFF", 16))
        color8 = discord.Colour(int("08F8FC", 16))
        color9 = discord.Colour(int("00FF00", 16))
        color10 = discord.Colour(int("FF69B4", 16))
        color11 = discord.Colour(int("FBF606", 16))
        color12 = discord.Colour(int("FF4C4C", 16))
        color13 = discord.Colour(int("D1D1FF", 16))
        color14 = discord.Colour(int("FFA07A", 16))
        color15 = discord.Colour(int("002EFF", 16))
        color16 = discord.Colour(int("570679", 16))
        permissions = discord.Permissions.none()
        await self.bot.create_role(server=ctx.message.server, permissions=permissions, name='red', color=color)
        await asyncio.sleep(0.4)
        await self.bot.create_role(server=ctx.message.server, permissions=permissions, name='green', color=color2)
        await asyncio.sleep(0.4)
        await self.bot.create_role(server=ctx.message.server, permissions=permissions, name='purple', color=color3)
        await asyncio.sleep(0.4)
        await self.bot.create_role(server=ctx.message.server, permissions=permissions, name='blue', color=color4)
        await asyncio.sleep(0.4)
        await self.bot.create_role(server=ctx.message.server, permissions=permissions, name='orange', color=color5)
        await asyncio.sleep(0.4)
        await self.bot.create_role(server=ctx.message.server, permissions=permissions, name='black', color=color6)
        await asyncio.sleep(0.4)
        await self.bot.create_role(server=ctx.message.server, permissions=permissions, name='white', color=color7)
        await asyncio.sleep(0.4)
        await self.bot.create_role(server=ctx.message.server, permissions=permissions, name='cyan', color=color8)
        await asyncio.sleep(0.4)
        await self.bot.create_role(server=ctx.message.server, permissions=permissions, name='lime', color=color9)
        await asyncio.sleep(0.4)
        await self.bot.create_role(server=ctx.message.server, permissions=permissions, name='pink', color=color10)
        await asyncio.sleep(0.4)
        await self.bot.create_role(server=ctx.message.server, permissions=permissions, name='yellow', color=color11)
        await asyncio.sleep(0.4)
        await self.bot.create_role(server=ctx.message.server, permissions=permissions, name='lightred', color=color12)
        await asyncio.sleep(0.4)
        await self.bot.create_role(server=ctx.message.server, permissions=permissions, name='lavender', color=color13)
        await asyncio.sleep(0.4)
        await self.bot.create_role(server=ctx.message.server, permissions=permissions, name='salmon', color=color14)
        await asyncio.sleep(0.4)
        await self.bot.create_role(server=ctx.message.server, permissions=permissions, name='darkblue', color=color15)
        await asyncio.sleep(0.4)
        await self.bot.create_role(server=ctx.message.server, permissions=permissions, name='darkpurple', color=color16)
        await self.bot.say("Added colors (16)\n```{0}```".format(", ".join(color_roles)))
        await self.bot.say("You might need to re-order the new color ranks to the top of the roles\nif they are not working!")
      except Exception as e:
        await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  @commands.command(pass_context=True)
  async def mentions(self, ctx, max_messages:int=1500, idk=None):
    """Searches through inputed amount (Max 1500) of bot messages to find any mentions for you.\n Results sent via PM."""
    try:
        count = max_messages
        found = False
        if max_messages > 1500:
            await self.bot.say("2 many messages (<= 1500)")
            return
        if max_messages == 0:
            await self.bot.say("Please input a number of messages to search through!\n Ex: `.mentions 20` searches through 20 messages if you were mentioned.")
        if max_messages > 0:
            await self.bot.say("Sending results over PM `{0}`".format(ctx.message.author.name))
        async for message in self.bot.logs_from(ctx.message.channel, limit=max_messages):
            count = count - 1
            if ctx.message.author.mention in message.content:
                found = True
                await self.bot.send_message(ctx.message.author, "{0} has mentioned you in \"{1}\"\nTime: `{2}`".format(message.author.mention, message.content, message.timestamp))
            elif "<@!" + ctx.message.author.id + ">" in message.content:
                found = True
                await self.bot.send_message(ctx.message.author, "{0} has mentioned you in \"{1}\"\nTime: `{2}`".format(message.author.mention, message.content, message.timestamp))
            elif idk != None and "@everyone" in message.content:
                found = True
                await self.bot.send_message(ctx.message.author, "{0} has mentioned you in \"1}\"\nTime: `{2}`".format(message.author.mention, message.content, message.timestamp))
            elif idk != None and "@here" in message.content:
                found = True
                await self.bot.send_message(ctx.message.author, "{0} has mentioned you in \"{1}\"\nTime: `{2}`".format(message.author.mention, message.content, message.timestamp))
            elif count == 0 and found == False:
                await self.bot.send_message(ctx.message.author, "No messages found with {0} mentioned \nwithin the given max message search amount!".format(ctx.message.author.mention))
    except Exception as e:
        await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  @commands.command(pass_context=True)
  async def search(self, ctx, max_messages:int=None, *, text:str):
      """Searches through inputed amount (Max 1500) of bot messages to\n find the text you inputed.\n Results sent via PM.\n Ex: '.search 10 text'"""
      try:
          if max_messages == None:
              await self.bot.say("Please input a number of messages to search through!\n Ex: `.text 20 TEXT` searches through 20 messages with the text you inputed.")
              return
          count = max_messages
          found = False
          text = text.lower()
          if max_messages > 1500:
              await self.bot.say("2 many messages (<= 1500)")
              return
          if max_messages > 0:
              await self.bot.say("Sending results over PM `{0}`".format(ctx.message.author.name))
          async for message in self.bot.logs_from(ctx.message.channel, limit=max_messages):
              count = count - 1
              if message.content != ctx.message.content and text in message.content.lower():
                  found = True
                  await self.bot.send_message(ctx.message.author, "`{0}` has been found in message \"{1}\"\nAuthor: `{2}`\nTime: `{3}`".format(text, message.content, message.author.name, message.timestamp))
              elif count == 0 and found == False:
                  await self.bot.send_message(ctx.message.author, "No messages found with `{0}` \nwithin the given max message search amount!".format(text))
      except Exception as e:
          await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  @commands.command(pass_context=True)
  async def gist(self, ctx, *, content:str):
      """Upload inputed text to gist.github.com"""
      gist = {
          'description': 'Uploaded from NotSoSuper\'s Bot by {0} <{1}>.'.format(ctx.message.author.name, ctx.message.author.id),
          'public': True,
          'files': {
              'discord.py': {
                  'content': str(content)
              }
          }
      }
      headers = {'Authorization': 'token a6221d918b1d5806163061881106f4cb33ed593c'}
      async with aiohttp.post('https://api.github.com/gists', data=json.dumps(gist), headers=headers) as gh:
          if gh.status != 201:
              await self.bot.say('Could not create gist.')
          elif len(content) > 500:
              js = await gh.json()
              await self.bot.say('Output too big. The gist URL: {0[html_url]}'.format(js))
          else:
              js = await gh.json()
              await self.bot.say('Uploaded to gist, URL: <{1[html_url]}>'.format(content, js))

  @commands.command(pass_context=True)
  @checks.is_owner()
  async def setavatar(self, ctx, url:str):
      """Changes the bots avatar.\nOwner only ofc."""
      try:
          location = "/root/discord/files/avatar.png"
          with aiohttp.ClientSession() as session:
              async with session.get(url) as resp:
                  data = await resp.read()
                  with open(location, "wb") as f:
                      f.write(data)
          avatar = open(location, "rb")
          await self.bot.edit_profile(avatar=avatar.read())
          await self.bot.say("Avatar has been changed to")
          await self.bot.send_file(ctx.message.channel, location)
          os.remove(location)
      except Exception as e:
          await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  @commands.command(pass_context=True)
  @checks.is_owner()
  async def setname(self, ctx, *, name:str):
      """Changes the bots name.\nOwner only ofc."""
      try:
          await self.bot.edit_profile(username=name)
          await self.bot.say("ok, username changed to `{0}`".format(name))
      except Exception as e:
          await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  #old/outdated
  sed_regex = re.compile(r"\/(.+?)\/(.+?)\/", re.IGNORECASE)
  @commands.command(pass_context=True)
  async def s(self, ctx, *, text:str=None):
      try:
          match = None
          found = False
          if text != None:
            match = self.sed_regex.match(text)
            if match:
              text_one = match.group(1)
              text_two = match.group(2).replace('@everyone', '@\u200beveryone')
          if match != None:
            async for message in self.bot.logs_from(ctx.message.channel, limit=20, before=ctx.message):
                if found == False and ".s" not in message.content and message.content.startswith("s/") == False and re.search(text_one, message.content):
                  found = True
                  msg = "{0}: {1}".format(message.author.name, re.sub(text_one, text_two, message.content))
          if found:
            await self.bot.say(msg)
          else:
            await self.bot.say("No messages found with `{0}`!".format(text_one))
      except Exception as e:
          await self.bot.say("Error: Invalid Syntax\n`.s /text to find/text to replace with/`")
          print(type(e).__name__ + ': ' + str(e))

  async def on_message(self, message):
    if message.content.startswith('s/'):
      try:
        log_before = message
        match = None
        found = False
        match = message.content.split('/')
        if match[0] != "s":
          return
        if len(match) != 1 and match[1] != '':
          text_one = match[1]
        else:
          await self.bot.send_message(message.channel, "Error: Invalid Syntax\n`.s /text to find (you are missing this)/text to replace with/`")
          return
        if len(match) >= 3:
          text_two = match[2].replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
        else:
          await self.bot.send_message(message.channel, "Error: Invalid Syntax\n`.s /text to find/text to replace with (you are missing this)/`")
          return
        if len(match) == 4:
          text_three = match[3]
        else:
          text_three = ''
        rand = str(random.randint(0, 100))
        path = '/root/discord/files/sed_{0}.txt'.format(rand)
        if text_three == '':
          cmd = ['sed', 's/{0}/{1}/g'.format(text_one, text_two), path]
        else:
          cmd = ['sed', 's/{0}/{1}/{2}'.format(text_one, text_two, text_three), path]
        async for message in self.bot.logs_from(message.channel, limit=20, before=log_before):
            if found == False and message.content.startswith('.s') == False and message.content.startswith('s/') == False and re.search(text_one, message.content):
              found = True
              open(path, 'w').close()
              with io.open(path, "a", encoding='utf8') as f:
                f.write(message.content)
                f.close()
              x = subprocess.check_output(cmd).decode()
              msg = "{0}: {1}".format(message.author.name, x)
        if found:
          await self.bot.send_message(message.channel, msg)
          os.remove(path)
        else:
          await self.bot.send_message(message.channel, "No messages found with `{0}`!".format(text_one))
      except Exception as e:
        await self.bot.send_message(message.channel, type(e).__name__ + ': ' + str(e))

  @commands.command(pass_context=True)
  async def screenshot(self, ctx, *, url:str):
      try:
          await self.bot.say("ok, processing")
          if "http" not in url:
            url = "https://" + url
          depot = DepotManager.get()
          driver = webdriver.PhantomJS()
          driver.set_window_size(1024, 768)
          driver.get(url)
          location = '/root/discord/files/screenshot.png'
          driver.save_screenshot(location)
          if os.path.getsize(location) <= 3150:
            await self.bot.say("No screenshot was able to be taken\n Most likely cloudflare blocked me.")
            return
          await self.bot.say("ok, here\'s a screenshot of `{0}`".format(url))
          await self.bot.send_file(ctx.message.channel, location)
      except Exception as e:
          await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  @commands.command()
  @checks.is_owner()
  async def announcement(self, *, message : str):
    servers = list(self.bot.servers)
    for server in servers:
      try:
        await self.bot.send_message(server, message)
      except discord.Forbidden:
        print('Cant send message to {0}'.format(server.name.encode('utf-8')))
        me = server.me
        def predicate(ch):
          text = ch.type == discord.ChannelType.text
          return text and ch.permissions_for(me).send_messages
        channel = discord.utils.find(predicate, server.channels)
        if channel is not None:
          await self.bot.send_message(channel, message)
      finally:
        print('Sent message to {0}'.format(server.name.encode('utf-8')))
        await asyncio.sleep(5)

  @commands.command(pass_context=True)
  async def complain(self, ctx, *, message:str):
    await self.bot.send_message(self.bot.get_channel("186704399677128704"), "User: {0}\nServer: `{1} <{2}>`\nChannel: `{3} <{4}>`\n Time: `{5}`\n Message: ```{6}```".format(ctx.message.author.mention, ctx.message.server.name, ctx.message.server.id, ctx.message.channel.name, ctx.message.channel.id, ctx.message.timestamp, message))
    await self.bot.say("ok, left complaint")

  # oauth_regex = r"^https:\/\/discordapp\.com\/oauth2\/authorize\?client_id=(\d+)"
  # @commands.command(pass_context=True, aliases=['addbot'])
  # @commands.bot_has_permissions(manage_server=True)
  # async def oauth(self, ctx, url:str):
  #   regex = re.compile(self.oauth_regex)
  #   match = regex.findall(url)
  #   if len(match) == 1:
  #     client_id = match[0]
  #   else:
  #     await self.bot.say(":exclamation: Invalid OAUTH URL")
  #     return
  #   oauth_url = "https://discordapp.com/oauth2/authorize?client_id={0}&scope=bot".format(client_id)
  #   payload = {"guild_id": ctx.message.server.id, "permissions": 0, "authorize": 'true'}
  #   headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0', 'path': '/api/oauth2/authorize?client_id={0}&scope=bot'.format(client_id), 'authority': 'discordapp.com', 'method': 'post', 'content-type': 'application/json', 'origin': 'https://discordapp.com', 'referer': oauth_url, 'authorization': self.bot.http.token}
  #   r = requests.post(oauth_url, data=payload, headers=headers)
  #   print(r.text)
  #   if discord.Server.get_member(ctx.message.server, user_id=client_id):
  #     bot_user = discord.Server.get_member(ctx.message.server, user_id=client_id)
  #     msg = "Name: {0}\n".format(bot_user.name)
  #     msg += "ID: {0}\n".format(bot_user.id)
  #     if bot_user.avatar:
  #       msg += "Avatar: {0}".format(bot_user.avatar_url)
  #     await self.bot.say(cool.format(msg)+":ok:")
  #   else:
  #     await self.bot.say(":warning: An Error has Occured While Attempting To Add The Bot")

def setup(bot):
    bot.add_cog(Utils(bot))
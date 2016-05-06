import asyncio
import sys
import os
import execjs
import aiohttp
import urllib.request
import traceback
import json
import discord
from sys import argv, path
from discord.message import Message
from discord.user import User
from discord.ext import commands
from discord.enums import Status
from utils import checks

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

  @commands.command()
  async def invite(self):
      """returns invite link for bot"""
      endpoint = "https://discordapp.com/api/oauth2/applications/@me"
      if self.bot.headers.get('authorization') is None:
          self.bot.headers['authorization'] = "Bot {}".format(settings.email)
      async with self.bot.session.get(endpoint, headers=self.bot.headers) as resp:
          data = await resp.json()
      url = discord.utils.oauth_url(data.get('id'))
      msg = 'Invite me to your server with this `url:` {0}'.format(url)
      await self.bot.say(msg)

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
  async def debug(self, ctx,*,code:str):
      """Evaluates code."""
      try:
          eva = eval(code)
          if code.lower().startswith("print"):
              eva
              await self.bot.say(eva)
          elif asyncio.iscoroutine(eva):
              await eva
          else:
              await self.bot.say(code.format(eva))
      except Exception as e:
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
          await self.bot.say(wrap.format(type(e).__name__ + ': ' + str(e)))

  color_roles = ['red', 'green', 'blue', 'purple', 'orange', 'black', 'white', 'cyan', 'lime', 'pink', 'yellow', 'lightred', 'lavender', 'salmon', 'darkblue', 'darkpurple']
  @commands.command(pass_context=True)
  async def color(self, ctx, color:str=None):
      """Set your color!"""
      try:
          if ctx.message.server is None: return
          if ctx.message.server.me.permissions_in(ctx.message.channel).manage_roles:
              if color is None:
                  await self.bot.say("You didn\'t input a color, here\'s a list\n```{0}```\nUse .color <color_name>".format(", ".join(color_roles)))
                  return
              color = color.lower()
              roles = list((map(str, ctx.message.author.roles)))
              role = discord.utils.find(lambda r: r.name.startswith(color), list(ctx.message.server.roles))
              fix = list(set(' '.join(map(str, ctx.message.author.roles)).split(' ')) & set(color_roles))
              fix.append("aaa")
              erole = discord.utils.find(lambda r: r.name.startswith(fix[0]), list(ctx.message.server.roles))
              if any(x in color for x in color_roles) == False and color != "none":
                  await self.bot.say("You have input an invalid color, here\'s a list\n```{0}```\nUse .color <color_name>".format(", ".join(color_roles)))
                  return
              if color != "none":
                  if erole != None:
                      await self.bot.remove_roles(ctx.message.author, erole)
                      await asyncio.sleep(0.5)
                      await self.bot.add_roles(ctx.message.author, role)
                      await self.bot.say("Changing {0}'s color to `{1}`".format(ctx.message.author.mention, color))
                  else:
                      await asyncio.sleep(0.5)
                      await self.bot.add_roles(ctx.message.author, role)
                      await self.bot.say("Added color `{0}` to {1}".format(color, ctx.message.author.mention))
              elif color == "none" and any(x in roles for x in color_roles):
                  await asyncio.sleep(0.5)
                  await self.bot.remove_roles(ctx.message.author, erole)
                  await self.bot.say("Removed color from {0}".format(ctx.message.author.mention))
              else:
                  if erole != None:
                      await asyncio.sleep(0.5)
                      await self.bot.remove_roles(ctx.message.author, erole)
                      await self.bot.say("Removed color from {0}".format(ctx.message.author.mention))
                  else:
                      await self.bot.say("You don't have a color to remove!")
          else:
              await self.bot.say("Sorry, this doesn't work on this server (No manage_roles Permission)!")
      except Exception as e:
          await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  @commands.command(pass_context=True)
  async def uncolor(self, ctx):
      """Removes color if set."""
      try:
          if ctx.message.server is None: return
          if ctx.message.server.me.permissions_in(ctx.message.channel).manage_roles:
              roles = ' '.join(map(str, ctx.message.author.roles))
              fix = list(set(' '.join(map(str, ctx.message.author.roles)).split(' ')) & set(color_roles))
              fix.append(" ")
              erole = discord.utils.find(lambda r: r.name.startswith(fix[0]), list(ctx.message.server.roles))
              if any(x in roles for x in color_roles) and erole != None:
                  await self.bot.remove_roles(ctx.message.author, erole)
                  await self.bot.say("ok, removed color `{0}` from {1}".format(erole, ctx.message.author.mention))
              else:
                  await self.bot.say("You don't have a color to remove!")
          else:
              await self.bot.say("Sorry, this doesn't work on this server (No manage_roles Permission)!")
      except Exception as e:
          await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  @commands.command(pass_context=True)
  async def colors(self, ctx):
      """Returns color roles available to use in '.color' command."""
      try:
          if ctx.message.server is None: return
          if ctx.message.server.me.permissions_in(ctx.message.channel).manage_roles:
              await self.bot.say("Role Colors Available\n```{0}```\nUse .color <color_name> to set your color!".format(", ".join(color_roles)))
          else:
              await self.bot.say("Sorry, this doesn't work on this server (No manage_roles Permission)!")
      except Exception as e:
          await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  @commands.command(pass_context=True)
  @checks.is_owner()
  async def addcolor(self, ctx, name, color:discord.Colour):
      """Add a color role with the inputted name and Hex Color"""
      try:
          if ctx.message.server is None: return
          roles = list(map(str, ctx.message.server.roles))
          permissions = discord.Permissions.none()
          if ctx.message.server.me.permissions_in(ctx.message.channel).manage_roles:
              for words in roles:
                  if re.search(r'^' + words + r'$', name):
                      await self.bot.say("There's already a role with this name!")
                      return
              await self.bot.create_role(server=ctx.message.server, permissions=permissions, name=name, color=color)
              await self.bot.say("Added role with name `{0}` and color `{1}`".format(name, color))
          else:
              await self.bot.say("Sorry, this doesn't work on this server (No manage_roles Permission)!")
      except Exception as e:
          await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  @commands.command(pass_context=True)
  @checks.is_owner()
  async def addcolors(self, ctx):
      """Add color roles to current server"""
      try:
        #STATIC CANCER
          if ctx.message.server.me.permissions_in(ctx.message.channel).manage_roles:  
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
          else:
              await self.bot.say("Sorry, this doesn't work on this server (No manage_roles Permission)!")          
      except Exception as e:
          await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  @commands.command(pass_context=True)
  async def mentions(self, ctx, max_messages=0):
    """Searches through inputed amount (Max 1000) of bot messages to find any mentions for you.\n Results sent via PM."""
    try:
        max_messages = int(max_messages)
        if max_messages > 1000:
            await self.bot.say("2 many messages")
        if max_messages == 0:
            await self.bot.say("Please input a number of messages to search through!\n Ex: `.mentions 20` searches through 20 messages if you were mentioned.")
        if max_messages > 0:
            await self.bot.say("Sending results over PM `{0}`".format(ctx.message.author.name))
        async for message in self.bot.logs_from(ctx.message.channel, limit=max_messages):
            count = max_messages - 1
            if ctx.message.author.mention in str(message.content):
                await self.bot.send_message(ctx.message.author, "{0} has mentioned you in ```{1}```".format(message.author.mention, str(message.content)))
            elif "<@!" + ctx.message.author.id + ">" in str(message.content):
                await self.bot.send_message(ctx.message.author, "{0} has mentioned you in ```{1}```".format(message.author.mention, str(message.content)))
            elif count == 0:
                await self.bot.send_message(ctx.message.author, "No messages found with {0} mentioned \nwithin the given max message search amount!".format(ctx.message.author.mention))
    except Exception as e:
        await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  @commands.command(pass_context=True)
  async def search(self, ctx, max_messages=0, *, text:str):
      """Searches through inputed amount (Max 1000) of bot messages to\n find the text you inputed.\n Results sent via PM.\n Ex: '.search 10 text'"""
      try:
          max_messages = int(max_messages)
          if max_messages > 1000:
              await self.bot.say("2 many messages")
          if max_messages == 0:
              await self.bot.say("Please input a number of messages to search through!\n Ex: `.text 20 TEXT` searches through 20 messages with the text you inputed.")
          if max_messages > 0:
              await self.bot.say("Sending results over PM `{0}`".format(ctx.message.author.name))
          async for message in self.bot.logs_from(ctx.message.channel, limit=max_messages):
              count = max_messages - 1
              if text in str(message.content):
                  await self.bot.send_message(ctx.message.author, "`{0}` has been found in message ```{1}```\nAuthor: `{2}`".format(text, str(message.content), message.author.name))
              elif count == 0:
                  await self.bot.send_message(ctx.message.author, "No messages found with `{0}` \nwithin the given max message search amount!".format(ctx.message.author.mention))
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
      headers = {'Authorization': 'token yourtoken'}
      async with aiohttp.post('https://api.github.com/gists', data=json.dumps(gist), headers=headers) as gh:
          if gh.status != 201:
              await self.bot.say('Could not create gist.')
          elif len(content) > 500:
              js = await gh.json()
              await self.bot.say('Output too big. The gist URL: {0[html_url]}'.format(js))
          else:
              js = await gh.json()
              await self.bot.say('Uploaded ```{0}``` to gist. The URL is: {1[html_url]}'.format(content, js))

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

def setup(bot):
    bot.add_cog(Utils(bot))
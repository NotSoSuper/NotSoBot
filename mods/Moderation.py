import asyncio
import traceback
import json
import discord
import pymysql
import time
import io
import random
import aiohttp
import re
import os
from datetime import datetime
from discord.ext import commands
from utils import checks

with open(os.path.join(os.getenv('discord_path', '~/discord/'), "utils/config.json")) as f:
  config = json.load(f)

cool = "```xl\n{0}\n```"
code = "```py\n{0}\n```"

class Moderation():
  def __init__(self,bot):
    self.bot = bot
    self.connection = bot.mysql.connection
    self.cursor = bot.mysql.cursor
    self.discord_path = bot.path.discord
    self.files_path = bot.path.files

  @commands.command(pass_context=True)
  @checks.mod_or_perm(manage_messages=True)
  async def clean(self, ctx, max_messages:int):
    """Removes inputed amount of bot messages."""
    if max_messages > 1500:
      await self.bot.say("2 many messages")
      return
    count = 0
    async for message in self.bot.logs_from(ctx.message.channel, limit=max_messages+1):
      if message.author == self.bot.user:
        asyncio.ensure_future(self.bot.delete_message(message))
        await asyncio.sleep(0.21)
        count += 1
    x = await self.bot.say("Removed `{0}` messages out of `{1}` searched messages".format(count, max_messages))
    await asyncio.sleep(10)
    try:
      await self.bot.delete_message(ctx.message)
    except:
      pass
    await self.bot.delete_message(x)

  @commands.group(pass_context=True, invoke_without_command=True, aliases=['purge', 'deletemessages'])
  @checks.mod_or_perm(manage_messages=True)
  async def prune(self, ctx, max_messages:int=100):
    """Delete inputed amount of messages in a channel."""
    if ctx.message.server.me.permissions_in(ctx.message.channel).manage_messages == False:
      await self.bot.say("Sorry, this doesn't work on this server (No manage_messages Permission)!")
      return
    if max_messages > 1500:
      await self.bot.say("2 many messages\nasshole")
      return
    message = ctx.message
    await self.bot.purge_from(ctx.message.channel, limit=max_messages)
    count = max_messages + 1
    x = await self.bot.say("ok, removed {0} messages".format(count))
    await asyncio.sleep(10)
    try:
      await self.bot.delete_message(ctx.message)
    except:
      pass
    await self.bot.delete_message(x)

  @prune.command(name='user', pass_context=True, aliases='u')
  @checks.mod_or_perm(manage_messages=True)
  async def _prune_user(self, ctx, max_messages:int, *users:discord.User):
    """Removes inputed amount of messages found of the inputed user."""
    if ctx.message.server.me.permissions_in(ctx.message.channel).manage_messages == False:
      await self.bot.say("Sorry, this doesn't work on this server (No manage_messages Permission)!")
      return
    if max_messages > 1500:
      await self.bot.say("2 many messages")
    for user in users:
      def m(k):
        return k.author == user
      deleted = await self.bot.purge_from(ctx.message.channel, limit=max_messages, check=m)
      if len(deleted) == 0:
        x = await self.bot.say("No messages found by {0} \nwithin the given max message search amount!".format(user.name))
        await asyncio.sleep(10)
        await self.bot.delete_message(x)
        return
      x = await self.bot.say("ok, removed `{0}` messages out of `{1}` searched for `{2}`".format(str(len(deleted)), str(max_messages), user.name))
      await asyncio.sleep(10)
      await self.bot.delete_message(x)
    try:
      await self.bot.delete_message(ctx.message)
    except:
      pass

  @commands.group(invoke_without_command=True, aliases=['unblacklist'])
  async def blacklist(self):
    """Blacklist base command"""
    await self.bot.say("**Blacklist Base Command**\nCommands: `user, channel`\nUser: Owner Only\n\nChannel: manage_server permission, call once to blacklist a channel, again to unblacklist.")

  @blacklist.command(name='user', pass_context=True)
  @checks.is_owner()
  async def _blacklist_user(self, ctx, user:discord.User):
    """Unblacklist a user.\nOwner only ofc."""
    if user.id == config["ownerid"]:
      await self.bot.say("what are you doing NotSoSuper?")
      return
    blacklist_path = self.discord_path('utils/blacklist.txt')
    if user.mention in open(blacklist_path).read():
      f = open(blacklist_path, 'r')
      a = f.read()
      f.close()
      data = a.replace(user.mention, "")
      f = open(blacklist_path, 'w')
      f.write(data)
      f.close()
      await self.bot.say("ok, unblacklisted {0}".format(user.mention))
    else:
      with open(blacklist_path, "a") as f:
        f.write(user.mention + "\n")
        f.close()
      await self.bot.say("ok, blacklisted {0}".format(user.mention))

  @blacklist.command(name='channel', pass_context=True)
  @checks.admin_or_perm(manage_server=True)
  async def _blacklist_channel(self, ctx, chan:discord.Channel=None):
    """Blacklists a channel from the bot."""
    if chan == None:
      chan = ctx.message.channel
    blacklist_path = self.discord_path('utils/cblacklist.txt')
    if chan.id in open(blacklist_path).read():
      with open(blacklist_path) as f:
        s = f.read().replace(chan.id + "\n", '')
      with open(blacklist_path, "w") as f:
        f.write(s)
      await self.bot.say("ok, unblacklisted channel {0.mention} `<{0.id}>`".format(chan))
    else:
      with open(blacklist_path, "a") as f:
        f.write('{0}\n'.format(chan.id))
        await self.bot.say("ok, blacklisted channel {0.mention} `<{0.id}>`".format(chan))

  @commands.command(pass_context=True)
  @checks.mod_or_perm(manage_messages=True)
  async def off(self, ctx, user:discord.User):
    if ctx.message.server.me.permissions_in(ctx.message.channel).manage_messages:
      pass
    else:
      await self.bot.say("Sorry, I do not have the manage_messages permission\n**Aborting**")
      return
    if user == self.bot.user:
      await self.bot.say("u cant turn me off asshole")
      return
    sql_check = "SELECT id FROM `muted` WHERE server={0} AND id={1}"
    sql_check = sql_check.format(ctx.message.server.id, user.id)
    self.cursor.execute(sql_check)
    check_result = self.cursor.fetchall()
    if len(check_result) == 0:
      pass
    else:
      await self.bot.say("{0} is already turned off!".format(user.mention))
      return
    sql = "INSERT INTO `muted` (`server`, `id`) VALUES (%s, %s)"
    self.cursor.execute(sql, (ctx.message.server.id, user.id))
    self.connection.commit()
    await self.bot.say("ok, tuned off {0}".format(user.mention))

  @commands.command(pass_context=True)
  @checks.mod_or_perm(manage_messages=True)
  async def on(self, ctx, user:discord.User):
    if ctx.message.server.me.permissions_in(ctx.message.channel).manage_messages:
      pass
    else:
      await self.bot.say("Sorry, I do not have the manage_messages permission\n**Aborting**")
      return
    if user == self.bot.user:
      await self.bot.say("thanks for trying to turn me on but u can\'t\nasshole")
      return
    sql_check = "SELECT id FROM `muted` WHERE server={0} AND id={1}"
    sql_check = sql_check.format(ctx.message.server.id, user.id)
    self.cursor.execute(sql_check)
    check_result = self.cursor.fetchall()
    if len(check_result) == 0:
      await self.bot.say("{0} is already turned on!".format(user.mention))
      return
    sql = "DELETE FROM `muted` WHERE server={0} AND id={1}"
    sql = sql.format(ctx.message.server.id, user.id)
    self.cursor.execute(sql)
    self.connection.commit()
    x = await self.bot.say("ok, turned on `{0}`".format(user.name))
    try:
      await self.bot.delete_message(ctx.message)
    except:
      pass
    await asyncio.sleep(10)
    await self.bot.delete_message(x)

  async def on_message(self, message):
    if message.author == self.bot.user:
      return
    if message.channel.is_private:
      return
    if message.server.me.permissions_in(message.channel).manage_messages == False:
      return
    sql = "SELECT id FROM `muted` WHERE server={0} AND id={1}"
    sql = sql.format(message.server.id, message.author.id)
    self.cursor.execute(sql)
    result = self.cursor.fetchall()
    if len(result) == 0:
      return
    if result[0]['id'] == message.author.id:
      try:
        await self.bot.delete_message(message)
      except:
        pass
    else:
      return

  @commands.command(pass_context=True)
  @checks.mod_or_perm(manage_messages=True)
  async def mute(self, ctx, *users:discord.User):
    """Mute a User"""
    if ctx.message.server.me.permissions_in(ctx.message.channel).manage_roles == False:
      await self.bot.say("Sorry, I do not have the manage_roles permission\n**Aborting**")
      return
    for user in users:
      try:
        overwrite = ctx.message.channel.overwrites_for(user)
        overwrite.send_messages = False
        await self.bot.edit_channel_permissions(ctx.message.channel, user, overwrite)
        await self.bot.say("ok, muted {0}".format(user))
      except discord.error.Forbidden:
        await self.bot.say(":no_entry: Bot does not have permission")
        return

  @commands.command(pass_context=True)
  @checks.mod_or_perm(manage_messages=True)
  async def unmute(self, ctx, *users:discord.User):
    """Unmute a User"""
    if ctx.message.server.me.permissions_in(ctx.message.channel).manage_roles == False:
      await self.bot.say("Sorry, I do not have the manage_roles permission\n**Aborting**")
      return
    for user in users:
      overwrite = ctx.message.channel.overwrites_for(user)
      overwrite.send_messages = True
      await self.bot.edit_channel_permissions(ctx.message.channel, user, overwrite)
      await self.bot.say("ok, unmuted {0}".format(user))

  @commands.command(pass_context=True)
  @checks.admin_or_perm(manage_server=True)
  async def createrole(self, ctx, *, role):
    """Create a role"""
    if ctx.message.server.me.permissions_in(ctx.message.channel).manage_roles == False:
      await self.bot.say("Sorry, I do not have the manage_roles permission\n**Aborting**")
      return
    await self.bot.create_role(ctx.message.server, name=role)
    await self.bot.say("ok, created the role `{0}`".format(role.name))

  @commands.command(pass_context=True)
  @checks.admin_or_perm(manage_server=True)
  async def addrole(self, ctx, role:discord.Role, *users:discord.User):
    """Add a role to x users"""
    if ctx.message.server.me.permissions_in(ctx.message.channel).manage_roles == False:
      await self.bot.say("Sorry, I do not have the manage_roles permission\n**Aborting**")
      return
    if len(users) == 0:
      await self.bot.say(":no_entry: You need to specify a user to give the role too.")
    idk = []
    for user in users:
      await self.bot.add_roles(user, role)
      idk.append(user.name)
    await self.bot.say("ok, gave user(s) `" + ", ".join(idk) + "` the role {0}".format(role.name))

  @commands.command(pass_context=True)
  @checks.admin_or_perm(manage_server=True)
  async def removerole(self, ctx, role:discord.Role, *users:discord.User):
    """Remove a role from x users"""
    if ctx.message.server.me.permissions_in(ctx.message.channel).manage_roles == False:
      await self.bot.say("Sorry, I do not have the manage_roles permission\n**Aborting**")
      return
    if len(users) == 0:
      await self.bot.say("You need to add a person to remove the role from!")
    idk = []
    for user in users:
      await self.bot.remove_roles(user, role)
      idk.append(user.name)
    await self.bot.say("ok, removed the role {0} from user(s) `{1}`".format(role.name, ', '.join(idk)))

  @commands.command(pass_context=True)
  @checks.admin_or_perm(manage_server=True)
  async def deleterole(self,ctx,*,role:discord.Role):
    """Delete a role"""
    if ctx.message.server.me.permissions_in(ctx.message.channel).manage_roles == False:
      await self.bot.say("Sorry, I do not have the manage_roles permission\n**Aborting**")
      return
    server = ctx.message.server
    await self.bot.delete_role(server,role)
    await self.bot.say("ok, deleted the role `{0}` from the server".format(role.name))

  @commands.command(pass_context=True)
  @checks.admin_or_perm(manage_server=True)
  async def leave(self,ctx):
    """bye"""
    await self.bot.say("bye faggots :wave:")
    await self.bot.leave_server(ctx.message.server)

  @commands.group(pass_context=True, invoke_without_command=True, aliases=['nickname'])
  @checks.mod_or_perm(manage_server=True)
  async def nick(self, ctx, nickname:str, *users:discord.User):
    """Change a user(s) nickname"""
    if ctx.message.server.me.permissions_in(ctx.message.channel).manage_nicknames == False:
      await self.bot.say("Sorry, I do not have the manage_nicknames permission\n**Aborting**")
      return
    for user in users:
      await self.bot.change_nickname(user, nickname)
      await self.bot.say("ok, changed the nickname of `{0}` to `{1}`".format(user.name, nickname))
      await asyncio.sleep(.21)

  @nick.command(name='mass', pass_context=True)
  @checks.admin_or_perm(manage_server=True)
  async def _nick_massnick(self, ctx, *, name:str):
    """Change everyones nickname"""
    if ctx.message.server.me.permissions_in(ctx.message.channel).manage_nicknames == False:
      await self.bot.say("Sorry, I do not have the manage_nicknames permission\n**Aborting**")
      return
    await self.bot.say("this might take a while, pls wait")
    count = 0
    for member in ctx.message.server.members:
      try:
        await self.bot.change_nickname(member, name)
      except:
        continue
      await asyncio.sleep(.21)
      count += 1
    await self.bot.say("ok, changed the nickname of `{0}` users to `{1}`".format(str(count), name))

  @nick.command(name='massunick', aliases=['revert', 'massun'], pass_context=True)
  @checks.admin_or_perm(manage_server=True)
  async def _nick_massunick(self, ctx):
    """Default every users nickname in the server"""
    if ctx.message.server.me.permissions_in(ctx.message.channel).manage_nicknames == False:
      await self.bot.say("Sorry, I do not have the manage_nicknames permission\n**Aborting**")
      return
    await self.bot.say("this might take a while, pls wait")
    count = 0
    for member in ctx.message.server.members:
      if member.nick:
        try:
          await self.bot.change_nickname(member,member.name)
        except:
          continue
        await asyncio.sleep(.21)
        count += 1
    await self.bot.say("ok, reset the nickname of `{0}` users".format(str(count), name))

  async def gist_logs(self, ctx, type:int, idk:str, content:str):
    if type == 1:
      gist = {
        'description': 'Message logs for Channel: "{2}" | \nUploaded from NotSoSuper\'s Bot by: {0} <{1}>.'.format(ctx.message.author.name, ctx.message.author.id, idk),
        'public': 'false',
        'files': {
            'channel_logs_{0}.txt'.format(idk): {
                'content': content
            }
        }
      }
    elif type == 2:
      gist = {
        'description': 'Message Logs for User: "{2}" | Channel: {3.name} <{3.id}> | \nUploaded from NotSoSuper\'s Bot by: {0} <{1}>.'.format(ctx.message.author.name, ctx.message.author.id, idk, ctx.message.channel),
        'public': 'false',
        'files': {
            'logs_{0}.txt'.format(idk): {
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

  mention_regex = re.compile(r'(<@((\!|\&)?[0-9]*?)>)')
  @commands.group(pass_context=True, invoke_without_command=True)
  @checks.mod_or_perm(manage_messages=True)
  async def logs(self, ctx, max_messages:int=500, channel:discord.Channel=None):
    """Returns gist and file of messages for current/a channel"""
    print("1")
    if max_messages > 2500:
      await self.bot.say("2 many messages (<= 2500)")
      return
    if channel == None:
      channel = ctx.message.channel
    count = 0
    rand = str(random.randint(0, 100))
    path = self.files_path("logs/clogs_{0}_{1}.txt".format(channel.name, rand))
    open(path, 'w').close()
    idk = True
    async for message in self.bot.logs_from(channel, limit=max_messages):
      with io.open(path, "a", encoding='utf8') as f:
        line = ''
        if idk:
          line += "Server: {0.name} <{0.id}>\n".format(message.server)
          line += "Channel: {0.name} <{0.id}>\n".format(message.channel)
          idk = False
        line += "Time: {0}\n".format(message.timestamp)
        line += "Author: {0.name} <{0.id}>\n".format(message.author)
        user = None
        if self.mention_regex.search(message.content):
          ss = self.mention_regex.search(message.content)
          mention_id = ss.group(2)
          if mention_id.startswith('!'):
            mention_id = mention_id.replace('!', '')
          for server in self.bot.servers:
            if user == None:
              user = discord.Server.get_member(server, user_id=mention_id)
            else:
              break
          if user != None:
            message.content = message.content.replace(ss.group(1), '{0.name}#{0.discriminator} (Discord mention converted)'.format(user))
        line += "Message: {0}\n\n".format(message.content)
        f.write(line)
        f.close()
      count += 1
    await self.gist_logs(ctx, 1, ctx.message.channel.name, open(path).read())
    await self.bot.send_file(ctx.message.channel, path, filename="logs_{0}.txt".format(ctx.message.channel.name), content="ok, here is a file/gist of the last `{0}` messages.".format(count))

  @logs.command(name="user", pass_context=True)
  @checks.mod_or_perm(manage_messages=True)
  async def _logs_user(self, ctx, max_messages:int=500, user:str=None, channel:discord.Channel=None):
    try:
      if max_messages > 2500:
        await self.bot.say("2 many messages (<= 2500)")
        return
      user_id = False
      if user == None:
        user = ctx.message.author
      else:
        if len(ctx.message.mentions) == 0:
          user_id = True
        else:
          user = ctx.message.mentions[0]
      server = ctx.message.server
      if channel == None:
        channel = ctx.message.channel
      count = 0
      rand = str(random.randint(0, 100))
      path = self.files_path("logs/logs_{0}_{1}.txt".format(user, rand))
      open(path, 'w').close()
      idk = True
      user_id_u = None
      async for message in self.bot.logs_from(channel, limit=max_messages):
        if user_id:
          if message.author.id != user:
            continue
        else:
          if message.author != user:
            continue
        if user_id:
          user_id_u = message.author
        with io.open(path, "a", encoding='utf8') as f:
          line = ''
          if idk:
            line += "Server: {0.name} <{0.id}>\n".format(message.server)
            line += "Channel: {0.name} <{0.id}>\n".format(message.channel)
            idk = False
          line += "Time: {0}\n".format(message.timestamp)
          line += "Author: {0.name} <{0.id}>\n".format(message.author)
          mention_user = None
          if self.mention_regex.search(message.content):
            ss = self.mention_regex.search(message.content)
            mention_id = ss.group(2)
            if mention_id.startswith('!'):
              mention_id = mention_id.replace('!', '')
            for server in self.bot.servers:
              if mention_user == None:
                mention_user = discord.Server.get_member(server, user_id=mention_id)
              else:
                break
            if mention_user != None:
              message.content = message.content.replace(ss.group(1), '{0.name}#{0.discriminator} (Discord mention converted)'.format(mention_user))
          line += "Message: {0}\n\n".format(message.content)
          f.write(line)
          f.close()
        count += 1
      if user_id_u:
        user = user_id_u
      if count == 0:
        await self.bot.say(":warning: No messages found within `{0}` searched for `{1}`!".format(max_messages, user))
        return
      await self.gist_logs(ctx, 2, user.name, open(path).read())
      await self.bot.send_file(ctx.message.channel, path, filename="logs_{0}.txt".format(user.name), content="ok, here is a file/gist of the last `{1}` messages for {0.name}#{0.discriminator}".format(user, count))
    except Exception as e:
      await self.bot.say(code.format(e))

  @commands.group(pass_context=True, invoke_without_command=True)
  @checks.mod_or_perm(manage_server=True)
  async def inv(self, ctx):
    """Create a Server Invite"""
    invite = await self.bot.create_invite(ctx.message.server)
    await self.bot.say(invite)

  @inv.command(name='delete', pass_context=True)
  @checks.mod_or_perm(manage_server=True)
  async def _inv_delete(self, ctx, invite:str):
    """Delete a Server Invite"""
    await self.bot.delete_invite(invite)
    await self.bot.say("ok, deleted/revoked invite")

  @inv.command(name='list', pass_context=True)
  @checks.mod_or_perm(manage_server=True)
  async def _inv_list(self, ctx):
    """List all Server Invites"""
    invites = await self.bot.invites_from(ctx.message.server)
    if len(invites) == 0:
      await self.bot.say(":warning: There currently no invites active.")
    else:
      await self.bot.say("Invites: {0}".format(", ".join(map(str, invites))))

  @inv.group(name='cserver', pass_context=True)
  @checks.is_owner()
  async def _inv_cserver(self, ctx, *, name:str):
    found = False
    for server in self.bot.servers:
      if name in server.name:
        for c in server.channels:
          s = c
          found = True
          break
    if found:
      try:
        invite = await self.bot.create_invite(s)
      except:
        await self.bot.say("no perms")
        return
      await self.bot.say(invite)
    else:
      await self.bot.say("no server found")

  @_inv_cserver.command(name='id', pass_context=True)
  @checks.is_owner()
  async def _inv_cserver_id(self, ctx, id:str):
    s = self.bot.get_server(id)
    invite = await self.bot.create_invite(s)
    await self.bot.say(invite)

  @commands.group(pass_context=True, invoke_without_command=True)
  @checks.mod_or_perm(manage_messages=True)
  async def pin(self, ctx, max_messages:int=1500, *, txt:str):
    """Attempt to find a Message by ID or Content and Pin it"""
    if ctx.message.server.me.permissions_in(ctx.message.channel).manage_messages == False:
      await self.bot.say("Sorry, this doesn't work on this server (No manage_messages Permission)!")
      return
    if max_messages > 1500:
      await self.bot.say("2 many messages (<= 2500)")
      return
    async for message in self.bot.logs_from(ctx.message.channel, before=ctx.message, limit=max_messages):
      if message.id == txt:
        try:
          await self.bot.pin_message(message)
        except:
          await self.bot.say(":warning: Could not pin message\nNo permission")
          return
        else:
          await self.bot.say(":ok: Pinned Message with Given ID")
          return
      elif txt in message.content:
        try:
          await self.bot.pin_message(message)
        except:
          await self.bot.say(":warning: Could not pin message\nNo permission")
          return
        else:
          await self.bot.say(":ok: Pinned Message with given text in it!".format(txt))
          return
      else:
        continue
    await self.bot.say(":exclamation: No message found with ID or Content given!")

  @pin.command(name='date', pass_context=True)
  async def _pin_date(self, ctx, date:str, channel:discord.Channel=None):
    """Pin a message after the specified date\nUse the \"pin first\" command to pin the first message!"""
    if ctx.message.server.me.permissions_in(ctx.message.channel).manage_messages == False:
      await self.bot.say("Sorry, this doesn't work on this server (No manage_messages Permission)!")
      return
    _date = None
    fmts = ('%Y/%m/%d', '%Y-%m-%d', '%m-%d-%Y', '%m/%d/%Y')
    for s in fmts:
      try:
        _date = datetime.strptime(date, s)
      except ValueError:
        continue
    if _date == None:
      await self.bot.say(':warning: Cannot convert to date. Formats: `YYYY/MM/DD, YYYY-MM-DD, MM-DD-YYYY, MM/DD/YYYY`')
      return
    if channel == None:
      channel = ctx.message.channel
    async for message in self.bot.logs_from(channel, after=_date, limit=1):
      try:
        await self.bot.pin_message(message)
      except:
        await self.bot.say(":warning: Could not pin message\nNo permission")
        return
      else:
        await self.bot.say(":ok: Pinned Message with date \"{0}\"!".format(str(_date)))
        return
    await self.bot.say(":exclamation: No message found with date given!")

  @pin.command(name='before', pass_context=True)
  async def _pin_before(self, ctx, date:str, max_messages:int=1500, *, txt:str):
    """Pin a message before a certain date"""
    if ctx.message.server.me.permissions_in(ctx.message.channel).manage_messages == False:
      await self.bot.say("Sorry, this doesn't work on this server (No manage_messages Permission)!")
      return
    if max_messages > 1500:
      await self.bot.say("2 many messages (<= 1500")
      return
    _date = None
    fmts = ('%Y/%m/%d', '%Y-%m-%d', '%m-%d-%Y', '%m/%d/%Y')
    for s in fmts:
      try:
        _date = datetime.strptime(date, s)
      except ValueError:
        continue
    if _date == None:
      await self.bot.say(':warning: Cannot convert to date. Formats: `YYYY/MM/DD, YYYY-MM-DD, MM-DD-YYYY, MM/DD/YYYY`')
      return
    if channel == None:
      channel = ctx.message.channel
    async for message in self.bot.logs_from(channel, before=_date, limit=max_messages):
      if txt in message.content:
        try:
          await self.bot.pin_message(message)
        except:
          await self.bot.say(":warning: Could not pin message\nNo permission")
          return
        else:
          await self.bot.say(":ok: Pinned Message before date \"{0}\" with given text!".format(str(_date)))
          return
    await self.bot.say(":exclamation: No message found with given text before date given!")

  @pin.command(name='first', aliases=['firstmessage'], pass_context=True)
  async def _pin_first(self, ctx, channel:discord.Channel=None):
    """Pin the first message in current/specified channel!"""
    if ctx.message.server.me.permissions_in(ctx.message.channel).manage_messages == False:
      await self.bot.say("Sorry, this doesn't work on this server (No manage_messages Permission)!")
      return
    if channel == None:
      channel = ctx.message.channel
    date = str(ctx.message.channel.created_at).split()[0]
    _date = datetime.strptime(date, '%Y-%m-%d')
    async for message in self.bot.logs_from(channel, after=_date, limit=1):
      try:
        await self.bot.pin_message(message)
      except:
        await self.bot.say(":warning: Could not pin first message\nNo permission")
        return
      else:
        if len(message.content) > 2000:
          message.content = message.content[:2000]+"\n:warning: Message Truncated (<= 2000)"
        message.content = message.content.replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
        if len(message.mentions) != 0:
          for s in message.mentions:
            message.content = message.content.replace(s.mention, s.name)
        await self.bot.say(":ok: Pinned First Message with date \"{0}\"!\n**Message Info**\nAuthor: `{1}`\nTime: `{2}`\nContent: \"{3}\"".format(str(_date), message.author.name, message.timestamp, message.content))
        return
    await self.bot.say(":exclamation: No first message found! \n*some shit fucked up*")

  @commands.command(pass_context=True)
  @checks.is_owner()
  async def sql(self, ctx, *, sql:str):
    """Debug SQL"""
    try:
      self.cursor.execute(sql)
      results = self.cursor.fetchall()
      await self.bot.say("**SQL RESULTS**\n"+str(results))
      while True:
        response = await self.bot.wait_for_message(author=ctx.message.author, channel=ctx.message.channel)
        if response == "sql commit":
          self.connection.commit()
          await self.bot.say("commited")
          return
        else:
          return
    except Exception as e:
      await self.bot.say(code.format(e))

def setup(bot):
  bot.add_cog(Moderation(bot))
import asyncio
import time
import steam
import steamapi
import traceback
import json
import discord
import pymysql
import subprocess
import datetime
import requests
import io
import linecache
import sys
import texttable
from discord.ext import commands
from subprocess import call
from subprocess import check_output
from utils import checks
from steam.steamid              import SteamId
from steam.steamprofile         import SteamProfile
from steam.steamaccountuniverse import SteamAccountUniverse
from steam.steamaccounttype     import SteamAccountType

cool = "```xl\n{0}\n```"
code = "```py\n{0}\n```"
diff = "```diff\n{0}\n```"

starttime = time.time()
starttime2 = time.ctime(int(time.time()))

class Info():
  def __init__(self,bot):
    self.bot = bot
    self.connection = bot.mysql.connection
    self.cursor = bot.mysql.cursor
    self.discord_path = bot.path.discord
    self.files_path = bot.path.files

  @commands.command(pass_context=True)
  async def help(self, ctx):
    """help"""
    await self.bot.say("{0}: https://mods.nyc/help".format(ctx.message.author.mention))

  @commands.command(pass_context=True, no_pm=True)
  async def server(self, ctx):
    """server info"""
    server = ctx.message.server
    online = str(len([m.status for m in server.members if str(m.status) == "online" or str(m.status) == "idle"]))
    total = str(len(server.members))

    data = "Name: {0}\n".format(server.name).replace("'", "′")
    data += "ID: {0}\n".format(server.id)
    data += "Region: {0}\n".format(str(server.region))
    data += "Users: {0}/{1}\n".format(online, total)
    data += "Channels: {0}\n".format(str(len(server.channels)))
    data += "Roles: {0}\n".format(str(len(server.roles)))
    data += "Created: {0}\n".format(str(server.created_at))
    data += "Owner: {0}#{1}\n".format(server.owner.name, server.owner.discriminator)
    data += "Icon: {0}\n".format(server.icon_url)
    await self.bot.say(cool.format(data))

  @commands.command()
  async def invite(self):
    """returns invite link for bot"""
    msg = diff.format('+ Invite me to your server with this url')
    msg += '<https://discordapp.com/oauth2/authorize?client_id=170903265565736960&scope=bot&permissions=8>'
    msg += diff.format("- Uncheck Administrator permission if you do not need Admin/Moderation commands.\n+ + +\n! Join NotSoSuper\'s Dev for any questions or help with the bot and free emotes!")
    msg += 'https://discord.gg/QQENx4f'
    await self.bot.say(msg)

  @commands.command(pass_context=True)
  async def info(self, ctx, *users:discord.User):
    """Returns inputed users info."""
    try:
      if not users:
        user = ctx.message.author
        server = ctx.message.server
        seen = str(len(set([member.server.name for member in self.bot.get_all_members() if member.name == user.name])))
        x = 'Your Info:\nUsername: "{0.name}"\nID #: "{1.id}"\nDiscriminator #: "{2.discriminator}"\nAvatar: "{3.avatar_url}"\nStatus: "{4}"\nGame: "{5}"\nVoice Channel: "{6}"\nSeen On: "{7}" servers\nJoined Server On: "{8}"\nRoles: "{9}"'.format(user, user, user, user, str(user.status), str(user.game), str(user.voice_channel), seen, str(user.joined_at), ', '.join(map(str, user.roles)).replace("@", "@\u200b"))
        await self.bot.say(cool.format(x))
      else:
        for user in users:
          server = ctx.message.server
          seen = str(len(set([member.server.name for member in self.bot.get_all_members() if member.name == user.name])))
          x = 'User Info:\nUsername: "{0}"\nID #: "{1}"\nDiscriminator #: "{2}"\nAvatar: "{3}"\nStatus: "{4}"\nGame: "{5}"\nVoice Channel: "{6}"\nSeen On: "{7} servers"\nJoined Server On: "{8}"\nRoles: "{9}"'.format(user.name, user.id, user.discriminator, user.avatar_url, str(user.status), str(user.game), str(user.voice_channel), seen, str(user.joined_at), ', '.join(map(str, user.roles)).replace("@", "@\u200b"))
          await self.bot.say(cool.format(x))
    except Exception as e:
        await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  @commands.command(pass_context=True)
  async def avatar(self, ctx, *users:discord.User):
    """Returns the input users avatar."""
    try:
      if len(users) == 0:
        ss = [ctx.message.author]
        users = ss
      for user in users:
        await self.bot.say("{0}'s avatar is: {1}\n".format(user.mention, user.avatar_url))
    except Exception as e:
      await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  @commands.command(name='time', pass_context=True)
  async def _time(self, ctx):
    """Returns bots date and time."""
    await self.bot.say('@{0}:'.format(ctx.message.author.name) + '\nDate is: **' + time.strftime("%A, %B %d, %Y") + '**' + '\nTime is: **' + time.strftime("%I:%M:%S %p") + '**')

  @commands.command(pass_context=True)
  async def uptime(self, ctx):
    """How long have I been up/online?"""
    seconds = time.time() - starttime
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    w, d = divmod(d, 7)
    await self.bot.say("Online for %dw :" % (w) + " %dd :" % (d) + " %dh :" % (h) + " %dm :" % (m) + " %ds" % (s))

  @commands.command(pass_context=True)
  async def cinfo(self, ctx):
    """Return Channel Information"""
    msg = "Channel Name: {0}\n".format(ctx.message.channel.name)
    msg += "Channel ID: {0}\n".format(ctx.message.channel.id)
    msg += "Channel Created: {0}\n".format(ctx.message.channel.created_at)
    await self.bot.say(cool.format(msg))

  @commands.command(pass_context=True, alias='binfo')
  async def botinfo(self, ctx):
    """Bot Information"""
    msg = "NotSoBot\n"
    msg += "Creator: @NotSoSuper#8800\n"
    msg += "Creator Steam: http://steamcommunity.com/id/suck\n"
    msg += "Library: Discord.py\n"
    msg += "Code: https://github.com/NotSoSuper/notsosuper_bot/\n"
    await self.bot.say(cool.format(msg))

  @commands.command()
  async def botc(self, *, text:str):
    txt = text.split()
    msg = "https://github.com/NotSoSuper/notsosuper_bot/search?q={0}".format("+".join(txt))
    await self.bot.say(msg)

  @commands.command()
  async def stats(self):
    try:
      sql = "SELECT COUNT(`server`) FROM `messages`"
      self.cursor.execute(sql)
      message_count = self.cursor.fetchall()
      sql = "SELECT COUNT(`server`) FROM `message_delete_logs`"
      self.cursor.execute(sql)
      message_delete_count = self.cursor.fetchall()
      sql = "SELECT COUNT(`server`) FROM `message_edit_logs`"
      self.cursor.execute(sql)
      message_edit_count = self.cursor.fetchall()
      sql = "SELECT COUNT(`server`) FROM `command_logs`"
      self.cursor.execute(sql)
      command_count = self.cursor.fetchall()
      sql = "SELECT `command`, COUNT(*) AS magnitude FROM `command_logs` GROUP BY `command` ORDER BY magnitude DESC LIMIT 6"
      self.cursor.execute(sql)
      command_magnitude = self.cursor.fetchall()
      sql = 'SELECT `server`, COUNT(*) AS magnitude FROM `command_logs` GROUP BY `server` ORDER BY magnitude DESC LIMIT 5'
      self.cursor.execute(sql)
      server_magnitude = self.cursor.fetchall()
      shards = [0, 1, 2, 3]
      count = 0
      server_list = []
      for x in shards:
        path = self.files_path('server_count/{0}_largest_member_server.txt'.format(x))
        with io.open(path, 'r') as f:
          split = f.read().split('\n')
          load = [split[0], split[1]]
          server_list.append(load)
          f.close()
      counts = []
      for x in server_list:
        count = int(x[1])
        counts.append(count)
      max_ = int(max(counts))
      max_index = int(counts.index(max_))
      biggest_server_name = server_list[max_index][0]
      biggest_server_count = server_list[max_index][1]
      magnitude_table = texttable.Texttable()
      for x in server_magnitude:
        magnitude_table.add_rows([["Server", "Commands"], [x['server'][:25], x['magnitude']]])
      magnitude_msg = magnitude_table.draw()
      command_table = texttable.Texttable()
      for x in command_magnitude:
        if x['command'] == 'img':
          continue
        command_table.add_rows([["Command", "Count"], [x['command'], x['magnitude']]])
      command_msg = command_table.draw()
      command_stats_msg = magnitude_msg+'\n\n'+command_msg
      text_channels = 0
      voice_channels = 0
      for x in shards:
        path = self.files_path('server_count/{0}_channels.txt'.format(x))
        with io.open(path, 'r') as f:
          split = f.read().split('\n')
          text_channels += int(split[0])
          voice_channels += int(split[1])
          f.close()
      user_count = 0
      unique_users = 0
      server_count = 0
      for x in shards:
        path = self.files_path('server_count/{0}.txt'.format(x))
        with io.open(path, 'r') as f:
          server_count += int(f.read())
          f.close()
        path = self.files_path('server_count/{0}_users.txt'.format(x))
        with io.open(path, 'r') as f:
          user_count += int(f.read())
          f.close()
        path = self.files_path('server_count/{0}_unique_users.txt'.format(x))
        with io.open(path, 'r') as f:
          unique_users += int(f.read())
          f.close()
      seconds = time.time() - starttime
      m, s = divmod(seconds, 60)
      h, m = divmod(m, 60)
      d, h = divmod(h, 24)
      w, d = divmod(d, 7)
      uptime = "**%d** Weeks, " % (w) + " **%d** Days, " % (d) + "**%d** Hours " % (h) + "**%d** Minutes " % (m) + " **%d** Seconds" % (s)
      msg = ":bar_chart: **User/Bot Statistics**\n"
      msg += "> Uptime: "+uptime+"\n"
      msg += "> On **{0}** Servers\n".format(server_count)
      msg += "> **{0}** Text channels | **{1}** Voice\n".format(text_channels, voice_channels)
      msg += "> Serving **{0}** Users\n".format(user_count)
      msg += "> Unique Users: **{0}**\n".format(unique_users)
      msg += "> Who've messaged **{0}** times ".format(message_count[0]['COUNT(`server`)'])
      msg += "where **{0}** of them have been edited ".format(message_edit_count[0]['COUNT(`server`)'])
      msg += "and **{0}** deleted.\n".format(message_delete_count[0]['COUNT(`server`)'])
      msg += "> In total **{0}** commands have been called.\n".format(command_count[0]['COUNT(`server`)'])
      msg += ':keyboard: **Command Statistics**\n'
      msg += cool.format(command_stats_msg)
      msg += ':desktop: **Server Statistics**\n'
      msg += '> Largest Server: **{0}** (Users: **{1}**)\n'.format(biggest_server_name, biggest_server_count)
      msg += '> Most used on: **{0}** (Commands: **{1}**/{2})'.format(server_magnitude[0]['server'], server_magnitude[0]['magnitude'], command_count[0]['COUNT(`server`)'])
      # msg += '> Server with most messages: *{0}* (Messages: **{1}/{2}**)'
      await self.bot.say(msg)
    except Exception as e:
      print(e)

  @commands.command()
  async def speedtest(self):
    msg = check_output(["speedtest-cli", "--simple", "--share"]).decode()
    await self.bot.say(cool.format(msg.replace("", "SERVER IP").replace("\n", "\n").replace("\"", "").replace("b'", "").replace("'", "")))

  @commands.command()
  async def iping(self, *, ip:str):
    msg = check_output(["ping", "-c", "4", "{0}".format(ip)]).decode()
    await self.bot.say(cool.format(msg))

  @commands.command(pass_context=True, aliases=['so', 'stack', 'csearch', 'stacko', 'stackoverflow'])
  async def sof(self, ctx, *, text:str):
    api = 'https://api.stackexchange.com/2.2/search?order=desc&sort=votes&site=stackoverflow&intitle={0}'.format(text)
    r = requests.get(api)
    load = r.json()
    q_c = len(load['items'])
    if q_c == 0:
      await self.bot.say("No Results Found On <https://stackoverflow.com>")
      return
    if q_c > 5:
      msg = "**First 5 Results For: `{0}`**\n".format(text)
    else:
      msg = "**First {0} Results For: `{1}`**\n".format(str(q_c), text)
    count = 0
    for s in load['items']:
      if q_c > 5:
        if count == 5:
          break
      else:
        if count == q_c:
          break
      epoch = int(s['creation_date'])
      date = str(datetime.datetime.fromtimestamp(epoch).strftime('%m-%d-%Y'))
      msg += "```xl\nTitle: {0}\nLink: {1}\nCreation Date: {2}\nScore: {3}\nViews: {4}\nIs-Answered: {5}\nAnswer Count: {6}```".format(s['title'], s['link'].replace("http://", "").replace("https://", "").replace("www.", ""), date, s['score'], s['view_count'], s['is_answered'], s['answer_count'])
      count += 1
    await self.bot.say(msg)

def setup(bot):
  bot.add_cog(Info(bot))
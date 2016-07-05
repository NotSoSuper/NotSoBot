import asyncio
import time
import traceback
import json
import discord
import pymysql
import subprocess
import datetime
import requests
from discord.ext import commands
from subprocess import call
from subprocess import check_output
from utils import checks

cool = "```xl\n{0}\n```"
code = "```py\n{0}\n```"

starttime = time.time()
starttime2 = time.ctime(int(time.time()))

connection = pymysql.connect(host='',
                     user='',
                     password='',
                     db='',
                     charset='',
                     cursorclass=pymysql.cursors.DictCursor)
cursor = connection.cursor()

class Info():
  def __init__(self,bot):
    self.bot = bot

  @commands.command(pass_context=True)
  async def help(self, ctx):
    """help"""
    await self.bot.say("Sending Help to {0} over PM.\nhttps://mods.nyc/help".format(ctx.message.author.mention))
    msg = "Due to extensive length in both the help docs and commands\n"
    msg += "Here's a website with everything for the bot\n"
    msg += "https://mods.nyc/help"
    await self.bot.send_message(ctx.message.author, msg)

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
    msg = 'Invite me to your server with this `url:` https://discordapp.com/oauth2/authorize?client_id=170903265565736960&scope=bot&permissions=8\nUncheck Administrator Permission If You Do Not Need Admin/Moderation Commands.'
    await self.bot.say(msg)

  @commands.command(pass_context=True)
  async def info(self, ctx,*users:discord.User):
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
        for user in users:
            await self.bot.say("{0}'s avatar is: \n".format(user.mention) + user.avatar_url)
    except Exception as e:
        await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  @commands.command(name='time', pass_context=True)
  async def _time(self, ctx):
    """Returns bots date and time."""
    try:
        await self.bot.say('@{0}:'.format(ctx.message.author.name) + '\nDate is: **' + time.strftime("%A, %B %d, %Y") + '**' + '\nTime is: **' + time.strftime("%I:%M:%S %p") + '**')
    except Exception as e:
        await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  @commands.command(pass_context=True)
  async def uptime(self, ctx):
    """How long have I been up/online?"""
    try:
        seconds = time.time() - starttime
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        w, d = divmod(d, 7)
        await self.bot.say("Online for %dw :" % (w) + " %dd :" % (d) + " %dh :" % (h) + " %dm :" % (m) + " %ds" % (s))
    except Exception as e:
        await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

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
    msg += "Code: https://github.com/NotSoSuper/NotSoBot/\n"
    msg += "Powered by https://ropestore.org"
    await self.bot.say(cool.format(msg))

  @commands.command()
  async def botc(self, *, text:str):
    msg = "https://github.com/NotSoSuper/NotSoBot/search?q={0}".format(text)
    await self.bot.say(msg)

  @commands.command()
  async def stats(self):
    count = len(set([member for member in self.bot.get_all_members()]))
    sql = "SELECT COUNT(`server`) FROM `messages`"
    cursor.execute(sql)
    message_count = cursor.fetchall()
    sql = "SELECT COUNT(`server`) FROM `message_delete_logs`"
    cursor.execute(sql)
    message_delete_count = cursor.fetchall()
    sql = "SELECT COUNT(`server`) FROM `message_edit_logs`"
    cursor.execute(sql)
    message_edit_count = cursor.fetchall()
    sql = "SELECT COUNT(`server`) FROM `command_logs`"
    cursor.execute(sql)
    command_count = cursor.fetchall()
    msg = "Server/User/Bot Statistics\n\n"
    msg += "Servers: {0}\n".format(len(self.bot.servers))
    msg += "Users: {0}\n".format(str(count))
    msg += "Messages: {0}\n".format(message_count[0]['COUNT(`server`)'])
    msg += "Messages Edited: {0}\n".format(message_edit_count[0]['COUNT(`server`)'])
    msg += "Messages Deleted: {0}\n".format(message_delete_count[0]['COUNT(`server`)'])
    msg += "Commands Used: {0}".format(command_count[0]['COUNT(`server`)'])
    await self.bot.say(cool.format(msg))

  @commands.command()
  async def speedtest(self):
    msg = check_output(["speedtest-cli", "--simple", "--share"]).decode()
    await self.bot.say(cool.format(msg.replace("serverip", "SERVER IP").replace("\n", "\n").replace("\"", "").replace("b'", "").replace("'", "")))

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
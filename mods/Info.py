import asyncio
import time
import steamapi
import traceback
import json
import discord
from discord.ext import commands
from utils import checks
from steamapi.steamid              import SteamId
from steamapi.steamprofile         import SteamProfile
from steamapi.steamaccountuniverse import SteamAccountUniverse
from steamapi.steamaccounttype     import SteamAccountType

cool = "```xl\n{0}\n```"
code = "```py\n{0}\n```"

class Info():
  def __init__(self,bot):
    self.bot = bot

  @commands.command(pass_context=True)
  async def help(self, ctx):
      """help"""
      await self.bot.say("Sending Help to {0} over PM.".format(ctx.message.author.mention))
      with open('/root/discord/./utils/help.txt') as halp:
          msg = halp.read()
          await self.bot.send_message(ctx.message.author, cool.format(msg))
      with open('/root/discord/./utils/help2.txt') as halp:
          msg = halp.read()
          await self.bot.send_message(ctx.message.author, cool.format(msg))

  @commands.command(pass_context=True, no_pm=True)
  async def server(self, ctx):
      """server info"""
      server = ctx.message.server
      online = str(len([m.status for m in server.members if str(m.status) == "online" or str(m.status) == "idle"]))
      total = str(len(server.members))

      data = "```\n"
      data += "Name: {}\n".format(server.name)
      data += "ID: {}\n".format(server.id)
      data += "Region: {}\n".format(str(server.region))
      data += "Users: {}/{}\n".format(online, total)
      data += "Channels: {}\n".format(str(len(server.channels)))
      data += "Roles: {}\n".format(str(len(server.roles)))
      data += "Created: {}\n".format(str(server.created_at))
      data += "Owner: {}#{}\n".format(server.owner.name, server.owner.discriminator)
      data += "Icon: {}\n".format(server.icon_url)
      data += "```"
      await self.bot.say(cool.format(data))

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
          await self.bot.say("@NotSoBot has been online for %dw :" % (w) + " %dd :" % (d) + " %dh :" % (h) + " %dm :" % (m) + " %ds" % (s))
      except Exception as e:
          await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

def setup(bot):
    bot.add_cog(Info(bot))
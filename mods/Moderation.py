import asyncio
import traceback
import json
import discord
from discord.ext import commands
from utils import checks
from discord.message import Message
from discord.user import User

with open("/root/discord/utils/config.json") as f:
    config = json.load(f)

cool = "```xl\n{0}\n```"
code = "```py\n{0}\n```"

class Moderation():
  def __init__(self,bot):
    self.bot = bot

  @commands.command(pass_context=True)
  @checks.mod_or_perm(manage_messages=True)
  async def clean(self, ctx, max_messages:int):
      """Removes inputed amount of bot messages."""
      try:
          if max_messages > 1000:
              await self.bot.say("2 many messages")
          max_messages = max_messages + 1
          async for message in self.bot.logs_from(ctx.message.channel, limit=max_messages):
              if message.author == bot.user:
                  asyncio.ensure_future(self.bot.delete_message(message))
                  await asyncio.sleep(0.4)
          await self.bot.say("Removed any of my messages found within ``{0}`` messages".format(max_messages))
      except Exception as e:
          await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  @commands.command(pass_context=True)
  @checks.mod_or_perm(manage_messages=True)
  async def prune(self, ctx, max_messages:int):
      """Removes inputed amount of channel messages."""
      try:
          if ctx.message.server.me.permissions_in(ctx.message.channel).manage_messages:
              if max_messages > 1000:
                  await self.bot.say("2 many messages")
              max_messages = max_messages + 1
              async for message in self.bot.logs_from(ctx.message.channel, limit=max_messages):
                  asyncio.ensure_future(self.bot.delete_message(message))
                  await asyncio.sleep(0.4)
              await self.bot.say("Removed ``{0}`` channel messages".format(max_messages))
          else:
              await self.bot.say("Sorry, this doesn't work on this server (No manage_messages Permission)!")          
      except Exception as e:
          await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  @commands.command(pass_context=True)
  @checks.mod_or_perm(manage_messages=True)
  async def pruneuser(self, ctx, max_messages:int, user:discord.User):
      """Removes inputed amount of messages found of the inputed user."""
      try:
          if ctx.message.server.me.permissions_in(ctx.message.channel).manage_messages:
              if max_messages > 1000:
                  await self.bot.say("2 many messages")
              async for message in self.bot.logs_from(ctx.message.channel, limit=max_messages):
                  count = max_messages - 1
                  if user.id == message.author.id:
                      asyncio.ensure_future(self.bot.delete_message(message))
                      await asyncio.sleep(0.4)
                  elif count == 0:
                      await self.bot.say("No messages found by {0} \nwithin the given max message search amount!".format(user.mention))
              await self.bot.say("Searching through `{0}` messages and removing any of {1}'s".format(max_messages, user.mention))
          else:
              await self.bot.say("Sorry, this doesn't work on this server (No manage_messages Permission)!")             
      except Exception as e:
          await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  @commands.command(pass_context=True)
  @checks.is_owner()
  async def blacklist(self, ctx, user:discord.User):
      """Blacklists a user from the bot.\nOwner only ofc."""
      try:
          if user.id == "<@{0}>".format(config["ownerid"]):
              await self.bot.say("what are you doing @NotSoSuper?")
          elif user.mention in open('/root/discord/utils/blacklist.txt').read():
              await self.bot.say("{0} is already blacklisted".format(user.mention))
          else:
              with open("/root/discord/utils/blacklist.txt","a") as f:
                  f.write(user.mention + "\n")
                  await self.bot.say("ok, blacklisted {0}".format(user.mention))
      except Exception as e:
          await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

  @commands.command(pass_context=True)
  @checks.is_owner()
  async def unblacklist(self, ctx, user:discord.User):
      """Unblacklist a user.\nOwner only ofc."""
      try:
          if len(set(ctx.message.mentions)) > 0:
              if user.id == "<@{0}>".format(config["ownerid"]):
                  await self.bot.say("what are you doing @NotSoSuper?")
              elif user.mention in open('/root/discord/utils/blacklist.txt').read():
                  f = open('/root/discord/utils/blacklist.txt', 'r')
                  a = f.read()
                  f.close()
                  data = a.replace(user.mention, "")
                  f = open('/root/discord/utils/blacklist.txt', 'w')
                  f.write(data)
                  f.close()
                  await self.bot.say("ok, unblacklisted {0}".format(user.mention))
              else:
                  await self.bot.say("{0} isn\'t Blacklisted!".format(user.mention))
          else:
              await self.bot.say("mention user plz")
      except Exception as e:
          await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

def setup(bot):
    bot.add_cog(Moderation(bot))
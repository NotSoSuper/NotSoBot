import discord
import asyncio
from pymarkovchain import MarkovChain
from discord.ext import commands
from io import StringIO

class Markov():
  def __init__(self,bot):
    self.bot = bot
    self.discord_path = bot.path.discord
    self.files_path = bot.path.files

  @commands.command(pass_context=True, aliases=['mark', 'm'])
  async def markov(self, ctx):
    """Get a response from inputed text using a markov chain generated from the channels text"""
    results = ''
    async for message in self.bot.logs_from(ctx.message.channel, limit=10):
      line = message.content
      results += line+"\n"
    f = StringIO(results.encode('utf-8'))
    mc = MarkovChain(f.getvalue())
    mc.generateDatabase(f)
    msg = mc.generateString()
    await self.bot.say(msg)

def setup(bot):
  bot.add_cog(Markov(bot))
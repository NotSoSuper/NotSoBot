import discord
import asyncio
import re
from discord.ext import commands
from chatterbot import ChatBot
from chatterbot.training.trainers import ChatterBotCorpusTrainer

chatbot = ChatBot("NotSoBot",
                  storage_adapter="chatterbot.adapters.storage.MongoDatabaseAdapter",
                  logic_adapter="chatterbot.adapters.logic.ClosestMeaningAdapter",
                  input_adapter="chatterbot.adapters.input.VariableInputTypeAdapter",
                  output_adapter="chatterbot.adapters.output.OutputFormatAdapter",
                  format='text',
                  database='chatterbot-database',
                  database_uri='')
chatbot.set_trainer(ChatterBotCorpusTrainer)
chatbot.train("chatterbot.corpus.english")

class AI():
  def __init__(self,bot):
    self.bot = bot

  ai_target = {}
  @commands.command(pass_context=True, aliases=['artificialinteligence', 'cb', 'talk', 'cleverbot'])
  async def ai(self, ctx):
    """Toggle AI Targeted Responses"""
    if any([ctx.message.author.id == x for x in self.ai_target]) == False:
      await self.bot.say("ok, AI targetting user `{0}`\n".format(ctx.message.author.name))
      self.ai_target.update({ctx.message.author.id:ctx.message.channel.id})
    else:
      await self.bot.say("ok, removed AI target `{0}`".format(ctx.message.author.name))
      del self.ai_target[ctx.message.author.id]

  async def on_message(self, message):
    if message.author == self.bot.user:
      return
    if message.content.startswith('.'):
      return
    message.content = re.sub('[^0-9a-zA-Z]+', ' ', message.content)
    message.content = message.content.replace('`', '')
    message.content = message.content.replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
    if len(message.mentions) != 0:
      for s in message.mentions:
        message.content = message.content.replace(s.mention, s.name)
    if message.author.id in self.ai_target.keys() and self.ai_target[message.author.id] == message.channel.id:
      await self.bot.send_typing(message.channel)
      i = 0
      while i < 5:
        msg = "**{0}**\n".format(message.author.name)+str(chatbot.get_response(message.content))
        if len(msg) != 0:
          try:
            await self.bot.send_message(message.channel, msg)
          except discord.errors.Forbidden:
            return
          i = 5
        else:
          i += 1
      asyncio.sleep(0.1)
    else:
      return


def setup(bot):
  bot.add_cog(AI(bot))
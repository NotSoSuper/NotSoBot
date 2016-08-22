#! /usr/bin/env python
import sys
import discord
import asyncio
import requests
from discord.ext import commands

bot = commands.Bot(command_prefix=commands.when_mentioned_or('idk '), help_attrs={'name':"iamabadhelpcommand", 'enabled':False, 'hidden':True})

async def check_queue():
  await bot.wait_until_ready()
  while not bot.is_closed:
    payload = {'key': ''}
    r = requests.post(':eyes:/queued', data=payload)
    queue = r.json()
    if len(queue) == 0:
      await asyncio.sleep(1)
    else:
      for s in queue:
        message_id = int(s)
        channel_id = int(queue[s][0])
        message = str(queue[s][1])
        target = discord.Object(id=channel_id)
        try:
          await bot.send_message(target, message)
        except:
          pass
        delete_payload = {'key':'', 'id':message_id}
        delete_request = requests.post(':eyes:/queue_delete', data=delete_payload)
        if delete_request.text == 'no, 1':
          print(delete_request.text)
          print('fucking rip')
        await asyncio.sleep(0.21)

@bot.event
async def on_ready():
  print('Logged in as')
  print(bot.user.name + "#" + bot.user.discriminator)
  print(bot.user.id)
  print('------')
  await bot.change_status(discord.Game(name="go away"))

bot.loop.create_task(check_queue())
bot.run('')
import asyncio
import aiohttp
import discord
import random
import io
import magic
import requests
import os
import PIL.Image
import numpy as np
from tempfile import mkstemp
from io import StringIO
from io import BytesIO
from discord.ext import commands
from utils import checks
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

cool = "```xl\n{0}\n```"
code = "```py\n{0}\n```"

image_mimes = ['image/png', 'image/pjpeg', 'image/jpeg', 'image/x-icon']
def isimage(url:str):
  r = requests.get(url, stream=True)
  mime = magic.from_buffer(next(r.iter_content(256)), mime=True).decode()
  if any([mime == x for x in image_mimes]):
    return True
  else:
    return False

async def download(url:str, path:str):
	with aiohttp.ClientSession() as session:
		async with session.get(url) as resp:
			data = await resp.read()
			with open(path, "wb") as f:
				f.write(data)
				f.close()

async def bytes_download(link:str):
  with aiohttp.ClientSession() as session:
    async with session.get(link) as resp:
      data = await resp.read()
      b = BytesIO(data)
      b.seek(0)
      return b

class Wc():
	def __init__(self, bot):
		self.bot = bot

	@commands.group(pass_context=True, name='wc', aliases=['wordcloud', 'wordc'], invoke_without_command=True)
	async def wc(self, ctx, max_messages:int=100):
		if max_messages > 1500:
			await self.bot.say("2 many messages")
			return
		results = ''
		async for message in self.bot.logs_from(ctx.message.channel, limit=max_messages):
			split = message.content.split()
			for s in split:
				results += s+'\n'
		text = results.split('\n')
		wc = WordCloud(background_color="black", width=1280, height=960, max_words=500).generate(' '.join(text))
		final = '/tmp/wc_{0}.png'.format(random.randint(0, 9999))
		wc.to_file(final)
		await self.bot.send_file(ctx.message.channel, final, filename='wordcloud.png')
		os.remove(final)

	@wc.command(name='custom', pass_context=True, invoke_without_command=True)
	async def _wc_custom(self, ctx, url:str, max_messages:int=100):
		try:
			if max_messages > 1500:
				await self.bot.say("2 many messages")
				return
			results = ''
			async for message in self.bot.logs_from(ctx.message.channel, limit=max_messages):
				split = message.content.split()
				for s in split:
					results += s+'\n'
			text = results.split('\n')
			eyes = False
			if url == "👀" or url == ":eyes:":
				image = '/root/discord/files/eyes_wc.png'
				eyes = True
			else:
				if isimage(url) == False:
					await self.bot.say("Invalid or Non-Image!")
					return
				image = await bytes_download(url)
			coloring = np.array(PIL.Image.open(image))
			wc = WordCloud(background_color="white", width=1280, height=960, max_words=500, mask=coloring).generate(' '.join(text))
			final = '/tmp/wc_{0}.png'.format(random.randint(0, 9999))
			wc.to_file(final)
			await self.bot.send_file(ctx.message.channel, final, filename='wordcloud_custom.png')
			os.remove(final)
		except Exception as e:
			print(e)

def setup(bot):
	bot.add_cog(Wc(bot))
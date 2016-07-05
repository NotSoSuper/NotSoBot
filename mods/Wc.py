import asyncio
import discord
import random
import io
from os import path
from PIL import Image
import numpy as np
from discord.ext import commands
from utils import checks
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

cool = "```xl\n{0}\n```"
code = "```py\n{0}\n```"

async def download(url:str, path:str):
	with aiohttp.ClientSession() as session:
		async with session.get(url) as resp:
			data = await resp.read()
			with open(path, "wb") as f:
				f.write(data)
				f.close()

class Wc():
	def __init__(self, bot):
		self.bot = bot

	#https://github.com/amueller/word_cloud/
	@commands.group(pass_context=True, name='wc', aliases=['wordcloud', 'wordc'], invoke_without_command=True)
	async def wc(self, ctx, max_messages:int=50):
		text_path = '/root/discord/files/wc.txt'
		async for message in self.bot.logs_from(ctx.message.channel, limit=max_messages):
			s = message.content.split()
			line = s[0]+"\n"
			with io.open(text_path, "a", encoding='utf8') as f:
				f.write(line)
				f.close()
		text = open(text_path).read()
		rand = str(random.randint(0, 100))
		wc = WordCloud(background_color="gray", max_words=100, max_font_size=20)
		wc.generate(text)
		path = '/root/discord/files/wc_final_{0}.png'.format(rand)
		wc.to_file(path)
		await self.bot.send_file(ctx.message.channel, path, filename='wordcloud.png')
		os.remove(text_path)
		os.remove(path)

	@wc.command(name='custom', pass_context=True, invoke_without_command=True)
	async def _wc_custom(self, ctx, url:str, max_messages:int=50):
		text_path = '/root/discord/files/wc.txt'
		async for message in self.bot.logs_from(ctx.message.channel, limit=max_messages):
			s = message.content.split()
			line = s[0]
			with io.open(text_path, "a", encoding='utf8') as f:
				f.write(line)
				f.close()
		text = open(text_path).read()
		rand = str(random.randint(0, 100))
		if url == ":eyes:":
			image_path = '/root/discord/files/emoji_eyes.png'
		else:
			image_path = '/root/discord/files/wc_custom_{0}.png'.format(rand)
			await download(url, image_path)
		coloring = np.array(Image.open(image_path))
		wc = WordCloud(background_color="white", max_words=100, mask=coloring, max_font_size=20, random_state=42)
		wc.generate(text)
		path = '/root/discord/files/wc_custom_final_{0}.png'.format(rand)
		wc.to_file(path)
		await self.bot.send_file(ctx.message.channel, path, filename='wordcloud_custom.png')
		os.remove(text_path)
		os.remove(image_path)
		os.remove(path)

def setup(bot):
	bot.add_cog(Wc(bot))
import random
import os
import PIL.Image
import numpy as np
from io import BytesIO, StringIO
from discord.ext import commands
from wordcloud import WordCloud, ImageColorGenerator
from mods.cog import Cog

cool = "```xl\n{0}\n```"
code = "```py\n{0}\n```"

class Wc(Cog):
	def __init__(self, bot):
		super().__init__(bot)
		self.bytes_download = bot.bytes_download
		self.isimage = bot.isimage

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
				check = await self.isimage(url)
				if check == False:
					await self.bot.say("Invalid or Non-Image!")
					return
				image = await self.bytes_download(url)
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
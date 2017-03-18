import discord
import PIL.Image
import numpy as np
from io import BytesIO
from discord.ext import commands
from wordcloud import WordCloud, ImageColorGenerator
from mods.cog import Cog

class Wc(Cog):
	def __init__(self, bot):
		super().__init__(bot)
		self.bytes_download = bot.bytes_download
		self.isimage = bot.isimage
		self.cursor = bot.mysql.cursor
		self.get_images = bot.get_images
		self.message_cache = {}

	def make_wc(self, text, max):
		try:
			wc = WordCloud(background_color='black', width=1024, height=768, max_words=max).generate(' '.join(text))
			img = wc.to_image()
			b = BytesIO()
			img.save(b, 'png')
			b.seek(0)
			return b
		except Exception as e:
			return str(e)

	def make_wc_custom(self, mask, text, max):
		try:
			coloring = np.array(PIL.Image.open(mask))
			wc = WordCloud(width=1024, height=768, max_words=max, mask=coloring)
			wc = wc.generate(' '.join(text))
			image_colors = ImageColorGenerator(coloring)
			wc = wc.recolor(color_func=image_colors)
			img = wc.to_image()
			b = BytesIO()
			img.save(b, 'png')
			b.seek(0)
			return b
		except Exception as e:
			return str(e)

	async def get_messages(self, channel, limit, user=None):
		msgs = None
		if channel in self.message_cache.keys():
			msgs = self.message_cache[channel]
			if len(msgs) >= limit:
				msgs = msgs[:limit]
			else:
				before = msgs[-1]
				limit = limit-len(msgs)
		else:
			self.message_cache[channel] = []
			before = None
		if not msgs:
			async for message in self.bot.logs_from(channel, limit=limit, before=before):
				self.message_cache[channel].append(message.content)
			msgs = self.message_cache[channel]
			if not len(msgs):
				return ['no messages found rip']
		final = []
		for msg in msgs:
			final.extend([*msg.split()])
		return final

	@commands.group(pass_context=True, name='wc', aliases=['wordcloud', 'wordc'], invoke_without_command=True)
	@commands.cooldown(10, 1)
	async def wc(self, ctx, *urls:str):
		max_messages = 500
		custom = False
		if len(urls) == 1:
			if urls[0].isdigit():
				max_messages = int(urls[0])
		elif len(urls) > 1:
			get_images = await self.get_images(ctx, urls=urls, scale=4000)
			if not get_images:
				return
			custom = True
			image, scale, scale_msg = get_images
			image = await self.bytes_download(image[0])
			if scale:
				max_messages = int(scale)
		if max_messages > 4000 or max_messages < 1:
			max_messages = 500
		x = await self.bot.say("ok, processing{0}".format(' (this might take a while)' if max_messages > 2000 else ''))				
		text = await self.get_messages(ctx.message.channel, max_messages)
		if custom:
			b = await self.bot.loop.run_in_executor(None, self.make_wc_custom, image, text, max_messages)
		else:
			b = await self.bot.loop.run_in_executor(None, self.make_wc, text, max_messages)
		if type(b) == str:
			await self.bot.say(b)
		else:
			await self.bot.upload(b, filename='wordcloud.png')
		await self.bot.delete_message(x)

	@wc.command(name='user', pass_context=True, aliases=['u'])
	@commands.cooldown(10, 1)
	async def wc_user(self, ctx, user:discord.User, max_messages:int=500):
		if max_messages > 4000 or max_messages < 1:
			max_messages = 500
		x = await self.bot.say("ok, processing{0}".format(' (this might take a while)' if max_messages > 2000 else ''))				
		text = await self.get_messages(ctx.message.channel, max_messages, user=user.id)
		b = await self.bot.loop.run_in_executor(None, self.make_wc, text, max_messages)
		await self.bot.upload(b, filename='wordcloud.png')
		await self.bot.delete_message(x)

def setup(bot):
	bot.add_cog(Wc(bot))

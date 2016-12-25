import discord
import asyncio
import re
from discord.ext import commands
from utils import checks
from mods.cog import Cog

class Afk(Cog):
	def __init__(self, bot):
		super().__init__(bot)
		self.cursor = bot.mysql.cursor
		self.afks = {}
		self.mention_regex = re.compile(r'(<@(|!|)\d*>)')
		self.bot.loop.create_task(self.afk_init())

	async def afk_init(self):
		sql = 'SELECT * FROM `afk`'
		result = self.cursor.execute(sql).fetchall()
		if len(result) == 0:
			return
		for s in result:
			self.afks[str(s['user'])] = s['reason']

	async def remove_afk(self, user):
		sql = 'DELETE FROM `afk` WHERE user={0}'
		sql = sql.format(user)
		self.cursor.execute(sql)
		self.cursor.commit()
		del self.afks[str(user)]

	@commands.command(pass_context=True)
	async def afk(self, ctx, *, reason:str=None):
		if reason:
			reason = reason.replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
		sql = 'INSERT INTO `afk` (`user`, `reason`) VALUES (%s, %s)'
		try:
			self.cursor.execute(sql, (ctx.message.author.id, reason))
		except:
			await self.remove_afk(ctx.message.author.id)
			await self.bot.say(':no_entry: You are already afk, you have been removed.')
		self.cursor.commit()
		self.afks[ctx.message.author.id] = reason
		msg = ':white_check_mark: `{0}` is now afk.'.format(ctx.message.author)
		await self.bot.say(msg)

	async def on_message(self, message):
		if message.author == self.bot.user:
			return
		if message.channel.is_private:
			return
		sql = 'SELECT user,reason FROM `afk`'
		result = self.cursor.execute(sql).fetchall()
		if len(result) == 0:
			return
		mentions_results = self.mention_regex.findall(message.content)
		if not mentions_results:
			return
		mentions = [x[0].replace('!', '') for x in mentions_results]
		for s in result:
			m = '<@{0}>'.format(s['user'])
			u = message.server.get_member(str(s['user']))
			if m in mentions and u != None and s['user'] in self.afks:
				await self.bot.send_message(message.channel, '\n:keyboard: `{0}` is currently AFK{1}'.format(u, ':\n{0}'.format(s['reason'] if s['reason'] else '.')))

	async def on_typing(self, channel, user, when):
		if user.id in self.afks:
			try:
				await self.remove_afk(user.id)
			except:
				return
			await self.bot.send_message(user, ':ok_hand: Welcome back, your AFK status has been removed{0}.'.format(' ({0})'.format(channel.mention) if not channel.is_private else ''))

def setup(bot):
	bot.add_cog(Afk(bot))
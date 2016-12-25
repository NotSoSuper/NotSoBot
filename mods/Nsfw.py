import discord
import random
import json
import xml.etree.ElementTree
import aiohttp
import bs4
import sys
from io import BytesIO
from discord.ext import commands
from utils import checks
from mods.cog import Cog
from urllib.parse import quote

class Nsfw(Cog):
	def __init__(self, bot):
		super().__init__(bot)
		self.cursor = bot.mysql.cursor
		self.escape = bot.escape
		self.bytes_download = bot.bytes_download
		self.get_json = bot.get_json

	async def banned_tags(self, ctx, search):
		if ctx.message.channel.is_private:
			return False
		sql = 'SELECT * FROM banned_nsfw_tags WHERE server={0}'
		sql = sql.format(ctx.message.server.id)
		result = self.cursor.execute(sql).fetchall()
		tags = []
		for x in result:
			tags.append(x['tag'])
		found = []
		for tag in tags:
			for s in [x for x in search]:
				try:
					index = tags.index(str(s))
					found.append(tags[index])
				except (IndexError, ValueError):
					continue
		if len(found) != 0:
			await self.bot.send_message(ctx.message.channel, ':no_entry: Your search included banned tag(s): `{0}`'.format(', '.join(found)))
			return True
		return False

	@commands.group(pass_context=True, aliases=['bannsfwtag', 'bannsfwsearch', 'nsfwban'], invoke_without_command=True, no_pm=True)
	@checks.mod_or_perm(manage_server=True)
	async def bantag(self, ctx, *tags:str):
		"""Ban a string/tag from being searched with nsfw commands"""
		if len(tags) == 0:
			await self.bot.say(":warning: Please input tag(s) to ban.")
			return
		sql = 'INSERT INTO `banned_nsfw_tags` (`server`, `tag`) VALUES (%s, %s)'
		for tag in tags:
			self.cursor.execute(sql, (ctx.message.server.id, tag))
			self.cursor.commit()
		await self.bot.say(':white_check_mark: Banned (**{0}**) tags: `{1}`.'.format(len(tags), ', '.join(tags)))

	@bantag.command(name='list', pass_context=True, invoke_without_command=True, no_pm=True)
	async def bantag_list(self, ctx):
		"""List all banned tags"""
		sql = 'SELECT * FROM banned_nsfw_tags WHERE server={0}'
		sql = sql.format(ctx.message.server.id)
		result = self.cursor.execute(sql).fetchall()
		if len(result) == 0:
			await self.bot.say('Server does not have any tags banned for nsfw commands!')
			return
		tags = []
		for x in result:
			tags.append(x['tag'])
		await self.bot.say(':white_check_mark: Banned NSFW Tags:\n`{0}`'.format(', '.join(tags)))

	@bantag.group(name='remove', pass_context=True, invoke_without_command=True, aliases=['delete', 'unban'], no_pm=True)
	async def bantag_remove(self, ctx, *tags:str):
		"""Remove a banned tag"""
		sql = "DELETE FROM `banned_nsfw_tags` WHERE server={0} AND tag={1}"
		removed = False
		for tag in tags:
			check = "SELECT * FROM `banned_nsfw_tags` WHERE server={0} AND tag={1}"
			check = check.format(ctx.message.server.id, self.escape(tag))
			result = self.cursor.execute(check).fetchall()
			if len(result) == 0:
				await self.bot.say(':warning: Tag `{0}` is not banned.'.format(tag))
				continue
			else:
				sql = sql.format(ctx.message.server.id, self.escape(tag))
				self.cursor.execute(sql)
				self.cursor.commit()
				removed = True
		if removed:
			await self.bot.say(':white_check_mark: Removed tag(s) `{0}` from the ban list.'.format(', '.join(tags)))

	@bantag_remove.command(name='all', pass_context=True, invoke_without_command=True, no_pm=True)
	async def bantag_remove_all(self, ctx):
		sql = 'DELETE FROM `banned_nsfw_tags` WHERE server={0}'
		sql = sql.format(ctx.message.server.id)
		check = 'SELECT * FROM `banned_nsfw_tags` WHERE server={0}'
		check = check.format(ctx.message.server.id)
		result = self.cursor.execute(check).fetchall()
		if len(result) == 0:
			await self.bot.say('Server does not have any tags banned for nsfw commands!')
			return
		self.cursor.execute(sql)
		self.cursor.commit()
		await self.bot.say(':white_check_mark: Removed `all` banned tags.')

# Commands redacted, thanks github sjws
banned = await self.banned_tags(ctx, search)
if banned:
	return

def setup(bot):
	bot.add_cog(Nsfw(bot))
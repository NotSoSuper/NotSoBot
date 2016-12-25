import asyncio
import discord
import json
import aiohttp
from time import strftime
from discord.ext import commands
from utils import checks
from mods.cog import Cog

class Changes(Cog):
	def __init__(self, bot):
		super().__init__(bot)
		self.cursor = bot.mysql.cursor
		self.proxy_request = bot.proxy_request

	async def gist(self, ctx, log_type:int, idk, content:str):
		title = 'Names: "{0}"'.format(idk) if log_type == 1 else 'Server Names: "{0}"'.format(idk)
		payload = {
			'name': 'NotSoBot - By: {0}.'.format(ctx.message.author),
			'text': content,
			'private': '1',
			'title': title,
			'expire': '0'
		}
		with aiohttp.ClientSession() as session:
			async with session.post('https://spit.mixtape.moe/api/create', data=payload) as r:
				url = await r.text()
				await self.bot.say(':warning: Results too long (>= 1999)\n**Uploaded** to paste, URL: <{0}>'.format(url))

	@commands.command(pass_context=True, aliases=['name', 'namelogs'])
	@commands.cooldown(1, 15)
	async def names(self, ctx, user:str=None):
		"""Show all the logs the bot has of the users name or nickname"""
		try:
			if user is None:
				user = ctx.message.author
			else:
				if user.isdigit():
					user = discord.Server.get_member(ctx.message.server, user_id=user)
					if user is None:
						for server in self.bot.servers:
							for member in server.members:
								if member.id == user:
									user = member
					if user is None:
						await self.bot.say("Sorry, no user was found with that ID on any servers I'm on!")
						return
				else:
					if len(ctx.message.mentions) != 0:
						user = ctx.message.mentions[0]
					else:
						user = ctx.message.author
			sql = "SELECT * FROM `names` WHERE id={0}"
			sql = sql.format(user.id)
			result = self.cursor.execute(sql).fetchall()
			if len(result) == 0:
				await self.bot.say(":no_entry: \"{0}\" does not have any name changes recorded!".format(user.name))
				return
			results = ""
			names_added = []
			discrims_added = []
			for s in result:
				already_there = False
				name = s['name'].replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
				if s['discrim'] != None:
					discrim_there = False
					for d in discrims_added:
						if d == s['discrim']:
							discrim_there = True
							break
					if discrim_there:
						continue
					results += "{0} {1} `{2}`\n".format(name, s['discrim'], s['time'])
					discrims_added.append(s['discrim'])
					names_added.append(name.replace('**Discriminator Change** ', ''))
					continue
				for x in names_added:
					if x == name:
						already_there = True
						break
				if already_there:
					continue
				names_added.append(name)
				if s['nickname'] == '1':
					if s['server'] == ctx.message.server.id:
						if name == user.nick:
							results += "**Current** [Nickname] \"{0}\" `{1}`\n".format(name, s['time'])
						else:
							results += "[Nickname] \"{0}\" `{1}`\n".format(name, s['time'])
				else:
					if name == user.name:
						results += "**Current** \"{0}\" `{1}`\n".format(name, s['time'])
					else:
						results += "\"{0}\" `{1}`\n".format(name, s['time'])
			nick_added = True
			if user.nick != None and user.nick not in names_added:
				results += "\"{0}\" `{1}`\n".format(user.nick, 'Current')
				nick_added = False
			if user.name != names_added[-1] and user.name != names_added[-2] and user.name != names_added[-3] and nick_added:
				results += "\"{0}\" `{1}`\n".format(user.name, 'Current')
			if len(results) == 0:
				await self.bot.say(":no_entry: \"{0}\" does not have any name changes recorded!".format(user.name))
				return
			final = "**Name/Nickname Logs for** `{0}`\n".format(user.name)+results
			if len(final) >= 1999:
				results = results.replace('`', '').replace('*', '-')
				await self.gist(ctx, 1, user.name, results)
			else:
				await self.bot.say(final)
		except Exception as e:
			await self.bot.say(e)

	@commands.command(pass_context=True, aliases=['servernames', 'sname'])
	@commands.cooldown(1, 15)
	async def snames(self, ctx):
		"""Show all the logs the bot has of the servers name"""
		try:
			server = ctx.message.server
			sql = "SELECT name,time FROM `server_names` WHERE id={0}"
			sql = sql.format(server.id)
			result = self.cursor.execute(sql).fetchall()
			if len(result) == 0:
				await self.bot.say(":no_entry: Server \"{0}\" does not have any name changes recorded!".format(server.name))
				return
			results = ""
			for s in result:
				name = s['name'].replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
				if name == server.name:
					results += "**Current** \"{0}\" `{1}`\n".format(name, s['time'])
				else:
					results += "\"{0}\" `{1}`\n".format(name, s['time'])
			final = "**Server Name Logs for** `{0}`\n".format(server.name)+results
			if len(final) >= 1999:
				results = results.replace('`', '').replace('*', '-')
				await self.gist(ctx, 2, server.name, results)
			else:
				await self.bot.say(final)
		except Exception as e:
			await self.bot.say(e)

	async def on_member_update(self, before, after):
		if before == self.bot.user:
			return
		time = strftime("%m-%d-%Y|%I:%M (EST)")
		if before.discriminator != after.discriminator:
			sql = "INSERT INTO `names` (`id`, `name`, `nickname`, `time`, `server`, `discrim`) VALUES (%s, %s, %s, %s, %s, %s)"
			self.cursor.execute(sql, (before.id, '**Discriminator Change** '+after.name, '0', time, before.server.id, '`#{0}` => `#{1}`'.format(before.discriminator, after.discriminator)))
			self.cursor.commit()
		if before.name != after.name:
			if before.name == after.name:
				return
			check = 'SELECT * FROM `names` WHERE id={0}'
			check = check.format(before.id)
			result = self.cursor.execute(check).fetchall()
			if len(result) == 0:
				sql = "INSERT INTO `names` (`id`, `name`, `nickname`, `time`, `server`) VALUES (%s, %s, %s, %s, %s)"
				self.cursor.execute(sql, (before.id, before.name, '0', time, before.server.id))
				self.cursor.commit()
			sql = "INSERT INTO `names` (`id`, `name`, `nickname`, `time`, `server`) VALUES (%s, %s, %s, %s, %s)"
			self.cursor.execute(sql, (before.id, after.name, '0', time, before.server.id))
			self.cursor.commit()
		elif before.nick != None or (before.nick is None and after.nick != None):
			if before.nick != None:
				if before.nick == after.nick:
					return
				if after.nick is None:
					return
			sql = "INSERT INTO `names` (`id`, `name`, `nickname`, `time`, `server`) VALUES (%s, %s, %s, %s, %s)"
			self.cursor.execute(sql, (before.id, after.nick, '1', time, before.server.id))
			self.cursor.commit()

	async def on_server_update(self, before, after):
		if before == self.bot.user:
			return
		time = strftime("%m-%d-%Y|%I:%M (EST)")
		if before.name != after.name:
			check = 'SELECT * FROM `server_names` WHERE id={0}'
			check = check.format(before.id)
			result = self.cursor.execute(check).fetchall()
			if len(result) == 0:
				sql = "INSERT INTO `server_names` (`id`, `name`, `time`) VALUES (%s, %s, %s)"
				self.cursor.execute(sql, (before.id, before.name, time))
				self.cursor.commit()
			sql = "INSERT INTO `server_names` (`id`, `name`, `time`) VALUES (%s, %s, %s)"
			self.cursor.execute(sql, (before.id, after.name, time))
			self.cursor.commit()

def setup(bot):
	bot.add_cog(Changes(bot))
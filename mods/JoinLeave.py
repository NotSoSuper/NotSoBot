import discord
import asyncio
from discord.ext import commands
from utils import checks
from mods.cog import Cog
import mods.Tags

parser = mods.Tags.Tags.parser
default_join = 'Welcome to **{server}** - {mention}! You are the {servercount} member to join.'
default_leave = '**{user}#{discrim}** has left the server.'

#http://stackoverflow.com/a/16671271
def number_formating(n):
	return str(n)+("th" if 4<=n%100<=20 else {1:"st",2:"nd",3:"rd"}.get(n%10, "th"))

class Object():
	pass

cool = "```xl\n{0}\n```"
code = "```py\n{0}\n```"

class JoinLeave(Cog):
	def __init__(self, bot):
		super().__init__(bot)
		self.cursor = bot.mysql.cursor
		self.escape = bot.escape

	@commands.group(pass_context=True, aliases=['welcomemessage', 'join'], invoke_without_command=True, no_pm=True)
	@checks.admin_or_perm(manage_server=True)
	async def welcome(self, ctx, *, message:str=None):
		channel = ctx.message.channel
		for c in ctx.message.channel_mentions:
			channel = c
			message = message.replace(c.mention, '').replace('#'+c.name, '')
		sql = 'SELECT server FROM `welcome` WHERE server={0}'
		sql = sql.format(ctx.message.server.id)
		result = self.cursor.execute(sql).fetchall()
		if len(result) == 0:
			if message is None:
				msg = ':white_check_mark: Enabled welcome messages for {0}.'.format(channel.mention)
			else:
				msg = ':white_check_mark: Added welcome message for {0}.'.format(channel.mention)
			sql = 'INSERT INTO `welcome` (`server`, `channel`, `message`, `user`) VALUES (%s, %s, %s, %s)'
			self.cursor.execute(sql, (ctx.message.server.id, channel.id, message, ctx.message.author.id))
		else:
			if message is None:
				await self.bot.say(':warning: Please input something to edit the welcome message to.\n`welcome clear` to disable welcome messages.')
				return
			msg = ':white_check_mark: Edited welcome message.'
			sql = "UPDATE `welcome` SET message={0} WHERE server={1}"
			sql = sql.format(self.escape(message), ctx.message.server.id)
			self.cursor.execute(sql)
		self.cursor.commit()
		await self.bot.say(msg)

	@welcome.command(name='remove', pass_context=True, aliases=['delete', 'clear', 'disable'], invoke_without_command=True)
	@checks.admin_or_perm(manage_server=True)
	async def welcome_remove(self, ctx):
		sql = 'SELECT server FROM `welcome` WHERE server={0}'
		sql = sql.format(ctx.message.server.id)
		result = self.cursor.execute(sql).fetchall()
		if len(result) == 0:
			await self.bot.say(':no_entry: Server does not have welcome messages enabled.')
			return
		sql = 'DELETE FROM `welcome` WHERE server={0}'
		sql = sql.format(ctx.message.server.id)
		self.cursor.execute(sql)
		self.cursor.commit()
		await self.bot.say(':negative_squared_cross_mark: Disabled welcome message.')

	@welcome.command(name='channel', pass_context=True, aliases=['setchannel'], invoke_without_command=True)
	@checks.admin_or_perm(manage_server=True)
	async def welcome_channel(self, ctx, channel:discord.Channel=None):
		sql = 'SELECT channel FROM `welcome` WHERE server={0}'
		sql = sql.format(ctx.message.server.id)
		result = self.cursor.execute(sql).fetchall()
		if len(result) == 0:
			await self.bot.say(':no_entry: Server does not have welcome messages enabled.')
			return
		if channel is None:
			channel = ctx.message.server.get_channel(str(result[0]['channel']))
			if channel is None:
				channel = ctx.message.channel
			else:
				await self.bot.say('Current Welcome Channel: {0}'.format(channel.mention))
				return
		sql = 'UPDATE `welcome` SET channel={0} WHERE server={1}'
		sql = sql.format(channel.id, ctx.message.server.id)
		self.cursor.execute(sql)
		self.cursor.commit()
		await self.bot.say(':white_check_mark: Changed welcome channel to {0}'.format(channel.mention))

	@commands.group(pass_context=True, aliases=['leavemessage'], invoke_without_command=True, no_pm=True)
	@checks.admin_or_perm(manage_server=True)
	async def leave(self, ctx, *, message:str=None):
		channel = ctx.message.channel
		for c in ctx.message.channel_mentions:
			channel = c
			message = message.replace(c.mention, '').replace('#'+c.name, '')
		sql = 'SELECT server FROM `leave` WHERE server={0}'
		sql = sql.format(ctx.message.server.id)
		result = self.cursor.execute(sql).fetchall()
		if len(result) == 0:
			if message is None:
				msg = ':white_check_mark: Enabled leave messages for {0}.'.format(channel.mention)
			else:
				msg = ':white_check_mark: Added leave message for {0}.'.format(channel.mention)
			sql = 'INSERT INTO `leave` (`server`, `channel`, `message`, `user`) VALUES (%s, %s, %s, %s)'
			self.cursor.execute(sql, (ctx.message.server.id, channel.id, message, ctx.message.author.id))
		else:
			if message is None:
				await self.bot.say(':warning: Please input something to edit the leave message to.\n`leave clear` to disable leave messages.')
				return
			msg = ':white_check_mark: Edited leave message.'
			sql = "UPDATE `leave` SET message={0} WHERE server={1}"
			sql = sql.format(self.escape(message), ctx.message.server.id)
			self.cursor.execute(sql)
		self.cursor.commit()
		await self.bot.say(msg)

	@leave.command(name='remove', pass_context=True, aliases=['delete', 'clear', 'disable'], invoke_without_command=True)
	@checks.admin_or_perm(manage_server=True)
	async def leave_remove(self, ctx):
		sql = 'SELECT server FROM `leave` WHERE server={0}'
		sql = sql.format(ctx.message.server.id)
		result = self.cursor.execute(sql).fetchall()
		if len(result) == 0:
			await self.bot.say(':no_entry: Server does not have leave messages enabled.')
			return
		sql = 'DELETE FROM `leave` WHERE server={0}'
		sql = sql.format(ctx.message.server.id)
		self.cursor.execute(sql)
		self.cursor.commit()
		await self.bot.say(':negative_squared_cross_mark: Disabled leave message.')

	@leave.command(name='channel', pass_context=True, aliases=['setchannel'], invoke_without_command=True)
	@checks.admin_or_perm(manage_server=True)
	async def leave_channel(self, ctx, channel:discord.Channel=None):
		sql = 'SELECT channel FROM `leave` WHERE server={0}'
		sql = sql.format(ctx.message.server.id)
		result = self.cursor.execute(sql).fetchall()
		if len(result) == 0:
			await self.bot.say(':no_entry: Server does not have leave messages enabled.')
			return
		if channel is None:
			channel = ctx.message.server.get_channel(str(result[0]['channel']))
			if channel is None:
				channel = ctx.message.channel
			else:
				await self.bot.say('Current Leave Channel: {0}'.format(channel.mention))
				return
		sql = 'UPDATE `leave` SET channel={0} WHERE server={1}'
		sql = sql.format(channel.id, ctx.message.server.id)
		self.cursor.execute(sql)
		self.cursor.commit()
		await self.bot.say(':white_check_mark: Changed leave channel to {0}'.format(channel.mention))

	@welcome.command(name='current', pass_context=True, aliases=['show'], invoke_without_command=True)
	async def welcome_current(self, ctx):
		sql = 'SELECT message FROM `welcome` WHERE server={0}'
		sql = sql.format(ctx.message.server.id)
		result = self.cursor.execute(sql).fetchall()
		if len(result) == 0:
			await self.bot.say(':no_entry: Server does not have welcome messages enabled.')
			return
		msg = result[0]['message'] if result[0]['message'] != None else default_join
		await self.bot.say(msg)

	@leave.command(name='current', pass_context=True, aliases=['show'], invoke_without_command=True)
	async def leave_current(self, ctx):
		sql = 'SELECT message FROM `leave` WHERE server={0}'
		sql = sql.format(ctx.message.server.id)
		result = self.cursor.execute(sql).fetchall()
		if len(result) == 0:
			await self.bot.say(':no_entry: Server does not have leave messages enabled.')
			return
		msg = result[0]['message'] if result[0]['message'] != None else default_leave
		await self.bot.say(msg)

	async def remove(self, server, welcome):
		if welcome:
			sql = 'DELETE FROM `welcome` WHERE server={0}'
		else:
			sql = 'DELETE FROM `leave` WHERE server={0}'
		sql = sql.format(server.id)
		self.cursor.execute(sql)
		self.cursor.commit()

	async def on_member_join(self, member):
		try:
			server = member.server
			sql = 'SELECT * FROM `welcome` WHERE server={0}'
			sql = sql.format(server.id)
			result = self.cursor.execute(sql).fetchall()
			if len(result) == 0:
				return
			channel = server.get_channel(str(result[0]['channel']))
			if channel is None:
				await self.remove(server, True)
			ctx = Object()
			ctx.message = Object()
			ctx.message.author = member
			ctx.message.server = server
			ctx.message.channel = channel
			msg = result[0]['message']
			join_message = msg if msg != None and len(msg) != 0 else default_join
			message = await parser(self, ctx, join_message.replace('{servercount}', number_formating(len(server.members))).replace('{membercount}', number_formating(len(server.members))), ())
			await self.bot.send_message(channel, message, replace_mentions=False, replace_everyone=False)
		except (discord.errors.Forbidden, discord.errors.NotFound, discord.errors.InvalidArgument):
			await self.remove(server, True)

	async def on_member_remove(self, member):
		try:
			server = member.server
			sql = 'SELECT * FROM `leave` WHERE server={0}'
			sql = sql.format(server.id)
			result = self.cursor.execute(sql).fetchall()
			if len(result) == 0:
				return
			channel = server.get_channel(str(result[0]['channel']))
			if channel is None:
				await self.remove(server, False)
			ctx = Object()
			ctx.message = Object()
			ctx.message.author = member
			ctx.message.server = server
			ctx.message.channel = channel
			msg = result[0]['message']
			leave_message = msg if msg != None and len(msg) != 0 else default_leave
			message = await parser(self, ctx, leave_message.replace('{servercount}', number_formating(len(server.members))).replace('{membercount}', number_formating(len(server.members))), ())
			await self.bot.send_message(channel, message, replace_mentions=False, replace_everyone=False)
		except (discord.errors.Forbidden, discord.errors.NotFound, discord.errors.InvalidArgument):
			await self.remove(server, False)

def setup(bot):
	bot.add_cog(JoinLeave(bot))
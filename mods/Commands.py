import asyncio
import discord
import sys
from discord.ext import commands
from utils import checks
from mods.cog import Cog

class Commands(Cog):
	def __init__(self, bot):
		super().__init__(bot)
		self.cursor = bot.mysql.cursor
		self.escape = bot.escape

	@commands.group(pass_context=True, aliases=['setprefix', 'changeprefix'], invoke_without_command=True, no_pm=True)
	@checks.admin_or_perm(manage_server=True)
	async def prefix(self, ctx, *, txt:str=None):
		"""Change the Bots Prefix for the Server"""
		if txt is None:
			sql = "SELECT prefix FROM `prefix` WHERE server={0}"
			sql = sql.format(ctx.message.server.id)
			sql_channel = "SELECT prefix FROM `prefix_channel` WHERE server={0} AND channel={1}"
			sql_channel = sql_channel.format(ctx.message.server.id, ctx.message.channel.id)
			result = self.cursor.execute(sql).fetchall()
			result2 = self.cursor.execute(sql_channel).fetchall()
			if len(result) == 0:
				server_prefix = '.'
			else:
				server_prefix = result[0]['prefix']
			if len(result2) == 0:
				channel_prefix = None
			else:
				channel_prefix = result2[0]['prefix']
			msg = "Server Prefix: `{0}`\n".format(server_prefix)
			if channel_prefix != None:
				msg += "**Current** Channel Prefix: `{0}`".format(channel_prefix)
			await self.bot.say(msg)
			return
		sql = "INSERT INTO `prefix` (`server`, `prefix`, `id`) VALUES (%s, %s, %s)"
		update_sql = "UPDATE `prefix` SET prefix={0} WHERE server={1}"
		update_sql = update_sql.format(self.escape(txt), ctx.message.server.id)
		check = "SELECT server FROM `prefix` WHERE server={0}"
		check = check.format(ctx.message.server.id)
		result = self.cursor.execute(check).fetchall()
		if len(result) == 0:
			self.cursor.execute(sql, (ctx.message.server.id, txt, ctx.message.author.id))
			self.cursor.commit()
			await self.bot.say(":white_check_mark: Set bot prefix to \"{0}\" for the server\n".format(txt))
		else:
			self.cursor.execute(update_sql)
			self.cursor.commit()
			await self.bot.say(":white_check_mark: Updated bot prefix to \"{0}\" for the server".format(txt))

	@prefix.command(pass_context=True, name='channel', no_pm=True)
	@checks.admin_or_perm(manage_server=True)
	async def _prefix_channel(self, ctx, *, txt:str):
		"""Change the Bots Prefix for the current Channel"""
		channel = ctx.message.channel
		for c in ctx.message.channel_mentions:
			channel = c
			txt = txt.replace(channel.mention, '').replace('#'+channel.name, '')
		sql = "INSERT INTO `prefix_channel` (`server`, `prefix`, `channel`, `id`) VALUES (%s, %s, %s, %s)"
		update_sql = "UPDATE `prefix_channel` SET prefix={0} WHERE server={1} AND channel={2}"
		update_sql = update_sql.format(self.escape(txt), ctx.message.server.id, channel.id)
		check = "SELECT * FROM `prefix_channel` WHERE server={0} AND channel={1}"
		check = check.format(ctx.message.server.id, channel.id)
		result = self.cursor.execute(check).fetchall()
		if len(result) == 0:
			self.cursor.execute(sql, (ctx.message.server.id, txt, channel.id, ctx.message.author.id))
			self.cursor.commit()
			await self.bot.say(":white_check_mark: Set bot prefix to \"{0}\" for {1}".format(txt, channel.mention))
		else:
			self.cursor.execute(update_sql)
			self.cursor.commit()
			await self.bot.say(":white_check_mark: Updated bot prefix to \"{0}\" for {1}".format(txt, channel.mention))

	@prefix.command(pass_context=True, name='reset', no_pm=True)
	@checks.admin_or_perm(manage_server=True)
	async def _prefix_reset(self, ctx, what:str=None, channel:discord.Channel=None):
		"""Reset All Custom Set Prefixes For the Bot"""
		if what is None or what == "server":
			sql = "DELETE FROM `prefix` WHERE server={0}"
			sql = sql.format(ctx.message.server.id)
			check = "SELECT * FROM `prefix` WHERE server={0}"
			check = check.format(ctx.message.server.id)
			result = self.cursor.execute(check).fetchall()
			if len(result) == 0:
				await self.bot.say(":no_entry: Current server does **not** have a custom prefix set!")
				return
			else:
				self.cursor.execute(sql)
				self.cursor.commit()
				await self.bot.say(":exclamation: **Reset server prefix**\nThis does not reset channel prefixes, run \"all\" after reset to reset all prefixes *or* \"channels\" to reset all custom channel prefixes.")
		elif what == "channel":
			if channel is None:
				channel = ctx.message.channel
			sql = "DELETE FROM `prefix_channel` WHERE server={0} AND channel={1}"
			sql = sql.format(ctx.message.server.id, channel.id)
			check = "SELECT * FROM `prefix_channel` WHERE server={0} AND channel={1}"
			check = check.format(ctx.message.server.id, channel.id)
			result = self.cursor.execute(check).fetchall()
			if len(result) == 0:
				await self.bot.say(":no_entry: {0} does **not** have a custom prefix Set!\nMention the channel after \"reset channel\" for a specific channel.".format(channel.mention))
				return
			else:
				self.cursor.execute(sql)
				self.cursor.commit()
				await self.bot.say(":exclamation: Reset {0}'s prefix!\nThis does **not** reset all custom channel prefixes, \"reset channels\" to do so.".format(channel.mention))
				return
		elif what == "channels":
			sql = "DELETE FROM `prefix_channel` WHERE server={0}"
			sql = sql.format(ctx.message.server.id)
			check = "SELECT * FROM `prefix_channel` WHERE server={0}"
			check = check.format(ctx.message.server.id)
			result = self.cursor.execute(check).fetchall()
			if len(result) == 0:
				await self.bot.say(":no_entry: Server does **not** reset a custom prefix set for any channel!\nMention the channel after \"reset channel\" for a specific channel.")
				return
			else:
				self.cursor.execute(sql)
				self.cursor.commit()
				await self.bot.say(":exclamation: Reset all channels custom prefixes!")
				return
		elif what == "all" or what == "everything":
			sql = "DELETE FROM `prefix_channel` WHERE server={0}"
			sql = sql.format(ctx.message.server.id)
			sql2 = "DELETE FROM `prefix` WHERE server={0}"
			sql2 = sql2.format(ctx.message.server.id)
			self.cursor.execute(sql)
			self.cursor.execute(sql2)
			self.cursor.commit()
			await self.bot.say(":warning: Reset all custom server prefix settings!")
			return
		else:
			await self.bot.say(":no_entry: Invalid Option\nOptions: `server, channel, channels, all/everything`")

	good_commands = ['command', 'blacklist', 'help', 'invite']
	async def command_toggle(self, t:str, ctx, cmd:str, user=None, msg=True):
		try:
			if cmd in self.good_commands:
				await self.bot.send_message(ctx.message.channel, ':no_entry: You cannot disable command: `{0}`!'.format(self.good_commands[self.good_commands.index(cmd)]))
				return
			if t == 'server':
				sql = "SELECT * FROM `command_blacklist` WHERE type='server' AND server={0} AND command={1}"
				sql = sql.format(ctx.message.server.id, self.escape(cmd))
				result = self.cursor.execute(sql).fetchall()
				if len(result) == 0:
					sql = 'INSERT INTO `command_blacklist` (`command`, `type`, `server`) VALUES (%s, %s, %s)'
					self.cursor.execute(sql, (cmd, "server", ctx.message.server.id))
					self.cursor.commit()
					if msg:
						await self.bot.send_message(ctx.message.channel, ':negative_squared_cross_mark: Disabled command `{0}`.'.format(cmd))
				else:
					sql = "DELETE FROM `command_blacklist` WHERE type='server' AND server={0} AND command={1}"
					sql = sql.format(ctx.message.server.id, self.escape(cmd))
					self.cursor.execute(sql)
					self.cursor.commit()
					if msg:
						await self.bot.send_message(ctx.message.channel, ':white_check_mark: Enabled command `{0}`.'.format(cmd))
			elif t == 'channel':
				channel = user
				sql = "SELECT * FROM `command_blacklist` WHERE type='channel' AND server={0} AND channel={1} AND command={2}"
				sql = sql.format(ctx.message.server.id, channel.id, self.escape(cmd))
				result = self.cursor.execute(sql).fetchall()
				if len(result) == 0:
					sql = 'INSERT INTO `command_blacklist` (`command`, `type`, `server`, `channel`) VALUES (%s, %s, %s, %s)'
					self.cursor.execute(sql, (cmd, "channel", ctx.message.server.id, channel.id))
					self.cursor.commit()
					if msg:
						await self.bot.send_message(ctx.message.channel, ':negative_squared_cross_mark: Disabled command `{0}` for channel {1}.'.format(cmd, channel.mention))
				else:
					sql = "DELETE FROM `command_blacklist` WHERE type='channel' AND server={0} AND channel={1} AND command={2}"
					sql = sql.format(ctx.message.server.id, channel.id, self.escape(cmd))
					self.cursor.execute(sql)
					self.cursor.commit()
					if msg:
						await self.bot.send_message(ctx.message.channel, ':white_check_mark: Enabled command `{0}` for channel {1}.'.format(cmd, channel.mention))
			elif t == 'user':
				sql = "SELECT * FROM `command_blacklist` WHERE type='user' AND server={0} AND user={1} AND command={2}"
				sql = sql.format(ctx.message.server.id, user.id, self.escape(cmd))
				result = self.cursor.execute(sql).fetchall()
				if len(result) == 0:
					sql = 'INSERT INTO `command_blacklist` (`command`, `type`, `server`, `user`) VALUES (%s, %s, %s, %s)'
					self.cursor.execute(sql, (cmd, "user", ctx.message.server.id, user.id))
					self.cursor.commit()
					if msg:
						await self.bot.send_message(ctx.message.channel, ':negative_squared_cross_mark: Disabled command `{0}` for user `{1}`.'.format(cmd, user))
				else:
					sql = "DELETE FROM `command_blacklist` WHERE type='user' AND server={0} AND user={1} AND command={2}"
					sql = sql.format(ctx.message.server.id, user.id, self.escape(cmd))
					self.cursor.execute(sql)
					self.cursor.commit()
					if msg:
						await self.bot.send_message(ctx.message.channel, ':white_check_mark: Enabled command `{0}` for user `{1}`.'.format(cmd, user))
			elif t == 'role':
				role = user
				sql = "SELECT * FROM `command_blacklist` WHERE type='role' AND server={0} AND role={1} AND command={2}"
				sql = sql.format(ctx.message.server.id, role.id, self.escape(cmd))
				result = self.cursor.execute(sql).fetchall()
				if len(result) == 0:
					sql = 'INSERT INTO `command_blacklist` (`command`, `type`, `server`, `role`) VALUES (%s, %s, %s, %s)'
					self.cursor.execute(sql, (cmd, "role", ctx.message.server.id, role.id))
					self.cursor.commit()
					if msg:
						await self.bot.send_message(ctx.message.channel, ':negative_squared_cross_mark: Disabled command `{0}` for role {1}.'.format(cmd, role.mention))
				else:
					sql = "DELETE FROM `command_blacklist` WHERE type='role' AND server={0} AND role={1} AND command={2}"
					sql = sql.format(ctx.message.server.id, role.id, self.escape(cmd))
					self.cursor.execute(sql)
					self.cursor.commit()
					if msg:
						await self.bot.send_message(ctx.message.channel, ':white_check_mark: Enabled command `{0}` for role {1}.'.format(cmd, role.mention))
			elif t == 'global':
				sql = "SELECT * FROM `command_blacklist` WHERE type='global' AND command={0}"
				sql = sql.format(self.escape(cmd))
				result = self.cursor.execute(sql).fetchall()
				if len(result) == 0:
					sql = 'INSERT INTO `command_blacklist` (`command`, `type`) VALUES (%s, %s)'
					self.cursor.execute(sql, (cmd, "global"))
					self.cursor.commit()
					if msg:
						await self.bot.send_message(ctx.message.channel, ':globe_with_meridians: Disabled command `{0}` globally.'.format(cmd))
				else:
					sql = "DELETE FROM `command_blacklist` WHERE type='global' AND command={0}"
					sql = sql.format(self.escape(cmd))
					self.cursor.execute(sql)
					self.cursor.commit()
					if msg:
						await self.bot.send_message(ctx.message.channel, ':white_check_mark: Enabled command `{0}` globally.'.format(cmd))
			else:
				return
		except Exception as e:
			await self.bot.send_message(ctx.message.channel, str(e))

	async def module_command_toggle(self, module, t:str, ctx):
		try:
			count = 0
			disabled = []
			for command in self.bot.commands:
				if self.bot.commands[command].module == module and command not in disabled:
					count += 1
					cmd = str(self.bot.commands[command].name)
					await self.command_toggle(t, ctx, cmd, msg=False)
					await asyncio.sleep(0.21)
					disabled.append(command)
			return count
		except Exception as e:
			await self.bot.send_message(ctx.message.channel, str(e))

	async def get_modules(self):
		modules = []
		for module in sys.modules:
			if module.startswith('mods.'):
				if module == 'mods.Repl' or module == 'mods.Stats' or module == 'mods.Commands':
					continue
				mod = module.replace('mods.', '')
				modules.append(mod)
		return modules

	@commands.group(pass_context=True, invoke_without_command=True, aliases=['commands', 'cmd'], no_pm=True)
	@checks.admin_or_perm(manage_server=True)
	async def command(self, ctx, cmd:str):
		"""Toggle a command for the server"""
		if cmd in self.bot.commands:
			cmd = str(self.bot.commands[cmd])
			await self.command_toggle('server', ctx, cmd)
		else:
			await self.bot.say(':no_entry: `Command does not exist.`')

	@command.command(name='toggle', aliases=['enable', 'disable'], pass_context=True, invoke_without_command=True, no_pm=True)
	@checks.admin_or_perm(manage_server=True)
	async def cmd_toggle(self, ctx, cmd:str):
		"""Server wide Command Toggle"""
		if cmd in self.bot.commands:
			cmd = str(self.bot.commands[cmd])
			await self.command_toggle('server', ctx, cmd)
		else:
			await self.bot.say(':no_entry: `Command does not exist.`')

	@command.command(name='user', pass_context=True, aliases=['member'], invoke_without_command=True, no_pm=True)
	@checks.admin_or_perm(manage_server=True)
	async def command_toggle_user(self, ctx, cmd:str, user:discord.User=None):
		"""Toggle Command for a user"""
		if user is None:
			user = ctx.message.author
		if cmd in self.bot.commands:
			cmd = str(self.bot.commands[cmd])
			await self.command_toggle('user', ctx, cmd, user)
		else:
			await self.bot.say(':no_entry: `Command does not exist.`')

	@command.command(name='role', pass_context=True, aliases=['rank'], invoke_without_command=True, no_pm=True)
	@checks.admin_or_perm(manage_server=True)
	async def command_toggle_role(self, ctx, cmd:str, role:discord.Role):
		"""Toggle Command for a role"""
		if cmd in self.bot.commands:
			cmd = str(self.bot.commands[cmd])
			await self.command_toggle('role', ctx, cmd, role)
		else:
			await self.bot.say(':no_entry: `Command does not exist.`')

	@command.command(name='channel', pass_context=True, invoke_without_command=True, no_pm=True)
	@checks.admin_or_perm(manage_server=True)
	async def command_toggle_channel(self, ctx, cmd:str, chan:discord.Channel=None):
		"""Toggle Command for a channel"""
		if chan is None:
			chan = ctx.message.channel
		if cmd in self.bot.commands:
			cmd = str(self.bot.commands[cmd])
			await self.command_toggle('channel', ctx, cmd, chan)
		else:
			await self.bot.say(':no_entry: `Command does not exist.`')

	@command.command(name='global', pass_context=True, invoke_without_command=True)
	@checks.is_owner()
	async def command_toggle_global(self, ctx, cmd:str):
		"""Toggle command globally"""
		if cmd in self.bot.commands:
			cmd = str(self.bot.commands[cmd])
			await self.command_toggle('global', ctx, cmd)
		else:
			await self.bot.say(':no_entry: `Command does not exist.`')

	@command.group(name='module', pass_context=True, invoke_without_command=True, no_pm=True)
	@checks.admin_or_perm(manage_server=True)
	async def command_toggle_module(self, ctx, module:str, chan:discord.Channel=None):
		"""Toggle a bot command module"""
		try:
			mod = sys.modules['mods.{0}'.format(module)]
		except KeyError:
			modules = await self.get_modules()
			await self.bot.say(':no_entry: Invalid Module\n**Modules**\n`{0}`'.format(', '.join(modules)))
			return
		if chan:
			count = await self.module_command_toggle(mod, 'channel', ctx)
		else:
			count = await self.module_command_toggle(mod, 'server', ctx)
		await self.bot.say(':white_check_mark: Disabled **{0}** commands in module `{1}`.'.format(count, module))

	@command_toggle_module.command(name='list', pass_context=True, invoke_without_command=True)
	async def command_toggle_module_list(self, ctx):
		modules = await self.get_modules()
		await self.bot.say(':information_source: **Modules**\n`{0}`'.format(', '.join(modules)))

	@command.command(name='all', pass_context=True, invoke_without_command=True, no_pm=True)
	@checks.admin_or_perm(manage_server=True)
	async def command_toggle_all(self, ctx):
		sql = 'SELECT COUNT(*) FROM `command_blacklist` WHERE server={0}'
		sql = sql.format(ctx.message.server.id)
		count = str(self.cursor.execute(sql).fetchall()[0]['COUNT(*)'])
		sql = 'DELETE FROM `command_blacklist` WHERE server={0}'
		sql = sql.format(ctx.message.server.id)
		self.cursor.execute(sql)
		self.cursor.commit()
		await self.bot.say(':white_check_mark: Enabled **{0}** server command(s).'.format(count))

	@command.command(name='list', pass_context=True, invoke_without_command=True, no_pm=True)
	async def command_list(self, ctx):
		sql = 'SELECT * FROM `command_blacklist` WHERE server={0} OR type="global"'
		sql = sql.format(ctx.message.server.id)
		result = self.cursor.execute(sql).fetchall()
		if len(result) == 0:
			await self.bot.say(':no_entry: Server does **not** have any commands blacklisted.')
			return
		msg = ''
		for s in result:
			if s['type'] == 'global':
				msg += ':globe_with_meridians: Globaly Command Disabled: `{0}`\n'.format(s['command'])
			elif s['type'] == 'server':
				msg += ':desktop: Command Disabled on Server: `{0}`\n'.format(s['command'])
			elif s['type'] == 'channel':
				msg += ':arrow_right: Command Disabled in <#{0}>: `{1}`\n'.format(s['channel'] ,s['command'])
			elif s['type'] == 'role':
				msg += ':eight_spoked_asterisk: Command Disabled for <@&{0}>: `{1}`\n'.format(s['role'], s['command'])
			elif s['type'] == 'user':
				user = discord.utils.get(self.bot.get_all_members(), id=str(s['user']))
				if user is None:
					user = '<@{0}> (Not Found)'.format(s['user'])
				msg += ':bust_in_silhouette: Command Disabled for **{0}**: `{1}`\n'.format(user, s['command'])
		await self.bot.say(':white_check_mark: **Commands Disabled**\n'+msg)

def setup(bot):
	bot.add_cog(Commands(bot))
import asyncio
import discord
import sys
import re
import time
import numpy as np
import PIL
import datetime
from discord.ext import commands
from utils import checks
from io import BytesIO
from mods.cog import Cog

cool = "```xl\n{0}\n```"
code = "```py\n{0}\n```"

class Logs(Cog):
	def __init__(self, bot):
		super().__init__(bot)
		self.cursor = bot.mysql.cursor
		self.escape = bot.escape
		self.discord_path = bot.path.discord
		self.files_path = bot.path.files
		self.download = bot.download
		self.bytes_download = bot.bytes_download
		self.truncate = bot.truncate
		self.banned_users = {}
		self.attachment_cache = {}

	def remove_server(self, server):
		remove_sql = "DELETE FROM `logs` WHERE server={0}"
		remove_sql = remove_sql.format(server.id)
		self.cursor.execute(remove_sql)
		self.cursor.commit()

	def remove_server_tracking(self, server):
		remove_sql = "DELETE FROM `tracking` WHERE server={0}"
		remove_sql = remove_sql.format(server.id)
		self.cursor.execute(remove_sql)
		self.cursor.commit()

	@commands.group(pass_context=True, aliases=['slogs', 'adminlogs'], no_pm=True, invoke_without_command=True)
	@checks.admin_or_perm(manage_server=True)
	async def serverlogs(self, ctx, channel:discord.Channel=None):
		"""Setup Server Logs for a Specific Channel or Current Channel"""
		sql = "INSERT INTO `logs` (`server`, `channel`) VALUES (%s, %s)"
		if channel is None:
			chan = ctx.message.channel
		else:
			chan = channel
		update_sql = "UPDATE `logs` SET channel={0} WHERE server={1}"
		update_sql = update_sql.format(chan.id, ctx.message.server.id)
		remove_sql = "DELETE FROM `logs` WHERE server={0}"
		remove_sql = remove_sql.format(ctx.message.server.id)
		check = "SELECT channel FROM `logs` WHERE server={0}"
		check = check.format(ctx.message.server.id)
		result = self.cursor.execute(check).fetchall()
		if len(result) == 0:
			self.cursor.execute(sql, (ctx.message.server.id, chan.id))
			self.cursor.commit()
			await self.bot.say(":white_check_mark: Set Server Logs to {0.mention}".format(chan))
		elif str(result[0]['channel']) == ctx.message.channel.id:
			self.cursor.execute(remove_sql)
			self.cursor.commit()
			await self.bot.say(":negative_squared_cross_mark: Disabled Server Logs.")
		else:
			self.cursor.execute(update_sql)
			self.cursor.commit()
			await self.bot.say(":white_check_mark: Updated Server Logs to {0.mention}".format(chan))

	@serverlogs.command(name='disable', aliases=['off', 'clear', 'deactivate'], pass_context=True, no_pm=True)
	async def serverlogs_disable(self, ctx):
		check = "SELECT channel FROM `logs` WHERE server={0}"
		check = check.format(ctx.message.server.id)
		result = self.cursor.execute(check).fetchall()
		if result:
			remove_sql = "DELETE FROM `logs` WHERE server={0}"
			remove_sql = remove_sql.format(ctx.message.server.id)
			self.cursor.execute(remove_sql)
			self.cursor.commit()
			await self.bot.say(":negative_squared_cross_mark: Disabled Server Logs.")
		else:
			await self.bot.say(':no_entry: Server does not have logs enabled!')

	@serverlogs.group(name='ignore', pass_context=True, no_pm=True, invoke_without_command=True)
	@checks.admin_or_perm(manage_server=True)
	async def serverlogs_ignore(self, ctx, *users:str):
		if not users:
			await self.bot.say(':no_entry: Please input user mentions or id(s).')
			return
		members = []
		users = list(users)
		for u in users:
			if u.isdigit():
				member = ctx.message.server.get_member(u)
				if member and member not in members:
					members.append(member)
				else:
					await self.bot.say(':warning: `{0}` is an invalid id.'.format(u))
					users.remove(u)
					if len(users):
						continue
					return
		sql = 'SELECT * FROM `logs` WHERE server={0}'
		sql = sql.format(ctx.message.server.id)
		result = self.cursor.execute(sql).fetchall()
		if not result:
			await self.bot.say(':no_entry: Server does not have logs enabled.')
			return
		s = result[0]
		if s['ignore_users']:
			a = s['ignore_users'].split(', ')
			for u in members:
				if u.id in a:
					sql = 'UPDATE `logs` SET ignore_users={0} WHERE server={1}'
					a.remove(u.id)
					i = self.escape(', '.join(a)) if a else 'NULL'
					sql = sql.format(i, ctx.message.server.id)
					self.cursor.execute(sql)
					self.cursor.commit()
					await self.bot.say(':negative_squared_cross_mark: Removed `{0}` from server log ignore.'.format(u))
					members.remove(u)
					if len(members):
						continue
					return
		sql = 'UPDATE `logs` SET ignore_users={0} WHERE server={1}'
		sql = sql.format(self.escape(', '.join([x.id for x in members])), ctx.message.server.id)
		self.cursor.execute(sql)
		self.cursor.commit()
		await self.bot.say(':white_check_mark: Ignoring `{0}` from server log.'.format(', '.join([str(x) for x in members])))

	@serverlogs_ignore.command(name='avatar', pass_context=True, no_pm=True)
	@checks.admin_or_perm(manage_server=True)
	async def serverlogs_ignore_avatar(self, ctx, *users:str):
		if not users:
			await self.bot.say(':no_entry: Please input user mentions or id(s).')
			return
		members = []
		users = list(users)
		for u in users:
			if u.isdigit():
				member = ctx.message.server.get_member(u)
				if member and member not in members:
					members.append(member)
				else:
					await self.bot.say(':warning: `{0}` is an invalid id.'.format(u))
					users.remove(u)
					if len(users):
						continue
					return
		sql = 'SELECT * FROM `logs` WHERE server={0}'
		sql = sql.format(ctx.message.server.id)
		result = self.cursor.execute(sql).fetchall()
		if not result:
			await self.bot.say(':no_entry: Server does not have logs enabled.')
			return
		s = result[0]
		if s['avatar_ignore']:
			a = s['avatar_ignore'].split(', ')
			for u in members:
				if u.id in a:
					sql = 'UPDATE `logs` SET avatar_ignore={0} WHERE server={1}'
					a.remove(u.id)
					i = self.escape(', '.join(a)) if a else 'NULL'
					sql = sql.format(i, ctx.message.server.id)
					self.cursor.execute(sql)
					self.cursor.commit()
					await self.bot.say(':negative_squared_cross_mark: Removed `{0}` from avatar ignore.'.format(u))
					members.remove(u)
					if len(members):
						continue
					return
		sql = 'UPDATE `logs` SET avatar_ignore={0} WHERE server={1}'
		sql = sql.format(self.escape(', '.join([x.id for x in members])), ctx.message.server.id)
		self.cursor.execute(sql)
		self.cursor.commit()
		await self.bot.say(':white_check_mark: Ignoring `{0}` from avatar log.'.format(', '.join([str(x) for x in members])))

	@serverlogs_ignore.group(name='global', pass_context=True, no_pm=True, invoke_without_command=True)
	@checks.is_owner()
	async def serverlogs_ignore_global(self, ctx, *users:str):
		if not users:
			await self.bot.say(':no_entry: Please input user mentions or id(s).')
			return
		members = []
		users = list(users)
		for u in users:
			if u.isdigit():
				member = ctx.message.server.get_member(u)
				if member and member not in members:
					members.append(member)
				else:
					await self.bot.say(':warning: `{0}` is an invalid id.'.format(u))
					users.remove(u)
					if len(users):
						continue
					return
		sql = 'SELECT * FROM `global_log_ignore` WHERE user={0} AND NOT avatar'
		for user in members:
			result = self.cursor.execute(sql.format(user.id)).fetchall()
			if result:
				sql = 'DELETE FROM `global_log_ignore` WHERE user={0} AND NOT avatar'
				sql = sql.format(user.id)
				self.cursor.execute(sql)
				await self.bot.say(':negative_squared_cross_mark: Removed `{0}` from global log ignore.'.format(user))
			else:
				sql = 'INSERT INTO `global_log_ignore` (`user`) VALUES (%s)'
				self.cursor.execute(sql, (user.id))
				await self.bot.say(':white_check_mark: Added `{0}` to global log ignore.'.format(user))
			self.cursor.commit()

	@serverlogs_ignore_global.command(name='avatar', pass_context=True, no_pm=True)
	@checks.is_owner()
	async def serverlogs_ignore_global_avatar(self, ctx, *users:str):
		if not users:
			await self.bot.say(':no_entry: Please input user mentions or id(s).')
			return
		members = []
		for m in ctx.message.mentions:
			members.append(m)
		users = list(users)
		for u in users:
			if u.isdigit():
				member = ctx.message.server.get_member(u)
				if member and member not in members:
					members.append(member)
				else:
					await self.bot.say(':warning: `{0}` is an invalid id.'.format(u))
					users.remove(u)
					if len(users):
						continue
					return
		sql = 'SELECT * FROM `global_log_ignore` WHERE user={0} AND avatar'
		for user in members:
			result = self.cursor.execute(sql.format(user.id)).fetchall()
			if result:
				sql = 'DELETE FROM `global_log_ignore` WHERE user={0} AND avatar'
				sql = sql.format(user.id)
				self.cursor.execute(sql)
				await self.bot.say(':negative_squared_cross_mark: Removed `{0}` from global avatar log ignore.'.format(user))
			else:
				sql = 'INSERT INTO `global_log_ignore` (`user`, `avatar`) VALUES (%s, %s)'
				self.cursor.execute(sql, (user.id, 1))
				await self.bot.say(':white_check_mark: Added `{0}` to global avatar log ignore.'.format(user))
			self.cursor.commit()

	@commands.group(pass_context=True, invoke_without_command=True, aliases=['messagetracking', 'trackmessage'], no_pm=True)
	@checks.admin_or_perm(manage_server=True)
	async def track(self, ctx, *, txt:str):
		"""Track messages in your server"""
		if len(txt) > 500:
			await self.bot.say(":no_entry: `Text too long (<= 500)`")
			return
		chan = ctx.message.channel
		sql = "INSERT INTO `tracking` (`txt`, `server`, `channel`) VALUES (%s, %s, %s)"
		check = "SELECT txt,id FROM `tracking` WHERE server={0} AND txt={1}"
		check = check.format(ctx.message.server.id, self.escape(txt))
		ssss = "SELECT * FROM `tracking` WHERE server={0}"
		ssss = ssss.format(ctx.message.server.id)
		result = self.cursor.execute(check).fetchall()
		s_result = self.cursor.execute(ssss).fetchall()
		if len(result) == 0 or result[0]['txt'] != txt:
			if len(s_result) != 0 and len(s_result[0]) == 3:
				self.cursor.execute(sql, (txt, ctx.message.server.id, s_result[0]['id']))
				self.cursor.commit()
				await self.bot.say(":white_check_mark: Added \"{0}\" to tracking.".format(txt))
			else:
				self.cursor.execute(sql, (txt, ctx.message.server.id, chan.id))
				self.cursor.commit()
				await self.bot.say(":white_check_mark: Set Channel to track all messages with \"{1}\"\nRun the channel command to change channel it logs in.".format(chan.mention, txt))
		else:
			await self.bot.say(":no_entry: `Tracking for text \"{0}\" already exists!`\nRemove using the remove command.".format(txt))

	@track.command(name='channel', pass_context=True, invoke_without_command=True, no_pm=True)
	async def _track_channel(self, ctx, chan:discord.Channel=None):
		if chan is None:
			chan = ctx.message.channel
		update_sql = 'UPDATE `tracking` SET channel={0} WHERE server={1}'
		update_sql = update_sql.format(chan.id, ctx.message.server.id)
		check = 'SELECT id FROM `tracking` WHERE server={0}'
		check = check.format(ctx.message.server.id)
		result = self.cursor.execute(check).fetchall()
		if len(result) == 0:
			await self.bot.say(":no_entry: `This server is not tracking any messages!`")
		elif result[0]['id'] == chan.id:
			await self.bot.say(":no_entry: `Channel is already the tracking logs channel!`\nUse the remove all command to stop tracking.")
		else:
			self.cursor.execute(update_sql)
			self.cursor.commit()
			await self.bot.say(":white_check_mark: Updated text tracking channel to {0}".format(chan.mention))

	@track.group(name='remove', pass_context=True, invoke_without_command=True, no_pm=True)
	async def _track_remove(self, ctx, *, txt:str):
		remove_sql = "DELETE FROM `tracking` WHERE server={0} AND txt={1}"
		remove_sql = remove_sql.format(ctx.message.server.id, self.escape(txt))
		check = "SELECT * FROM `tracking` WHERE server={0} AND txt={1}"
		check = check.format(ctx.message.server.id, self.escape(txt))
		result = self.cursor.execute(check).fetchall()
		if len(result) == 0:
			await self.bot.say(":no_entry: `That text isn't being tracked!`")
		else:
			self.cursor.execute(remove_sql)
			self.cursor.commit()
			await self.bot.say(":x: Removed text from tracking.")

	@_track_remove.command(name='all', pass_context=True, invoke_without_command=True, no_pm=True)
	async def _track_remove_all(self, ctx):
		sql = "DELETE FROM `tracking` WHERE server={0}"
		sql = sql.format(ctx.message.server.id)
		check = 'SELECT * FROM `tracking` WHERE server={0}'
		check = check.format(ctx.message.server.id)
		result = self.cursor.execute(check).fetchall()
		if len(result) == 0:
			await self.bot.say(":no_entry: `Server has not added any text to be tracked!`")
		else:
			self.cursor.execute(sql)
			self.cursor.commit()
			await self.bot.say(":x: Reset/Removed all tracked text.")

	@track.command(name='list', pass_context=True, invoke_without_command=True, no_pm=True)
	async def _track_list(self, ctx):
		sql = "SELECT txt FROM `tracking` WHERE server={0}"
		sql = sql.format(ctx.message.server.id)
		result = self.cursor.execute(sql).fetchall()
		if len(result) == 0:
			await self.bot.say(":warning: `This server does not have any text being tracked!`")
		else:
			results = ''
			for s in result:
				results += '`{0}`\n'.format(s['txt'])
			await self.bot.say('**All Tracked Text**\n'+results)

	@commands.command(pass_context=True, aliases=['commanddelete', 'cmd_delete', 'command_delete'])
	@checks.admin_or_perm(manage_server=True)
	async def cmddelete(self, ctx):
		sql = 'SELECT * FROM `command_delete` WHERE server={0}'.format(ctx.message.server.id)
		sql = sql.format(ctx.message.server.id)
		result = self.cursor.execute(sql).fetchall()
		if result:
			sql = 'DELETE FROM `command_delete` WHERE server={0}'
			sql = sql.format(ctx.message.server.id)
			self.cursor.execute(sql)
			self.cursor.commit()
			await self.bot.say(':negative_squared_cross_mark: Disabled on Command Delete Messages.')
		else:
			sql = 'INSERT INTO `command_delete` (`server`) VALUES (%s)'
			self.cursor.execute(sql, (ctx.message.server.id))
			self.cursor.commit()
			await self.bot.say(':white_check_mark: Enabled on Command Delete Messages.')

	async def is_ignored(self, message, **kwargs):
		ids = []
		if message is None:
			user = kwargs.pop('u')
			server = kwargs.pop('server')
		else:
			user = message.author
			server = message.server
		if kwargs.get('avatar', False):
			o = 'avatar_ignore'
			g_sql = 'SELECT user FROM `global_log_ignore` WHERE user={0} AND avatar'
		elif kwargs.get('user', False):
			o = 'ignore_users'
			g_sql = 'SELECT user FROM `global_log_ignore` WHERE user={0} AND NOT avatar'
		g_sql = g_sql.format(user.id)
		result = self.cursor.execute(g_sql).fetchall()
		if result:
			return True
		elif kwargs.get('global_only', False):
			return False
		sql = 'SELECT {0} FROM `logs` WHERE server={1}'
		sql = sql.format(o, server.id)
		result = self.cursor.execute(sql).fetchall()
		if not result:
			return False
		elif not result[0][o]:
			return False
		ids.extend([*result[0][o].split(', ')])
		return user.id in ids

	# Deleted command messages
	async def on_command_message_delete(self, message):
		await self.bot.wait_until_ready()
		if message.channel.is_private:
			return
		check = await self.is_ignored(message, user=True)
		if check:
			return
		await asyncio.sleep(3)
		if message not in self.bot.command_messages.copy().keys():
			return
		if message in self.bot.pruned_messages:
			return
		if message.timestamp < datetime.datetime.now()-datetime.timedelta(minutes=20):
			return
		sql = 'SELECT * FROM `command_delete` WHERE server={0}'
		sql = sql.format(message.server.id)
		result = self.cursor.execute(sql).fetchall()
		if len(result) == 0:
			return
		spam_sent = self.bot.globals.command_deleted_sent
		utc = int(time.time())
		if message.server in spam_sent:
			sent_time = spam_sent[message.server]
			sent_sec = int(sent_time) - int(utc)
			if utc >= sent_time or sent_sec == 0:
				del spam_sent[message.server]
			else:
				return
		spam_sent[message.server] = utc+5
		command, prefix = self.bot.command_messages[message]
		await self.bot.send_message(message.channel, ':warning: `{0}` **deleted command message**: {1}'.format(message.author, prefix+command))

	async def on_message(self, message):
		try:
			if message.author == self.bot.user:
				return
			if message.channel.is_private:
				return
			check = await self.is_ignored(message, user=True)
			if check:
				return
			s = False
			if len(message.attachments) != 0:
				sql = "SELECT server,channel FROM `logs` WHERE server={0}"
				sql = sql.format(message.server.id)
				result = self.cursor.execute(sql).fetchall()
				if len(result) != 0:
					channel = str(result[0]['channel'])
					server = str(result[0]['server'])
					for attachment in message.attachments:
						b = await self.bytes_download(attachment['url'])
						filename = attachment['filename']
						if message in self.attachment_cache:
							self.attachment_cache[message] += [b, filename]
						else:
							self.attachment_cache[message] = [[b, filename]]
			s = True
			sql = "SELECT * FROM `tracking` WHERE server={0}"
			sql = sql.format(message.server.id)
			result = self.cursor.execute(sql).fetchall()
			if len(result) == 0:
				return
			for s in result:
				if str(s['server']) != message.server.id:
					return
				if str(s['channel']) == message.channel.id:
					return
				for x in message.content.lower().split():
					if s['txt'].lower() == x:
						msg = '`[{0}]` \"{1}\" was said **{2}** times in {3} by {4}'.format(time.strftime("%I:%M:%S %p"), s['txt'], str(message.content.lower().count(s['txt'].lower())), message.channel.mention, message.author)
						await self.bot.send_message(discord.Object(id=str(s['channel'])), msg)
		except (discord.errors.Forbidden, discord.errors.NotFound, discord.errors.InvalidArgument):
			if s:
				self.remove_server_tracking(message.server)

	async def on_command(self, command, ctx):
		try:
			if ctx.message.channel.is_private:
				return
			check = await self.is_ignored(ctx.message, user=True)
			if check:
				return
			sql = "SELECT server,channel FROM `logs` WHERE server={0}"
			sql = sql.format(ctx.message.server.id)
			result = self.cursor.execute(sql).fetchall()
			if len(result) == 0:
				return
			channel = str(result[0]['channel'])
			server = str(result[0]['server'])
			if ctx.message.server.id != server:
				return
			if len(ctx.message.mentions):
				for s in ctx.message.mentions:
					ctx.message.content = ctx.message.content.replace(s.mention, '@'+s.name).replace('<@!{0}>'.format(s.id), '@'+s.name)
			msg = "User: {0} <{1}>\n".format(ctx.message.author, ctx.message.author.id).replace("'", "")
			msg += "Command: {0}\n".format(ctx.invoked_with)
			msg2 = "`Channel:` {0}\n".format(ctx.message.channel.mention)
			msg2 += "`Context Message:` \"{0}\"".format(ctx.message.content)
			target = discord.Object(id=channel)
			await self.truncate(target, "`[{0}]` :exclamation: **Command Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg)+msg2)
		except (discord.errors.Forbidden, discord.errors.NotFound, discord.errors.InvalidArgument):
			self.remove_server(ctx.message.server)

	async def on_message_delete(self, message):
		try:
			if message.channel.is_private:
				return
			if message.author == self.bot.user:
				return
			check = await self.is_ignored(message, user=True)
			if check:
				return
			if message in self.bot.pruned_messages:
				return
			off_check = "SELECT id FROM `muted` WHERE server={0} AND id={1}"
			off_check = off_check.format(message.server.id, message.author.id)
			off_results = self.cursor.execute(off_check).fetchall()
			if len(off_results) != 0:
				return
			sql = "SELECT server,channel FROM `logs` WHERE server={0}"
			sql = sql.format(message.server.id)
			result = self.cursor.execute(sql).fetchall()
			if len(result) == 0:
				return
			channel = str(result[0]['channel'])
			server = str(result[0]['server'])
			if message.server.id != server:
				return
			if message.channel.id == channel:
				return
			message.content = message.content
			for s in message.mentions:
				message.content = message.content.replace(s.mention, '@'+s.name).replace('<@!{0}>'.format(s.id), '@'+s.name)
			msg = "User: {0} <{1}>\n".format(message.author, message.author.id).replace("'", "")
			msg2 = "Channel: {0}\n".format(message.channel.mention)
			msg2 += "`Deleted Message:` \"{0}\"".format(message.content)
			target = discord.Object(id=channel)
			final = "`[{0}]` :wastebasket: **Message Delete Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg)+msg2
			if len(message.attachments) != 0:
				first = True
				if message in self.attachment_cache:
					for attachment in self.attachment_cache[message]:
						index = self.attachment_cache[message].index(attachment)
						attachment = self.attachment_cache[message][index][0]
						filename = self.attachment_cache[message][index][1]
						if first:
							await self.bot.send_file(target, attachment, filename=filename, content=final)
							first = False
						else:
							await self.bot.send_file(target, attachment, filename=filename)
					del self.attachment_cache[message]
				else:
					await self.truncate(target, final)
			await self.truncate(target, final)
		except (discord.errors.Forbidden, discord.errors.NotFound, discord.errors.InvalidArgument):
			self.remove_server(message.server)

	async def on_message_edit(self, before, after):
		try:
			if before.channel.is_private:
				return
			check = await self.is_ignored(before, user=True)
			if check:
				return
			if before.content == after.content:
				return
			if before.author == self.bot.user:
				return
			sql = "SELECT server,channel FROM `logs` WHERE server={0}"
			sql = sql.format(before.server.id)
			result = self.cursor.execute(sql).fetchall()
			if len(result) == 0:
				return
			channel = str(result[0]['channel'])
			server = str(result[0]['server'])
			if before.server.id != server:
				return
			if before.channel.id == channel:
				return
			before.content = before.content
			after.content = after.content
			for s in before.mentions:
				before.content = before.content.replace(s.mention, s.name)
			for s in after.mentions:
				after.content = after.content.replace(s.mention, s.name)
			msg = "User: {0} <{1}>\n".format(after.author.name, after.author.id).replace("'", "")
			msg2 = "Channel: {0}\n".format(after.channel.mention)
			msg2 += "`Before:` \"{0}\"\n".format(before.content)
			msg2 += "`After:` \"{0}\"".format(after.content)
			target = discord.Object(id=channel)
			await self.truncate(target, "`[{0}]` :pencil2: **Message Edit Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg)+msg2)
		except (discord.errors.Forbidden, discord.errors.NotFound, discord.errors.InvalidArgument):
			self.remove_server(after.server)

	async def on_channel_delete(self, channel):
		try:
			sql = "SELECT server,channel FROM `logs` WHERE server={0}"
			sql = sql.format(channel.server.id)
			result = self.cursor.execute(sql).fetchall()
			if len(result) == 0:
				return
			chan = str(result[0]['channel'])
			if channel.id == chan:
				remove_sql = "DELETE FROM `logs` WHERE server={0}"
				remove_sql = remove_sql.format(channel.server.id)
				self.cursor.execute(remove_sql)
				self.cursor.commit()
				return
			server = str(result[0]['server'])
			if channel.server.id != server:
				return
			a = channel.server
			msg = "{0} Channel: {1} <{2}>\n".format("Voice" if channel.type == discord.ChannelType.voice else "Text", channel.name, channel.id).replace("'", "")
			target = discord.Object(id=chan)
			await self.bot.send_message(target, "`[{0}]` :x: **Channel Delete Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
		except (discord.errors.Forbidden, discord.errors.NotFound, discord.errors.InvalidArgument):
			self.remove_server(channel.server)

	async def on_channel_create(self, channel):
		try:
			if channel.is_private:
				return
			sql = "SELECT server,channel FROM `logs` WHERE server={0}"
			sql = sql.format(channel.server.id)
			result = self.cursor.execute(sql).fetchall()
			if len(result) == 0:
				return
			chan = str(result[0]['channel'])
			server = str(result[0]['server'])
			if channel.server.id != server:
				return
			msg = "{0} Channel: {1} <{2}>\n".format("Voice" if channel.type == discord.ChannelType.voice else "Text", channel.name, channel.id).replace("'", "")
			target = discord.Object(id=chan)
			await self.bot.send_message(target, "`[{0}]` :white_check_mark: **Channel Create Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
		except (discord.errors.Forbidden, discord.errors.NotFound, discord.errors.InvalidArgument):
			self.remove_server(channel.server)

	async def on_channel_update(self, before, after):
		try:
			sql = "SELECT server,channel FROM `logs` WHERE server={0}"
			sql = sql.format(before.server.id)
			result = self.cursor.execute(sql).fetchall()
			if len(result) == 0:
				return
			channel = str(result[0]['channel'])
			server = str(result[0]['server'])
			if before.server.id != server:
				return
			msg = ""
			if before.name != after.name:
				msg += "Name After: {0}\n".format(after.name)
			if before.is_private == False:
				if after.is_private == True:
					msg += "Channel Private: Changed from False to True\n"
			else:
				if after.is_private == False:
					msg += "Channel Is_Private: Changed from True to False\n"
			if before.topic != after.topic:
				msg += "Channel Topic Before: {0}\n".format(before.topic)
				msg += "Channel Topic After: {0}\n".format(after.topic)
			if before.position != after.position:
				msg += "Channel Position Before: {0}\n".format(str(before.position))
				msg += "Channel Position After: {0}\n".format(str(after.position))
			if before.bitrate != after.bitrate:
				msg += "Channel Bitrate Before: {0}\n".format(str(before.bitrate))
				msg += "Channel Bitrate After: {0}\n".format(str(after.bitrate))
			target = discord.Object(id=channel)
			if msg:
				await self.bot.send_message(target, "`[{0}]` :warning: **Channel Edit Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format("Channel Edited: {0} <{1}>\n".format(before.name, before.id).replace("'", "")+"Channel Type: {0}\n".format(str(after.type))+msg))
		except (discord.errors.Forbidden, discord.errors.NotFound, discord.errors.InvalidArgument):
			self.remove_server(after.server)

	async def on_member_join(self, member):
		try:
			if member == self.bot.user:
				return
			check = await self.is_ignored(None, user=True, global_only=True, u=member, server=member.server)
			if check:
				return
			sql = "SELECT server,channel FROM `logs` WHERE server={0}"
			sql = sql.format(member.server.id)
			result = self.cursor.execute(sql).fetchall()
			if len(result) == 0:
				return
			channel = str(result[0]['channel'])
			server = str(result[0]['server'])
			if member.server.id != server:
				return
			a = member.server
			msg = "Member Joined: {0.name} <{0.id}>\n".format(member)
			msg += "Server: {0.name} <{0.id}>\n".format(a).replace("'", "")
			target = discord.Object(id=channel)
			await self.bot.send_message(target, "`[{0}]` :inbox_tray: **Member Join Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
		except (discord.errors.Forbidden, discord.errors.NotFound, discord.errors.InvalidArgument):
			self.remove_server(member.server)

	async def on_member_remove(self, member):
		try:
			if member == self.bot.user:
				return
			check = await self.is_ignored(None, user=True, global_only=True, u=member, server=member.server)
			if check:
				return
			sql = "SELECT server,channel FROM `logs` WHERE server={0}"
			sql = sql.format(member.server.id)
			result = self.cursor.execute(sql).fetchall()
			if len(result) == 0:
				return
			if member.server.id in self.banned_users:
				if member.id in self.banned_users[member.server.id]:
					return
			channel = str(result[0]['channel'])
			server = str(result[0]['server'])
			if member.server.id != server:
				return
			a = member.server
			msg = "User: {0.name} <{0.id}>\n".format(member)
			target = discord.Object(id=channel)
			await self.bot.send_message(target, "`[{0}]` :outbox_tray: **Member Leave/Kick Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
		except (discord.errors.Forbidden, discord.errors.NotFound, discord.errors.InvalidArgument):
			self.remove_server(member.server)

	async def on_member_ban(self, member):
		try:
			if member == self.bot.user:
				return
			check = await self.is_ignored(None, user=True, global_only=True, u=member, server=member.server)
			if check:
				return
			sql = "SELECT server,channel FROM `logs` WHERE server={0}"
			sql = sql.format(member.server.id)
			result = self.cursor.execute(sql).fetchall()
			if len(result) == 0:
				return
			if member.server.id in self.banned_users:
				self.banned_users[member.server.id] += member.id
			else:
				self.banned_users[member.server.id] = [member.id]
			channel = str(result[0]['channel'])
			server = str(result[0]['server'])
			if member.server.id != server:
				return
			msg = "User: {0} <{0.id}>\n".format(member)
			target = discord.Object(id=channel)
			await self.bot.send_message(target, "`[{0}]` :outbox_tray: **Member Ban Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
		except (discord.errors.Forbidden, discord.errors.NotFound, discord.errors.InvalidArgument):
			self.remove_server(member.server)

	async def on_member_unban(self, server, member):
		try:
			if member == self.bot.user:
				return
			check = await self.is_ignored(None, user=True, global_only=True, u=member, server=server)
			if check:
				return
			sql = "SELECT server,channel FROM `logs` WHERE server={0}"
			sql = sql.format(server.id)
			result = self.cursor.execute(sql).fetchall()
			if len(result) == 0:
				return
			channel = str(result[0]['channel'])
			serverr = str(result[0]['server'])
			if server.id != serverr:
				return
			msg = "Unbanned User: {0} <{0.id}>\n".format(member)
			target = discord.Object(id=channel)
			await self.bot.send_message(target, "`[{0}]` :white_check_mark: **Member Unban Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
		except (discord.errors.Forbidden, discord.errors.NotFound, discord.errors.InvalidArgument):
			self.remove_server(server)

	async def on_member_update(self, before, after):
		try:
			if before == self.bot.user:
				return
			check = await self.is_ignored(None, user=True, server=before.server, u=before)
			if check:
				return
			sql = "SELECT server,channel FROM `logs` WHERE server={0}"
			sql = sql.format(before.server.id)
			result = self.cursor.execute(sql).fetchall()
			if len(result) == 0:
				return
			channel = str(result[0]['channel'])
			server = str(result[0]['server'])
			if before.server.id != server:
				return
			target = discord.Object(id=channel)
			if before.avatar != after.avatar:
				if before.id == '135251434445733888':
					return
				check = await self.is_ignored(None, avatar=True, server=before.server, u=before)
				if not check:
					msg = "User: {0} <{0.id}>\n".format(after)
					try:
						after_avatar = await self.bytes_download(after.avatar_url)
					except ValueError:
						return
					if not after_avatar or sys.getsizeof(after_avatar) == 215:
						return
					if before.avatar is None:
						await self.bot.send_file(target, after_avatar, filename='new_avatar.png', content=":frame_photo: **New Avatar Log**\n"+cool.format(msg))
						return
					try:
						before_avatar = await self.bytes_download(before.avatar_url)
					except ValueError:
						return
					if not before_avatar or sys.getsizeof(before_avatar) == 215:
						return
					list_im = [before_avatar, after_avatar]
					try:
						imgs = [PIL.Image.open(i).convert('RGBA') for i in list_im]
					except OSError:
						return
					min_shape = sorted([(np.sum(i.size), i.size) for i in imgs])[0][1]
					imgs_comb = np.hstack((np.asarray(i.resize(min_shape)) for i in imgs))
					imgs_comb = PIL.Image.fromarray(imgs_comb)
					final = BytesIO()
					imgs_comb.save(final, 'png')
					final.seek(0)
					await self.bot.send_file(target, final, filename='avatar_change.png', content="`[{0}]` :frame_photo: **Avatar Change Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
			if before.name != after.name:
				msg = "User Name Before: {0.name} <{0.id}>\n".format(before)
				msg += "User Name After: {0.name}\n".format(after)
				await self.bot.send_message(target, "`[{0}]` :name_badge: **Name Change Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
			if before.nick != None:
				if before.nick != after.nick:
					msg = "User: {0.name} <{0.id}>\n".format(after)
					msg += "Nickname Before: {0}\n".format(before.nick)
					if after.nick is None:
						msg += "Nickname After: Reverted to Username\n"
					else:
						msg += "Nickname After: {0}\n".format(after.nick)
					await self.bot.send_message(target, "`[{0}]` :warning: **Nickname Change Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
			elif after.nick != None:
				msg = "User: {0.name} <{0.id}>\n".format(after)
				msg += "Nickname: {0}\n".format(after.nick)
				await self.bot.send_message(target, "`[{0}]` :warning: **Nickname Create Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
			if before.roles != after.roles:
				msg = "User: {0.name} <{0.id}>\n".format(after)
				r_b = set(before.roles)
				r_a = set(after.roles)
				roles_added = r_a - r_b
				roles_removed = r_b - r_a
				first_1 = False
				for role in roles_added:
					if not first_1:
						msg += "Role{0} Added: ".format('(s)' if len(roles_removed) > 1 else '')
						first_1 = True
					msg += str(role)
				first_2 = False
				for role in roles_removed:
					if not first_2:
						msg += "\nRole{0} Removed: ".format('(s)' if len(roles_removed) > 1 else '') if first_1 else "Role{0} Removed: ".format('(s)' if len(roles_removed) > 1 else '')
						first_2 = True
					msg += str(role)
				await self.bot.send_message(target, "`[{0}]` :bangbang: **Roles Change Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
		except (discord.errors.Forbidden, discord.errors.NotFound, discord.errors.InvalidArgument):
			self.remove_server(after.server)

	async def on_server_update(self, before, after):
		try:
			sql = "SELECT server,channel FROM `logs` WHERE server={0}"
			sql = sql.format(before.id)
			result = self.cursor.execute(sql).fetchall()
			if len(result) == 0:
				return
			channel = str(result[0]['channel'])
			server = str(result[0]['server'])
			if before.id != server:
				return
			target = discord.Object(id=channel)
			if before.icon != after.icon:
				msg = "Server: {0.name} <{0.id}>\n".format(after)
				try:
					after_icon = await self.bytes_download(after.icon_url)
				except ValueError:
					return
				if not after_icon or sys.getsizeof(after_icon) == 215:
					return
				if before.icon is None:
					await self.bot.send_file(target, after_icon, filename='new_server_icon.png', content="`[{0}]` :frame_photo: **New Server Icon Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
					return
				try:
					before_icon = await self.bytes_download(before.icon_url)
				except ValueError:
					return
				if not before_icon or sys.getsizeof(before_icon) == 215:
					return
				list_im = [before_icon, after_icon]
				imgs    = [PIL.Image.open(i).convert('RGBA') for i in list_im]
				min_shape = sorted([(np.sum(i.size), i.size) for i in imgs])[0][1]
				imgs_comb = np.hstack((np.asarray( i.resize(min_shape)) for i in imgs))
				imgs_comb = PIL.Image.fromarray(imgs_comb)
				final = BytesIO()
				imgs_comb.save(final, 'png')
				final.seek(0)
				await self.bot.send_file(target, final, filename='server_icon_change.png', content="`[{0}]` :frame_photo: **Server Icon Change Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
				await asyncio.sleep(2)
			if before.name != after.name:
				msg = "Server Name Before: {0}\n".format(before.name)
				msg += "Server Name After: {0}\n".format(after.name)
				await self.bot.send_message(target, "`[{0}]` :name_badge: **Server Name Change Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
			if before.region != after.region:
				msg = "Server Region Before: {0}\n".format(str(before.region))
				msg += "Server Region After: {0}\n".format(str(after.region))
				await self.bot.send_message(target, "`[{0}]` :globe_with_meridians: **Server Region Change Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
		except (discord.errors.Forbidden, discord.errors.NotFound, discord.errors.InvalidArgument):
			self.remove_server(after)

	async def on_server_role_create(self, role):
		try:
			sql = "SELECT server,channel FROM `logs` WHERE server={0}"
			sql = sql.format(role.server.id)
			result = self.cursor.execute(sql).fetchall()
			if len(result) == 0:
				return
			channel = str(result[0]['channel'])
			server = str(result[0]['server'])
			if role.server.id != server:
				return
			target = discord.Object(id=channel)
			msg = "Server Role Created: {0}\n".format(role.name)
			await self.bot.send_message(target, "`[{0}]` :bangbang: **Server Roles Create Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
		except (discord.errors.Forbidden, discord.errors.NotFound, discord.errors.InvalidArgument):
			self.remove_server(role.server)

	async def on_server_role_delete(self, role):
		try:
			sql = "SELECT server,channel FROM `logs` WHERE server={0}"
			sql = sql.format(role.server.id)
			result = self.cursor.execute(sql).fetchall()
			if len(result) == 0:
				return
			channel = str(result[0]['channel'])
			server = str(result[0]['server'])
			if role.server.id != server:
				return
			target = discord.Object(id=channel)
			r_b = ', '.join(map(str, role.server.roles))
			msg = "Server Role Deleted: {0}\n".format(role.name)
			await self.bot.send_message(target, "`[{0}]` :bangbang: **Server Roles Delete Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
		except (discord.errors.Forbidden, discord.errors.NotFound, discord.errors.InvalidArgument):
			self.remove_server(role.server)

	async def on_server_role_update(self, before, after):
		try:
			sql = "SELECT server,channel FROM `logs` WHERE server={0}"
			sql = sql.format(before.server.id)
			result = self.cursor.execute(sql).fetchall()
			if len(result) == 0:
				return
			channel = str(result[0]['channel'])
			server = str(result[0]['server'])
			if before.server.id != server:
				return
			target = discord.Object(id=channel)
			msg = "Role: {0} <{1}>\n".format(before.name, before.id)
			if before.name != after.name:
				msg += "Role Name Before: {0}\n".format(before.name)
				msg += "Role Name After: {0}\n".format(after.name)
			if before.color != after.color:
				if before.color != None:
					msg += "Role Color Before: {0}\n".format(before.color)
					msg += "Role Color After: {0}\n".format(after.color)
				else:
					msg += "New Role Color: {0}\n".format(after.color)
			if before.mentionable != after.mentionable:
				msg += "Role Mentionable: {0}\n".format('True' if after.mentionable else 'False')
			if before.hoist != after.hoist:
				msg += "Role Shown Sepperatly: {0}\n".format('True' if after.hoist else 'False')
			if before.position != after.position:
				msg += "Role Position Before: {0}\n".format(before.position)
				msg += "Role Position After: {0}\n".format(after.position)
			if before.permissions != after.permissions:
				msg += "Permissions Changed:\n"
				p1 = before.permissions
				p2 = after.permissions
				if p1.administrator != p2.administrator:
					msg += '--Administrator--\nFrom {0} to {1}\n'.format(p1.administrator, p2.administrator)
				if p1.manage_server != p2.manage_server:
					msg += '--Manage Server--\nFrom {0} to {1}\n'.format(p1.manage_server, p2.manage_server)
				if p1.manage_roles != p2.manage_roles:
					msg += '--Manage Roles--\nFrom {0} to {1}\n'.format(p1.manage_roles, p2.manage_roles)
				if p1.manage_channels != p2.manage_channels:
					msg += '--Manage Channels--\nFrom {0} to {1}\n'.format(p1.manage_channels, p2.manage_channels)
				if p1.manage_messages != p2.manage_messages:
					msg += '--Manage Messages--\nFrom {0} to {1}\n'.format(p1.manage_messages, p2.manage_messages)
				if p1.manage_nicknames != p2.manage_nicknames:
					msg += '--Manage Nicknames--\nFrom {0} to {1}\n'.format(p1.manage_nicknames, p2.manage_nicknames)
				if p1.kick_members != p2.kick_members:
					msg += '--Kick Members--\nFrom {0} to {1}\n'.format(p1.kick_members, p2.kick_members)
				if p1.ban_members != p2.ban_members:
					msg += '--Ban Members--\nFrom {0} to {1}\n'.format(p1.ban_members, p2.ban_members)
				if p1.kick_members != p2.kick_members:
					msg += '--Kick Members--\nFrom {0} to {1}\n'.format(p1.kick_members, p2.kick_members)
				if p1.change_nickname != p2.change_nickname:
					msg += '--Change Nickname--\nFrom {0} to {1}\n'.format(p1.change_nickname, p2.change_nickname)
				if p1.attach_files != p2.attach_files:
					msg += '--Attach Files--\nFrom {0} to {1}\n'.format(p1.attach_files, p2.attach_files)
				if p1.deafen_members != p2.deafen_members:
					msg += '--Deafen Members--\nFrom {0} to {1}\n'.format(p1.deafen_members, p2.deafen_members)
				if p1.embed_links != p2.embed_links:
					msg += '--Embed Links--\nFrom {0} to {1}\n'.format(p1.embed_links, p2.embed_links)
				if p1.external_emojis != p2.external_emojis:
					msg += '--Use External Emojis--\nFrom {0} to {1}\n'.format(p1.external_emojis, p2.external_emojis)
				if p1.connect != p2.connect:
					msg += '--Connect to Voice Channels--\nFrom {0} to {1}\n'.format(p1.connect, p2.connect)
				if p1.create_instant_invite != p2.create_instant_invite:
					msg += '--Create Invites--\nFrom {0} to {1}\n'.format(p1.create_instant_invite, p2.create_instant_invite)
				if p1.manage_emojis != p2.manage_emojis:
					msg += '--Manage Emojis--\nFrom {0} to {1}\n'.format(p1.manage_emojis, p2.manage_emojis)
				if p1.manage_webhooks != p2.manage_webhooks:
					msg += '--Manage Webhooks--\nFrom {0} to {1}\n'.format(p1.manage_webhooks, p2.manage_webhooks)
				if p1.mention_everyone != p2.mention_everyone:
					msg += '--Mention Everyone--\nFrom {0} to {1}\n'.format(p1.mention_everyone, p2.mention_everyone)
				if p1.move_members != p2.move_members:
					msg += '--Move Members in Voice Channels--\nFrom {0} to {1}\n'.format(p1.move_members, p2.move_members)
				if p1.mute_members != p2.mute_members:
					msg += '--Mute Members Voice--\nFrom {0} to {1}\n'.format(p1.mute_members, p2.mute_members)
				if p1.read_message_history != p2.read_message_history:
					msg += '--Read Message History--\nFrom {0} to {1}\n'.format(p1.read_message_history, p2.read_message_history)
				if p1.read_messages != p2.read_messages:
					msg += '--Read Messages--\nFrom {0} to {1}\n'.format(p1.read_messages, p2.read_messages)
				if p1.send_messages != p2.send_messages:
					msg += '--Send Messages--\nFrom {0} to {1}\n'.format(p1.send_messages, p2.send_messages)
				if p1.send_tts_messages != p2.send_tts_messages:
					msg += '--Send TTS Messages--\nFrom {0} to {1}\n'.format(p1.send_tts_messages, p2.send_tts_messages)
				if p1.speak != p2.speak:
					msg += '--Speak in Voice Channels--\nFrom {0} to {1}\n'.format(p1.speak, p2.speak)
				if p1.use_voice_activation != p2.use_voice_activation:
					msg += '--Use Voice Activation--\nFrom {0} to {1}\n'.format(p1.use_voice_activation, p2.use_voice_activation)
			await self.bot.send_message(target, "`[{0}]` :bangbang: **Roles Change Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
		except (discord.errors.Forbidden, discord.errors.NotFound, discord.errors.InvalidArgument):
			self.remove_server(after.server)

	async def on_voice_state_update(self, before, after):
		try:
			check = await self.is_ignored(None, user=True, u=before, server=before.server)
			if check:
				return
			sql = "SELECT server,channel FROM `logs` WHERE server={0}"
			sql = sql.format(before.server.id)
			result = self.cursor.execute(sql).fetchall()
			if len(result) == 0:
				return
			channel = str(result[0]['channel'])
			server = str(result[0]['server'])
			if before.server.id != server:
				return
			target = discord.Object(id=channel)
			msg = ""
			if before.self_mute != after.self_mute:
				return
			if before.self_deaf != after.self_deaf:
				return
			if before.voice_channel != after.voice_channel:
				msg += "User: {0} <{0.id}>\n".format(before)
				if not before.voice_channel:
					msg += "Voice Channel Join: {0.name} <{0.id}>".format(after.voice_channel)
				elif before.voice_channel and after.voice_channel:
					msg += "Voice Channel Before: {0.name} <{0.id}>\n".format(before.voice_channel)
					msg += "Voice Channel After: {0.name} <{0.id}>".format(after.voice_channel)
				elif before.voice_channel and not after.voice_channel:
					msg += "Voice Channel Leave: {0.name} <{0.id}>".format(before.voice_channel)
			if before.mute != after.mute:
				if not before.mute:
					msg += "Server Muted: {0} <{0.id}>".format(after)
				else:
					msg += "Server Un-Muted: {0} <{0.id}>".format(after)
			if before.deaf != after.deaf:
				if after.deaf:
					msg += "Server Deafened: {0} <{0.id}>".format(after)
				else:
					msg += "Server Un-Deafened: {0} <{0.id}>".format(after)
			if msg:
				await self.bot.send_message(target, "`[{0}]` :bangbang: **Voice Channel Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
		except (discord.errors.Forbidden, discord.errors.NotFound, discord.errors.InvalidArgument):
			self.remove_server(after.server)

def setup(bot):
	mod = Logs(bot)
	bot.add_cog(mod)
	bot.add_listener(mod.on_command_message_delete, 'on_message_delete')
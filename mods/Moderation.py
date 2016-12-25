import asyncio, discord, aiohttp
import re, io, random, datetime
from discord.ext import commands
from utils import checks
from mods.cog import Cog

code = "```py\n{0}\n```"

class Moderation(Cog):
	def __init__(self, bot):
		super().__init__(bot)
		self.cursor = bot.mysql.cursor
		self.discord_path = bot.path.discord
		self.files_path = bot.path.files
		self.nick_massing = []
		self.nick_unmassing = []

	@commands.command(pass_context=True)
	@commands.cooldown(2, 5, commands.BucketType.server)
	@checks.mod_or_perm(manage_messages=True)
	async def clean(self, ctx, max_messages:int=None):
		"""Removes inputed amount of bot and invoker messages."""
		none = False
		if max_messages is None:
			none = True
			max_messages = 20
		if max_messages and max_messages > 1500:
			await self.bot.say("2 many messages (<= 1500)")
			return
		if ctx.message.server.me.permissions_in(ctx.message.channel).manage_messages:
			prefix = await self.bot.funcs.get_prefix(ctx.message)
			prefix = prefix[0][0]
			check = lambda m: m.author == self.bot.user or m.content.startswith(prefix)
			deleted = await self.bot.purge_from(ctx.message.channel, limit=max_messages, check=check, after=datetime.datetime.now() - datetime.timedelta(minutes=5) if none else None)
			self.bot.pruned_messages.append(deleted)
			count = len(deleted)
		else:
			count = 0
			async for message in self.bot.logs_from(ctx.message.channel, limit=max_messages+1, after=datetime.datetime.now() - datetime.timedelta(minutes=5) if none else None):
				if message.author == self.bot.user:
					self.bot.pruned_messages.append(message)
					asyncio.ensure_future(self.bot.delete_message(message))
					await asyncio.sleep(0.21)
					count += 1
		x = await self.bot.send_message(ctx.message.channel, "Removed `{0}` messages out of `{1}` searched messages".format(count, max_messages))
		await asyncio.sleep(10)
		try:
			self.bot.pruned_messages.append(ctx.message)
			await self.bot.delete_message(ctx.message)
		except:
			pass
		await self.bot.delete_message(x)

	@commands.group(pass_context=True, invoke_without_command=True, aliases=['purge', 'deletemessages'], no_pm=True)
	@commands.cooldown(2, 5, commands.BucketType.server)
	@checks.mod_or_perm(manage_messages=True)
	async def prune(self, ctx, *, max_messages:str=None):
		"""Delete inputed amount of messages in a channel."""
		if ctx.message.server.me.permissions_in(ctx.message.channel).manage_messages == False:
			await self.bot.say("Sorry, this doesn't work on this server (No manage_messages Permission)!")
			return
		users = []
		none = False
		if max_messages:
			for u in ctx.message.mentions:
				users.append(u)
				max_messages = max_messages.replace(u.mention, '')
			if max_messages.replace(' ', '').isdigit():
				max_messages = int(max_messages)
		if max_messages is None:
			none = True
			max_messages = 100
		try:
			max_messages = int(max_messages)
		except:
			max_messages = 100
		if max_messages > 6000:
			await self.bot.say("2 many messages (<= 6000)")
			return
		check = lambda m: m.author in users
		deleted = await self.bot.purge_from(ctx.message.channel, limit=max_messages, before=ctx.message, after=datetime.datetime.now() - datetime.timedelta(minutes=5) if none else None, check=check if users else None)
		self.bot.pruned_messages.append(deleted)
		if users and len(deleted) == 0:
			x = await self.bot.send_message(ctx.message.channel, ":warning: No messages found by `{0}` within `{1}` searched messages!".format(', '.join(users), max_messages))
		else:
			x = await self.bot.send_message(ctx.message.channel, "ok, removed **{0}** messages.".format(len(deleted)))
		await asyncio.sleep(10)
		try:
			self.bot.pruned_messages.append(ctx.message)
			await self.bot.delete_message(ctx.message)
		except:
			pass
		try:
			await self.bot.delete_message(x)
		except:
			pass

	@prune.command(name='bots', pass_context=True, no_pm=True)
	@commands.cooldown(2, 5, commands.BucketType.server)
	async def prune_bots(self, ctx, max_messages:int=50):
		if max_messages > 5000:
			await self.bot.say("2 many messages (<= 5000)")
			return
		deleted = await self.bot.purge_from(ctx.message.channel, limit=max_messages, before=ctx.message, check=lambda m: m.author.bot)
		users = set([str(u.author) for u in deleted])
		if len(deleted) == 0:
			x = await self.bot.send_message(ctx.message.channel, ":warning: No messages found by bots within `{0}` searched messages!".format(max_messages))
		else:
			self.bot.pruned_messages.append(deleted)
			x = await self.bot.send_message(ctx.message.channel, 'ok, removed `{0}` messages by bot{2} `{1}`.'.format(len(deleted), ', '.join(users), 's' if len(users) > 1 else ''))
		await asyncio.sleep(10)
		try:
			self.bot.pruned_messages.append(ctx.message)
			await self.bot.delete_message(ctx.message)
		except:
			pass
		try:
			await self.bot.delete_message(x)
		except:
			pass

	@prune.command(name='attachments', aliases=['files'], pass_context=True, no_pm=True)
	@commands.cooldown(2, 5, commands.BucketType.server)
	async def prune_attachments(self, ctx, max_messages:int=50):
		if max_messages > 5000:
			await self.bot.say("2 many messages (<= 5000)")
			return
		deleted = await self.bot.purge_from(ctx.message.channel, limit=max_messages, before=ctx.message, check=lambda m: len(m.attachments))
		users = set([str(u.author) for u in deleted])
		if len(deleted) == 0:
			x = await self.bot.send_message(ctx.message.channel, ":warning: No messages found with attachments within `{0}` searched messages!".format(max_messages))
		else:
			self.bot.pruned_messages.append(deleted)
			x = await self.bot.send_message(ctx.message.channel, 'ok, removed `{0}` messages with attachments by `{1}`.'.format(len(deleted), ', '.join(users)))
		await asyncio.sleep(10)
		try:
			self.bot.pruned_messages.append(ctx.message)
			await self.bot.delete_message(ctx.message)
		except:
			pass
		try:
			await self.bot.delete_message(x)
		except:
			pass

	@prune.command(name='embeds', pass_context=True, no_pm=True)
	@commands.cooldown(2, 5, commands.BucketType.server)
	async def prune_embeds(self, ctx, max_messages:int=50):
		if max_messages > 5000:
			await self.bot.say("2 many messages (<= 5000)")
			return
		deleted = await self.bot.purge_from(ctx.message.channel, limit=max_messages, before=ctx.message, check=lambda m: len(m.embeds))
		users = set([str(u.author) for u in deleted])
		if len(deleted) == 0:
			x = await self.bot.send_message(ctx.message.channel, ":warning: No messages found with embeds within `{0}` searched messages!".format(max_messages))
		else:
			self.bot.pruned_messages.append(deleted)
			x = await self.bot.send_message(ctx.message.channel, 'ok, removed `{0}` messages with embeds by `{1}`.'.format(len(deleted), ', '.join(users)))
		await asyncio.sleep(10)
		try:
			self.bot.pruned_messages.append(ctx.message)
			await self.bot.delete_message(ctx.message)
		except:
			pass
		try:
			await self.bot.delete_message(x)
		except:
			pass

	@prune.command(name='images', pass_context=True, no_pm=True)
	@commands.cooldown(2, 5, commands.BucketType.server)
	async def prune_images(self, ctx, max_messages:int=50):
		if max_messages > 5000:
			await self.bot.say("2 many messages (<= 5000)")
			return
		deleted = await self.bot.purge_from(ctx.message.channel, limit=max_messages, before=ctx.message, check=lambda m: len(m.attachments) or len(m.embeds))
		users = set([str(u.author) for u in deleted])
		if len(deleted) == 0:
			x = await self.bot.send_message(ctx.message.channel, ":warning: No messages found with images within `{0}` searched messages!".format(max_messages))
		else:
			self.bot.pruned_messages.append(deleted)
			x = await self.bot.send_message(ctx.message.channel, 'ok, removed `{0}` messages with images by `{1}`.'.format(len(deleted), ', '.join(users)))
		await asyncio.sleep(10)
		try:
			self.bot.pruned_messages.append(ctx.message)
			await self.bot.delete_message(ctx.message)
		except:
			pass
		try:
			await self.bot.delete_message(x)
		except:
			pass

	@prune.command(name='with', aliases=['contains', 'content'], pass_context=True, no_pm=True)
	@commands.cooldown(2, 5, commands.BucketType.server)
	async def prune_with(self, ctx, *, max_messages:str=None):
		txt = max_messages
		if max_messages:
			for s in max_messages.split():
				if s.isdigit():
					max_messages = int(s)
					txt = txt.replace(str(max_messages), '')
					break
		if max_messages is None:
			max_messages = 50
			if txt is None:
				await self.bot.say(':no_entry: `Please input a string to search for in messages and delete.`')
				return
		elif max_messages > 5000:
			await self.bot.say("2 many messages (<= 5000)")
			return
		deleted = await self.bot.purge_from(ctx.message.channel, limit=max_messages, before=ctx.message, check=lambda m: txt in m.content)
		users = set([str(u.author) for u in deleted])
		if len(deleted) == 0:
			x = await self.bot.send_message(ctx.message.channel, ":warning: No messages found with given string within `{0}` searched messages!".format(max_messages))
		else:
			self.bot.pruned_messages.append(deleted)
			x = await self.bot.send_message(ctx.message.channel, 'ok, removed `{0}` messages with a string by `{1}`.'.format(len(deleted), ', '.join(users)))
		await asyncio.sleep(10)
		try:
			self.bot.pruned_messages.append(ctx.message)
			await self.bot.delete_message(ctx.message)
		except:
			pass
		try:
			await self.bot.delete_message(x)
		except:
			pass

	@commands.group(pass_context=True, invoke_without_command=True, aliases=['unblacklist', 'ignore'], no_pm=True)
	@checks.admin_or_perm(manage_server=True)
	async def blacklist(self, ctx, user:discord.User=None):
		"""Blacklist/Unblacklist user from server"""
		if user is None:
			await self.bot.say("**Blacklist Base Command**\nCommands:\n`global`: Owner Only\n`user`: Server admin (manage_server) only\n`channel`: Server admin (manage_server) only\n Call once to blacklist, again to unblacklist.")
			return
		if user == ctx.message.author:
			await self.bot.say('lol dumbass')
			return
		elif user.id == self.bot.owner.id:
			await self.bot.say('no')
			return
		sql = 'SELECT * FROM `blacklist` WHERE server={0} AND user={1}'
		sql = sql.format(ctx.message.server.id, user.id)
		result = self.cursor.execute(sql).fetchall()
		if len(result) == 0:
			sql = 'INSERT INTO `blacklist` (`server`, `user`, `admin`) VALUES (%s, %s, %s)'
			self.cursor.execute(sql, (ctx.message.server.id, user.id, ctx.message.author.id))
			await self.bot.say(':white_check_mark: Server blacklisted `{0}` from the bot.'.format(user))
		else:
			sql = 'DELETE FROM `blacklist` WHERE server={0} AND user={1}'
			sql = sql.format(ctx.message.server.id, user.id)
			self.cursor.execute(sql)
			await self.bot.say(':negative_squared_cross_mark: Server unblacklisted `{0}` from the bot.'.format(user))
		self.cursor.commit()

	@blacklist.command(name='global', pass_context=True)
	@checks.is_owner()
	async def blacklist_global(self, ctx, user:discord.User):
		"""Blacklist/Unblacklist user from server"""
		if user.id == self.bot.owner.id:
			await self.bot.say("what are you doing NotSoSuper?")
			return
		sql = 'SELECT * FROM `global_blacklist` WHERE user={0}'
		sql = sql.format(user.id)
		result = self.cursor.execute(sql).fetchall()
		if len(result) == 0:
			sql = 'INSERT INTO `global_blacklist` (`user`) VALUES (%s)'
			self.cursor.execute(sql, (user.id))
			await self.bot.say(':white_check_mark: Global blacklisted `{0}` from the bot.'.format(user))
		else:
			sql = 'DELETE FROM `global_blacklist` WHERE user={0}'
			sql = sql.format(user.id)
			self.cursor.execute(sql)
			await self.bot.say(':negative_squared_cross_mark: Global unblacklisted `{0}` from the bot.'.format(user))
		self.cursor.commit()

	@blacklist.command(name='channel', pass_context=True, no_pm=True)
	@checks.admin_or_perm(manage_server=True)
	async def blacklist_channel(self, ctx, chan:discord.Channel=None):
		"""Blacklists a channel from the bot."""
		if chan is None:
			chan = ctx.message.channel
		sql = 'SELECT * FROM `channel_blacklist` WHERE server={0} AND channel={1}'
		sql = sql.format(ctx.message.server.id, chan.id)
		result = self.cursor.execute(sql).fetchall()
		if len(result) == 0:
			sql = 'INSERT INTO `channel_blacklist` (`server`, `channel`, `admin`) VALUES (%s, %s, %s)'
			self.cursor.execute(sql, (ctx.message.server.id, chan.id, ctx.message.author.id))
			await self.bot.say(":white_check_mark: Blacklisted {0.mention} `<{0.id}>`".format(chan))
		else:
			sql = 'DELETE FROM `channel_blacklist` WHERE server={0} AND channel={1}'
			sql = sql.format(ctx.message.server.id, chan.id)
			self.cursor.execute(sql)
			await self.bot.say(":white_check_mark: Unblacklisted {0.mention} `<{0.id}>`".format(chan))
		self.cursor.commit()

	@blacklist.command(name='list', pass_context=True, no_pm=True)
	async def blacklist_list(self, ctx):
		sql = 'SELECT * FROM `channel_blacklist` WHERE server={0}'
		sql = sql.format(ctx.message.server.id)
		result = self.cursor.execute(sql).fetchall()
		msg = ':white_check_mark: **Blacklisted Users**\n'
		found = False
		if len(result) != 0:
			for s in result:
				channel = ctx.message.server.get_channel(str(s['channel']))
				if channel is None:
					channel = '**Not found on server** ID: `{0}`'.format(s['channel'])
				else:
					channel = channel.mention
				admin = ctx.message.server.get_member(str(s['admin']))
				if admin is None:
					admin = await self.bot.get_user_info(str(s['admin']))
					admin = '`{0}`'.format(admin)
				msg += ':no_entry: Channel: {0} | Admin: {1} | Time: `{2}`\n'.format(channel, admin, s['time'].strftime('%m/%d/%Y %H:%M:%S'))
				found = True
		sql = 'SELECT * FROM `blacklist` WHERE server={0}'
		sql = sql.format(ctx.message.server.id)
		result = self.cursor.execute(sql).fetchall()
		if len(result) == 0 and ctx.message.author.id != self.bot.owner.id:
			await self.bot.say(':no_entry: Server does **not** have any channels or users blacklisted.')
			return
		for s in result:
			discord_user = ctx.message.server.get_member(str(s['user']))
			if discord_user is None:
				discord_user = await self.bot.get_user_info(str(s['user']))
				discord_user = '`{0}`'.format(discord_user)
			admin = ctx.message.server.get_member(str(s['admin']))
			if admin is None:
				admin = await self.bot.get_user_info(str(s['admin']))
				admin = '`{0}`'.format(admin)
			msg += ':no_entry: User: {0} | Admin: {1} | Time: `{2}`\n'.format(discord_user, admin, s['time'].strftime('%m/%d/%Y %H:%M:%S'))
			found = True
		if ctx.message.author.id == self.bot.owner.id:
			sql = 'SELECT * FROM `global_blacklist`'
			result = self.cursor.execute(sql).fetchall()
			if len(result) != 0:
				for s in result:
					discord_user = discord.utils.get(self.bot.get_all_members(), id=str(s['user']))
					if discord_user is None:
						discord_user = await self.bot.get_user_info(str(s['user']))
						discord_user = '`{0}`'.format(discord_user)
					msg += ':globe_with_meridians: **Global Blacklisted** User: {0} | Time: `{1}`\n'.format(discord_user, s['time'].strftime('%m/%d/%Y %H:%M:%S'))
			elif not found:
				msg = ':no_entry: Server does **not** have any channels or users blacklisted.'
		await self.bot.say(msg)

	@commands.group(pass_context=True, invoke_without_command=True, no_pm=True)
	@commands.cooldown(1, 5)
	@checks.mod_or_perm(manage_messages=True)
	async def off(self, ctx, user:discord.User):
		if ctx.message.server.me.permissions_in(ctx.message.channel).manage_messages:
			pass
		else:
			await self.bot.say("Sorry, I do not have the manage_messages permission\n**Aborting**")
			return
		if user == self.bot.user:
			await self.bot.say("u cant turn me off asshole")
			return
		sql_check = "SELECT user FROM `muted` WHERE server={0} AND user={1}"
		sql_check = sql_check.format(ctx.message.server.id, user.id)
		check_result = self.cursor.execute(sql_check).fetchall()
		if len(check_result) == 0:
			pass
		else:
			await self.bot.say("`{0}` is already turned off!".format(user))
			return
		sql = "INSERT INTO `muted` (`server`, `user`) VALUES (%s, %s)"
		self.cursor.execute(sql, (ctx.message.server.id, user.id))
		self.cursor.commit()
		await self.bot.say("ok, tuned off `{0}`".format(user))

	@off.command(name='list', pass_context=True, invoke_without_command=True, no_pm=True)
	@commands.cooldown(1, 5)
	async def off_list(self, ctx):
		sql = 'SELECT * FROM `muted` WHERE server={0}'
		sql = sql.format(ctx.message.server.id)
		result = self.cursor.execute(sql).fetchall()
		if len(result) == 0:
			await self.bot.say(':no_entry: Server does **not** have any users turned off!')
		else:
			msg = ':white_check_mark: Users turned off:\n'
			count = 0
			for s in result:
				count += 1
				user = discord.utils.find(lambda m: m.id == str(s['user']), self.bot.get_all_members())
				if user == None:
					user = await self.bot.get_user_info(str(s['user']))
					user = '`'+str(user)+'`'
				msg += '**{0}.** {1}\n'.format(str(count), user)
			await self.bot.say(msg)

	@commands.group(pass_context=True, invoke_without_command=True, no_pm=True)
	@commands.cooldown(1, 5)
	@checks.mod_or_perm(manage_messages=True)
	async def on(self, ctx, user:discord.User):
		if ctx.message.server.me.permissions_in(ctx.message.channel).manage_messages:
			pass
		else:
			await self.bot.say("Sorry, I do not have the manage_messages permission\n**Aborting**")
			return
		if user == self.bot.user:
			await self.bot.say("thanks for trying to turn me on but u can\'t\nasshole")
			return
		sql_check = "SELECT user FROM `muted` WHERE server={0} AND user={1}"
		sql_check = sql_check.format(ctx.message.server.id, user.id)
		check_result = self.cursor.execute(sql_check).fetchall()
		if len(check_result) == 0:
			await self.bot.say("`{0}` is already turned on!".format(user))
			return
		sql = "DELETE FROM `muted` WHERE server={0} AND user={1}"
		sql = sql.format(ctx.message.server.id, user.id)
		self.cursor.execute(sql)
		self.cursor.commit()
		x = await self.bot.send_message(ctx.message.channel, "ok, turned on `{0}`".format(user))
		try:
			await self.bot.delete_message(ctx.message)
		except:
			pass
		await asyncio.sleep(10)
		await self.bot.delete_message(x)

	@on.command(name='all', pass_context=True, invoke_without_command=True, no_pm=True)
	@checks.mod_or_perm(manage_messages=True)
	async def on_all(self, ctx):
		sql = 'SELECT COUNT(*) FROM `muted` WHERE server={0}'
		sql = sql.format(ctx.message.server.id)
		result = self.cursor.execute(sql).fetchall()
		if result[0]['COUNT(*)'] == 0:
			await self.bot.say(':no_entry: Server does **not** have any users turned off!')
		else:
			sql = 'DELETE FROM `muted` WHERE server={0}'
			sql = sql.format(ctx.message.server.id)
			self.cursor.execute(sql)
			self.cursor.commit()
			await self.bot.say(':white_check_mark: Turned on `{0}` users.'.format(result[0]['COUNT(*)']))

	async def on_message(self, message):
		await self.bot.wait_until_ready()
		if self.bot.self_bot:
			return
		if message.author == self.bot.user:
			return
		if message.channel.is_private or message.channel is None:
			return
		if message.server.me.permissions_in(message.channel).manage_messages == False:
			return
		sql = "SELECT user FROM `muted` WHERE server={0} AND user={1}"
		sql = sql.format(message.server.id, message.author.id)
		result = self.cursor.execute(sql).fetchall()
		if len(result) == 0:
			return
		if str(result[0]['user']) == message.author.id:
			try:
				await self.bot.delete_message(message)
			except:
				pass
		else:
			return

	muted_users = {}
	@commands.command(pass_context=True, no_pm=True)
	@commands.cooldown(1, 20)
	@checks.mod_or_perm(manage_messages=True)
	async def mute(self, ctx, *users:discord.User):
		"""Mute a User"""
		if ctx.message.server.me.permissions_in(ctx.message.channel).manage_channels == False:
			await self.bot.say("Sorry, I do not have the manage_channels permission\n**Aborting**")
			return
		for user in users:
			if ctx.message.author.permissions_in(ctx.message.channel).administrator:
				await self.bot.say(':no_entry: `{0}` cannot be muted.'.format(user))
				continue
			if ctx.message.server in self.muted_users:
				if user in self.muted_users[ctx.message.server]:
					await self.bot.say('`{0}` is already muted!'.format(user))
					continue
			count = 0
			for channel in ctx.message.server.channels:
				perms = user.permissions_in(channel)
				if perms.read_messages == False:
					continue
				overwrite = discord.PermissionOverwrite()
				overwrite.send_messages = False
				try:
					await self.bot.edit_channel_permissions(channel, user, overwrite)
					await asyncio.sleep(0.21)
					count += 1
				except:
					if count == 0:
						await self.bot.say(":no_entry: Bot does not have permission")
						return
					continue
			if ctx.message.server.id not in self.muted_users:
				self.muted_users[ctx.message.server] = [user]
			else:
				self.muted_users[ctx.message.server] += user
			await self.bot.say("ok, muted `{0}`".format(user))

	@commands.command(pass_context=True, no_pm=True)
	@checks.mod_or_perm(manage_messages=True)
	async def unmute(self, ctx, *users:discord.User):
		"""Unmute a User"""
		if ctx.message.server.me.permissions_in(ctx.message.channel).manage_channels == False:
			await self.bot.say("Sorry, I do not have the manage_channels permission\n**Aborting**")
			return
		for user in users:
			try:
				s = user in self.muted_users[ctx.message.server]
				assert s
			except:
				await self.bot.say('`{0}` is not muted!'.format(user))
				return
			count = 0
			for channel in ctx.message.server.channels:
				perms = user.permissions_in(channel)
				if perms.read_messages == False:
					continue
				try:
					await self.bot.delete_channel_permissions(channel, user)
					await asyncio.sleep(0.21)
					count += 1
				except:
					if count == 0:
						await self.bot.say(":no_entry: Bot does not have permission")
						return
					continue
			index = self.muted_users[ctx.message.server].index(user)
			del self.muted_users[ctx.message.server][index]
			await self.bot.say("ok, unmuted `{0}`".format(user))

	@commands.command(pass_context=True, no_pm=True)
	@checks.admin_or_perm(manage_server=True)
	async def createrole(self, ctx, *, role):
		"""Create a role"""
		if ctx.message.server.me.permissions_in(ctx.message.channel).manage_roles == False:
			await self.bot.say("Sorry, I do not have the manage_roles permission\n**Aborting**")
		else:
			await self.bot.create_role(ctx.message.server, name=role)
			await self.bot.say("ok, created the role `{0}`".format(role))

	@commands.command(pass_context=True, no_pm=True)
	@checks.admin_or_perm(manage_server=True)
	async def addrole(self, ctx, role:discord.Role, *users:discord.User):
		"""Add a role to x users"""
		if ctx.message.server.me.permissions_in(ctx.message.channel).manage_roles == False:
			await self.bot.say("Sorry, I do not have the manage_roles permission\n**Aborting**")
			return
		if len(users) == 0:
			await self.bot.say(":no_entry: You need to specify a user to give the role too.")
		idk = []
		for user in users:
			await self.bot.add_roles(user, role)
			idk.append(user.name)
		await self.bot.say("ok, gave {2} `{0}` the role {1}".format(", ".join(idk), role.name, 'user' if len(users) == 1 else 'users'))

	@commands.command(pass_context=True, no_pm=True)
	@checks.admin_or_perm(manage_server=True)
	async def removerole(self, ctx, role:discord.Role, *users:discord.User):
		"""Remove a role from x users"""
		if ctx.message.server.me.permissions_in(ctx.message.channel).manage_roles == False:
			await self.bot.say("Sorry, I do not have the manage_roles permission\n**Aborting**")
			return
		if len(users) == 0:
			await self.bot.say("You need to add a person to remove the role from!")
		idk = []
		for user in users:
			await self.bot.remove_roles(user, role)
			idk.append(user.name)
		await self.bot.say("ok, removed the role {0} from {2} `{1}`".format(role.name, ', '.join(idk), 'user' if len(users) == 1 else 'users'))

	@commands.command(pass_context=True, no_pm=True)
	@checks.admin_or_perm(manage_server=True)
	async def deleterole(self, ctx, *roles:discord.Role):
		"""Delete a role"""
		if ctx.message.server.me.permissions_in(ctx.message.channel).manage_roles == False:
			await self.bot.say("Sorry, I do not have the manage_roles permission\n**Aborting**")
			return
		server = ctx.message.server
		for role in roles:
			await self.bot.delete_role(server,role)
			await self.bot.say("ok, deleted the role `{0}` from the server".format(role.name))

	@commands.command(pass_context=True, no_pm=True)
	@checks.admin_or_perm(manage_server=True)
	async def leaveserver(self, ctx):
		"""bye"""
		await self.bot.say("bye faggots :wave:")
		await self.bot.leave_server(ctx.message.server)

	@commands.group(pass_context=True, invoke_without_command=True, aliases=['nickname'], no_pm=True)
	@checks.mod_or_perm(manage_server=True)
	async def nick(self, ctx, *, nickname:str):
		"""Change a user(s) nickname"""
		if ctx.message.server.me.permissions_in(ctx.message.channel).manage_nicknames == False:
			await self.bot.say("Sorry, I do not have the manage_nicknames permission\n**Aborting**")
			return
		if len(ctx.message.mentions) == 0:
			user = ctx.message.author
			await self.bot.change_nickname(user, nickname)
			await self.bot.say("ok, changed your to `{1}`".format(user.name, nickname))
			return
		for member in ctx.message.mentions:
			nickname = nickname.replace(member.mention, '').replace('<@!{0}>'.format(member.id), '')
		if len(nickname) > 32:
			await self.bot.say(':warning: `Nickname truncated, too long (<= 32).`')
			nickname = nickname[:32]
		for user in ctx.message.mentions:
			await self.bot.change_nickname(user, nickname)
			await self.bot.say("ok, changed the nickname of `{0}` to `{1}`".format(user.name, nickname))
			await asyncio.sleep(.21)

	@nick.command(name='mass', pass_context=True, no_pm=True)
	@commands.cooldown(1, 200)
	@checks.admin_or_perm(manage_server=True)
	async def _nick_massnick(self, ctx, *, name:str):
		"""Change everyones nickname"""
		if ctx.message.server.me.permissions_in(ctx.message.channel).manage_nicknames == False:
			await self.bot.say("Sorry, I do not have the manage_nicknames permission\n**Aborting**")
			return
		elif ctx.message.server.id in self.nick_massing:
			await self.bot.say('lol no, already nick massing asshole.')
			return
		elif ctx.message.server.id in self.nick_unmassing:
			await self.bot.say('lol no, already nick unmassing asshole.')
			return
		await self.bot.say("this might take a while, pls wait")
		self.nick_massing.append(ctx.message.server.id)
		members = list(ctx.message.server.members)
		if len(members) >= 500:
			sleep_time = .45
		else:
			sleep_time = .10
		count = 0
		for member in members:
			if member.nick == name:
				continue
			elif member.status in (discord.Status.offline, discord.Status.invisible) and 'all' not in name and member.top_role.position < ctx.message.server.me.top_role.position:
				continue
			try:
				await self.bot.change_nickname(member, name)
			except:
				continue
			await asyncio.sleep(sleep_time)
			count += 1
		await self.bot.say("ok, changed the nickname of `{0}` users".format(count))
		self.nick_massing.remove(ctx.message.server.id)

	@nick.command(name='massunick', aliases=['revert', 'massun'], pass_context=True, no_pm=True)
	@commands.cooldown(1, 200)
	@checks.admin_or_perm(manage_server=True)
	async def _nick_massunick(self, ctx):
		"""Default every users nickname in the server"""
		if ctx.message.server.me.permissions_in(ctx.message.channel).manage_nicknames == False:
			await self.bot.say("Sorry, I do not have the manage_nicknames permission\n**Aborting**")
			return
		elif ctx.message.server.id in self.nick_unmassing:
			await self.bot.say('lol no, already nick unmassing asshole.')
			return
		elif ctx.message.server.id in self.nick_massing:
			await self.bot.say('lol no, already nick massing asshole.')
			return
		await self.bot.say("this might take a while, pls wait")
		self.nick_unmassing.append(ctx.message.server.id)
		members = list(ctx.message.server.members)
		if len(members) >= 500:
			sleep_time = .45
		else:
			sleep_time = .10
		count = 0
		for member in members:
			if member.nick and member.status not in (discord.Status.offline, discord.Status.invisible) and member.top_role.position < ctx.message.server.me.top_role.position:
				try:
					await self.bot.change_nickname(member,member.name)
				except:
					pass
				await asyncio.sleep(sleep_time)
				count += 1
		await self.bot.say("ok, reset the nickname of `{0}` users".format(str(count)))
		self.nick_unmassing.remove(ctx.message.server.id)

	async def gist_logs(self, ctx, idk, content:str):
		payload = {
			'title': '"{0}" Logs'.format(idk),
			'name': 'NotSoBot - By: {0}'.format(ctx.message.author),
			'text': content,
			'private': '1',
			'expire': '0'
		}
		with aiohttp.ClientSession() as session:
			async with session.post('https://spit.mixtape.moe/api/create', data=payload) as r:
				url = await r.text()
				await self.bot.say('Uploaded to paste, URL: <{0}>'.format(url))

	mention_regex = re.compile(r'(<@((\!|\&)?[0-9]*?)>)')
	@commands.group(pass_context=True, invoke_without_command=True)
	@commands.cooldown(1, 10)
	@checks.mod_or_perm(manage_messages=True)
	async def logs(self, ctx, max_messages:int=500, channel:discord.Channel=None):
		"""Returns gist and file of messages for current/a channel"""
		print("1")
		if max_messages > 2500:
			await self.bot.say("2 many messages (<= 2500)")
			return
		if channel is None:
			channel = ctx.message.channel
		count = 0
		rand = str(random.randint(0, 100))
		path = self.files_path("logs/clogs_{0}_{1}.txt".format(channel.name, rand))
		open(path, 'w').close()
		idk = True
		async for message in self.bot.logs_from(channel, limit=max_messages):
			if message.server is None:
				message.server = message.channel
			with io.open(path, "a", encoding='utf8') as f:
				line = ''
				if idk:
					line += "Server: {0.name} <{0.id}>\n".format(message.server)
					line += "Channel: {0.name} <{0.id}>\n\n".format(message.channel)
					idk = False
				line += "Time: {0}\n".format(message.timestamp.strftime('%m/%d/%Y %H:%M:%S'))
				line += "Author: {0.name} <{0.id}>\n".format(message.author)
				user = None
				if self.mention_regex.search(message.content):
					ss = self.mention_regex.search(message.content)
					mention_id = ss.group(2)
					if mention_id.startswith('!'):
						mention_id = mention_id.replace('!', '')
					for server in self.bot.servers:
						if user is None:
							user = discord.Server.get_member(server, user_id=mention_id)
						else:
							break
					if user != None:
						message.content = message.content.replace(ss.group(1), '{0.name}#{0.discriminator} (Discord mention converted)'.format(user))
				line += "Message: {0}\n\n".format(message.content)
				f.write(line)
				f.close()
			count += 1
		await self.gist_logs(ctx, ctx.message.channel.name, open(path).read())
		await self.bot.send_file(ctx.message.channel, path, filename="logs_{0}.txt".format(ctx.message.channel.name), content="ok, here is a file/gist of the last `{0}` messages.".format(count))

	@logs.command(name="user", pass_context=True)
	@commands.cooldown(1, 10)
	@checks.mod_or_perm(manage_messages=True)
	async def _logs_user(self, ctx, max_messages:int=500, user:str=None, channel:discord.Channel=None):
		try:
			if max_messages > 2500:
				await self.bot.say("2 many messages (<= 2500)")
				return
			user_id = False
			if user is None:
				user = ctx.message.author
			else:
				if len(ctx.message.mentions) == 0:
					user_id = True
				else:
					user = ctx.message.mentions[0]
			server = ctx.message.server
			if channel is None:
				channel = ctx.message.channel
			count = 0
			rand = str(random.randint(0, 100))
			path = self.files_path("logs/logs_{0}_{1}.txt".format(user, rand))
			open(path, 'w').close()
			idk = True
			user_id_u = None
			async for message in self.bot.logs_from(channel, limit=max_messages):
				if user_id:
					if message.author.id != user:
						continue
				else:
					if message.author != user:
						continue
				if user_id:
					user_id_u = message.author
				if message.server is None:
					message.server = message.channel
				with io.open(path, "a", encoding='utf8') as f:
					line = ''
					if idk:
						line += "Server: {0.name} <{0.id}>\n".format(message.server)
						line += "Channel: {0.name} <{0.id}>\n\n".format(message.channel)
						idk = False
					line += "Time: {0}\n".format(message.timestamp.strftime('%m/%d/%Y %H:%M:%S'))
					line += "Author: {0.name} <{0.id}>\n".format(message.author)
					mention_user = None
					if self.mention_regex.search(message.content):
						ss = self.mention_regex.search(message.content)
						mention_id = ss.group(2)
						if mention_id.startswith('!'):
							mention_id = mention_id.replace('!', '')
						for server in self.bot.servers:
							if mention_user is None:
								mention_user = discord.Server.get_member(server, user_id=mention_id)
							else:
								break
						if mention_user != None:
							message.content = message.content.replace(ss.group(1), '{0.name}#{0.discriminator} (Discord mention converted)'.format(mention_user))
					line += "Message: {0}\n\n".format(message.content)
					f.write(line)
					f.close()
				count += 1
			if user_id_u:
				user = user_id_u
			if count == 0:
				await self.bot.say(":warning: No messages found within `{0}` searched for `{1}`!".format(max_messages, user))
				return
			await self.gist_logs(ctx, user.name, open(path).read())
			await self.bot.send_file(ctx.message.channel, path, filename="logs_{0}.txt".format(user.name), content="ok, here is a file/gist of the last `{1}` messages for {0.name}#{0.discriminator}".format(user, count))
		except Exception as e:
			await self.bot.say(code.format(e))

	@commands.group(pass_context=True, invoke_without_command=True, no_pm=True)
	@checks.mod_or_perm(manage_server=True)
	async def inv(self, ctx):
		"""Create a Server Invite"""
		invite = await self.bot.create_invite(ctx.message.server)
		await self.bot.say(invite)

	@inv.command(name='delete', pass_context=True, invoke_without_command=True, no_pm=True)
	@checks.mod_or_perm(manage_server=True)
	async def _inv_delete(self, ctx, invite:str):
		"""Delete a Server Invite"""
		await self.bot.delete_invite(invite)
		await self.bot.say("ok, deleted/revoked invite")

	@inv.command(name='list', pass_context=True, invoke_without_command=True, no_pm=True)
	@checks.mod_or_perm(manage_server=True)
	async def _inv_list(self, ctx):
		"""List all Server Invites"""
		invites = await self.bot.invites_from(ctx.message.server)
		if len(invites) == 0:
			await self.bot.say(":warning: There currently no invites active.")
		else:
			await self.bot.say("Invites: {0}".format(", ".join(map(str, invites))))

	@inv.group(name='cserver', pass_context=True, invoke_without_command=True)
	@checks.is_owner()
	async def _inv_cserver(self, ctx, *, name:str):
		found = False
		for server in self.bot.servers:
			if name in server.name:
				for c in server.channels:
					s = c
					found = True
					break
		if found:
			try:
				invite = await self.bot.create_invite(s)
			except:
				await self.bot.say("no perms")
				return
			await self.bot.say(invite)
		else:
			await self.bot.say("no server found")

	@_inv_cserver.command(name='id', pass_context=True, invoke_without_command=True)
	@checks.is_owner()
	async def _inv_cserver_id(self, ctx, id:str):
		s = self.bot.get_server(id)
		if s is None:
			await self.bot.say('no server id found')
			return
		invite = await self.bot.create_invite(s)
		await self.bot.say(invite)

	@commands.group(pass_context=True, invoke_without_command=True)
	@checks.mod_or_perm(manage_messages=True)
	async def pin(self, ctx, max_messages:int=1500, *, txt:str):
		"""Attempt to find a Message by ID or Content and Pin it"""
		if ctx.message.server.me.permissions_in(ctx.message.channel).manage_messages == False:
			await self.bot.say("Sorry, this doesn't work on this server (No manage_messages Permission)!")
			return
		if max_messages > 1500:
			await self.bot.say("2 many messages (<= 2500)")
			return
		async for message in self.bot.logs_from(ctx.message.channel, before=ctx.message, limit=max_messages):
			if message.id == txt:
				try:
					await self.bot.pin_message(message)
				except:
					await self.bot.say(":warning: Could not pin message\nNo permission")
					return
				else:
					await self.bot.say(":ok: Pinned Message with Given ID")
					return
			elif txt in message.content:
				try:
					await self.bot.pin_message(message)
				except:
					await self.bot.say(":warning: Maximum Pins Reached (50).")
					return
				else:
					await self.bot.say(":ok: Pinned Message with given text in it!".format(txt))
					return
			else:
				continue
		await self.bot.say(":exclamation: No message found with ID or Content given!")

	@pin.command(name='date', pass_context=True)
	async def _pin_date(self, ctx, date:str, channel:discord.Channel=None):
		"""Pin a message after the specified date\nUse the \"pin first\" command to pin the first message!"""
		if ctx.message.server.me.permissions_in(ctx.message.channel).manage_messages == False:
			await self.bot.say("Sorry, this doesn't work on this server (No manage_messages Permission)!")
			return
		_date = None
		fmts = ('%Y/%m/%d', '%Y-%m-%d', '%m-%d-%Y', '%m/%d/%Y')
		for s in fmts:
			try:
				_date = datetime.datetime.strptime(date, s)
			except ValueError:
				continue
		if _date is None:
			await self.bot.say(':warning: Cannot convert to date. Formats: `YYYY/MM/DD, YYYY-MM-DD, MM-DD-YYYY, MM/DD/YYYY`')
			return
		if channel is None:
			channel = ctx.message.channel
		async for message in self.bot.logs_from(channel, after=_date, limit=1):
			try:
				await self.bot.pin_message(message)
			except:
				await self.bot.say(":warning: Maximum Pins Reached (50).")
				return
			else:
				await self.bot.say(":ok: Pinned Message with date \"{0}\"!".format(str(_date)))
				return
		await self.bot.say(":exclamation: No message found with date given!")

	@pin.command(name='before', pass_context=True)
	async def _pin_before(self, ctx, date:str, max_messages:int=1500, *, txt:str):
		"""Pin a message before a certain date"""
		if ctx.message.server.me.permissions_in(ctx.message.channel).manage_messages == False:
			await self.bot.say("Sorry, this doesn't work on this server (No manage_messages Permission)!")
			return
		if max_messages > 1500:
			await self.bot.say("2 many messages (<= 1500")
			return
		_date = None
		fmts = ('%Y/%m/%d', '%Y-%m-%d', '%m-%d-%Y', '%m/%d/%Y')
		for s in fmts:
			try:
				_date = datetime.datetime.strptime(date, s)
			except ValueError:
				continue
		if _date is None:
			await self.bot.say(':warning: Cannot convert to date. Formats: `YYYY/MM/DD, YYYY-MM-DD, MM-DD-YYYY, MM/DD/YYYY`')
			return
		if channel is None:
			channel = ctx.message.channel
		async for message in self.bot.logs_from(channel, before=_date, limit=max_messages):
			if txt in message.content:
				try:
					await self.bot.pin_message(message)
				except:
					await self.bot.say(":warning: Maximum Pins Reached (50).")
					return
				else:
					await self.bot.say(":ok: Pinned Message before date \"{0}\" with given text!".format(str(_date)))
					return
		await self.bot.say(":exclamation: No message found with given text before date given!")

	@pin.command(name='first', aliases=['firstmessage'], pass_context=True)
	async def _pin_first(self, ctx, channel:discord.Channel=None):
		"""Pin the first message in current/specified channel!"""
		if ctx.message.server.me.permissions_in(ctx.message.channel).manage_messages == False:
			await self.bot.say("Sorry, this doesn't work on this server (No manage_messages Permission)!")
			return
		if channel is None:
			channel = ctx.message.channel
		date = str(ctx.message.channel.created_at).split()[0]
		_date = datetime.datetime.strptime(date, '%Y-%m-%d')
		async for message in self.bot.logs_from(channel, after=_date, limit=1):
			try:
				await self.bot.pin_message(message)
			except:
				await self.bot.say(":warning: Maximum Pins Reached (50).")
				return
			else:
				if len(message.content) > 2000:
					message.content = message.content[:2000]+"\n:warning: Message Truncated (<= 2000)"
				message.content = message.content
				if len(message.mentions) != 0:
					for s in message.mentions:
						message.content = message.content.replace(s.mention, s.name)
				await self.bot.say(":ok: Pinned First Message with date \"{0}\"!\n**Message Info**\nAuthor: `{1}`\nTime: `{2}`\nContent: \"{3}\"".format(str(_date), message.author.name, message.timestamp.strftime('%m/%d/%Y %H:%M:%S'), message.content))
				return
		await self.bot.say(":exclamation: No first message found!")

	@commands.command(pass_context=True)
	@checks.is_owner()
	async def sql(self, ctx, *, sql:str):
		"""Debug SQL"""
		try:
			results = self.cursor.execute(sql).fetchall()
			await self.bot.say("**SQL RESULTS**\n"+str(results))
			while True:
				response = await self.bot.wait_for_message(timeout=15, author=ctx.message.author, channel=ctx.message.channel)
				if response is None or response.content != 'sql commit':
					return
				else:
					break
			self.cursor.commit()
			await self.bot.say("commited")
		except Exception as e:
			await self.bot.say(code.format(e))

	@commands.command(pass_context=True)
	@commands.bot_has_permissions(ban_members=True)
	@checks.mod_or_perm(ban_members=True)
	async def hackban(self, ctx, *users:str):
		banned = []
		for user in users:
			u = discord.Object(id=user)
			u.server = ctx.message.server
			try:
				await self.bot.ban(u)
				banned.append(user)
			except:
				uu = ctx.message.server.get_member(user)
				if uu is None:
					await self.bot.say('`{0}` could not be hack banned.'.format(user))
				else:
					await self.bot.say('`{0}` is already on the server and could not be banned.'.format(uu))
				continue
		if banned:
			await self.bot.say(':white_check_mark: Hackbanned `{0}`!'.format(", ".join(banned)))

def setup(bot):
	bot.add_cog(Moderation(bot))
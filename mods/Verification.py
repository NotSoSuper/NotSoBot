import discord
import asyncio
import random
import steam
from steam.steamid import SteamId
from steam.steamprofile import SteamProfile
from steam.steamaccountuniverse import SteamAccountUniverse
from steam.steamaccounttype import SteamAccountType
from discord.ext import commands
from utils import checks
from mods.cog import Cog

code = "```py\n{0}\n```"

class Verification(Cog):
	def __init__(self, bot):
		super().__init__(bot)
		self.cursor = bot.mysql.cursor
		self.escape = bot.escape
		self.bot.loop.create_task(self.verification_task())

	async def remove_verification(self, server, idk=None):
		role = discord.utils.get(server.roles, name='Awaiting Approval')
		if role:
			try:
				await self.bot.delete_role(server, role)
			except:
				pass
		sql = 'DELETE FROM `verification` WHERE server={0}'
		sql = sql.format(server.id)
		self.cursor.execute(sql)
		self.cursor.commit()
		sql = 'DELETE FROM `verification_queue` WHERE server={0}'
		sql = sql.format(server.id)
		self.cursor.execute(sql)
		self.cursor.commit()
		if idk is None:
			try:
				await self.bot.send_message(server.owner, ":warning: One of your server administrators (or you) have enabled approval/verification on user join.\n\nAdministrator permission was taken away from me making the feature unusable, I need Administrator permission to make/add a role to mute on join.\n\n`The system has been automatically disabled, re-enable anytime if you please.`")
			except:
				pass

	@commands.group(pass_context=True, aliases=['onjoinverify', 'approval'], invoke_without_command=True, no_pm=True)
	@checks.admin_or_perm(manage_server=True)
	async def verification(self, ctx, channel:discord.Channel=None, *, mentions:str=None):
		perms = ctx.message.server.me.permissions_in(ctx.message.channel)
		if perms.manage_roles is False or perms.manage_channels is False:
			if perms.administrator is False:
				await self.bot.say(":warning: `I need Administrator permission to make/add a role to mute on join`")
				return
		if channel is None:
			channel = ctx.message.channel
		sql = 'SELECT * FROM `verification` WHERE server={0}'
		sql = sql.format(ctx.message.server.id)
		result = self.cursor.execute(sql).fetchall()
		if len(result) == 0:
			if mentions is None:
				sql = "INSERT INTO `verification` (`server`, `channel`) VALUES (%s, %s)"
				self.cursor.execute(sql, (ctx.message.server.id, channel.id))
				self.cursor.commit()
				await self.bot.say(":white_check_mark: Enabled user approval/verification on join, all requests will go to {0} (`verification #<discord_channel>` to change)!".format(channel.mention))
			else:
				if len(ctx.message.mentions) == 0:
					await self.bot.say("invalid mention")
					return
				sql = "INSERT INTO `verification` (`server`, `channel`, `mentions`) VALUES (%s, %s, %s)"
				mention_ids = []
				mention_names = []
				for mention in ctx.message.mentions:
					mention_ids.append(mention.id)
					mention_names.append(mention.name)
				self.cursor.execute(sql, (ctx.message.server.id, channel.id, ' '.join(mention_ids)))
				self.cursor.commit()
				await self.bot.say(":white_check_mark: Enabled user approval/verification on join, all requests will go to {0} (`verification <#discord_channel>` to change) and mention `{0}`!".format(channel.mention, ', '.join(mention_names)))
			permissions = discord.Permissions()
			permissions.read_messages = True
			try:
				await self.bot.create_role(ctx.message.server, name='Awaiting Approval', color=discord.Colour(int("FF0000", 16)), permissions=permissions)
			except Exception as e:
				print(e)
				await self.bot.say(":warning: For some reason I couldn't create the \"Awaiting Approval\" role and users won't be muted, please create it (same name) and disable all the permissions you don't want unapproved-users to have.\nMake sure I have the administrator permission!")
		elif channel is None:
			sql = 'UPDATE `verification` SET channel={0} WHERE server={1}'
			sql = sql.format(channel.id, ctx.message.server.id)
			self.cursor.execute(sql)
			self.cursor.commit()
			await self.bot.say(":white_check_mark: Set approval/verification channel to {0}".format(channel.mention))
		else:
			await self.bot.say(':warning: You are about to disable member verification/approval on join, type `yes` to proceed.')
			while True:
				response = await self.bot.wait_for_message(timeout=15, author=ctx.message.author, channel=ctx.message.channel)
				if response is None or response.content != 'yes':
					await self.bot.say('**Aborting**')
					return
				else:
					break
			await self.remove_verification(ctx.message.server, True)
			try:
				role = discord.utils.get(ctx.message.server.roles, name='Awaiting Approval')
				if role != None:
					await self.bot.delete_role(ctx.message.server, role)
			except discord.errors.Forbidden:
				await self.bot.say("could not remove role, you took my perms away :(")
			role2 = discord.utils.get(ctx.message.server.roles, name='Approved')
			if role2 != None:
				try:
					await self.bot.delete_role(ctx.message.server, role2)
				except:
					pass
			await self.bot.say(":negative_squared_cross_mark: **Disabled** user approval on join")

	@verification.command(name='mention', aliases=['mentions'], pass_context=True, invoke_without_command=True, no_pm=True)
	@checks.admin_or_perm(manage_server=True)
	async def verification_mention(self, ctx, *mentions:str):
		perms = ctx.message.server.me.permissions_in(ctx.message.channel)
		if perms.manage_roles is False or perms.manage_channels is False:
			if perms.administrator is False:
				await self.bot.say(":warning: `I need Administrator permission to make/add a role to mute on join`")
				return
		if len(ctx.message.mentions) == 0 and '@everyone' not in mentions and '@here' not in mentions:
			await self.bot.say(':no_entry: `Invalid mention(s).`')
			return
		sql = 'SELECT * FROM `verification` WHERE server={0}'
		sql = sql.format(ctx.message.server.id)
		result = self.cursor.execute(sql).fetchall()
		if len(result) == 0:
			await self.bot.say(":no_entry: This server does not have approval/verification turned on (`verification <#discord_channel>` to do so)!!!")
			return
		if len(mentions) == 0:
			sql = 'UPDATE `verification` SET mentions=NULL WHERE server={0}'
			sql = sql.format(ctx.message.server.id)
			self.cursor.execute(sql)
			self.cursor.commit()
			await self.bot.say(":negative_squared_cross_mark: Disabled/Removed mentions on user join for approval")
		else:
			mention_ids = []
			mention_names = []
			everyone = False
			for mention in mentions:
				if mention == '@everyone':
					mention_ids.append('@everyone')
				elif mention == '@here':
					mention_ids.append('@here')
			for mention in ctx.message.mentions:
				mention_ids.append(mention.id)
				mention_names.append(mention.name)
			sql = 'SELECT mentions FROM `verification` WHERE server={0}'
			sql = sql.format(ctx.message.server.id)
			mention_results = self.cursor.execute(sql).fetchall()
			update = False
			if mention_results[0]['mentions'] != None:
				update = True
				things = mention_results[0]['mentions'].split()
				for x in things:
					mention_ids.append(x)
			sql = "UPDATE `verification` SET mentions={0} WHERE server={1}"
			sql = sql.format(self.escape(' '.join(mention_ids)), ctx.message.server.id)
			self.cursor.execute(sql)
			self.cursor.commit()
			if update:
				await self.bot.say(":white_check_mark: Updated mentions to include `{0}` on user join for approval".format(', '.join(mention_names)))
			else:
				await self.bot.say(":white_check_mark: Set `{0}` to be mentioned on user join for approval".format(', '.join(mention_names)))

	@commands.group(pass_context=True, invoke_without_command=True, no_pm=True)
	@checks.mod_or_perm(manage_server=True)
	async def verify(self, ctx, *users:str):
		perms = ctx.message.server.me.permissions_in(ctx.message.channel)
		if perms.manage_roles is False or perms.manage_channels is False:
			if perms.administrator is False:
				await self.bot.say(":warning: `I need Administrator permission to make/add a role to mute on join`")
				return
		if len(users) == 0:
			await self.bot.say("pls input users to verify thx")
			return
		sql = 'SELECT * FROM `verification` WHERE server={0}'
		sql = sql.format(ctx.message.server.id)
		result = self.cursor.execute(sql).fetchall()
		if len(result) == 0:
			await self.bot.say(":no_entry: This server does not have approval/verification turned **on** (`verification <#discord_channel>` to do so)!!!")
			return
		role = discord.utils.get(ctx.message.server.roles, name="Awaiting Approval")
		count = 0 
		count2 = 0
		discord_user = None
		for user in users:
			if user.isdigit():
				user = int(user)
				sql = 'SELECT * FROM `verification_queue` WHERE server={0} AND id={1}'
				sql = sql.format(ctx.message.server.id, user)
				result = self.cursor.execute(sql).fetchall()
				if len(result) == 0:
					await self.bot.say(":warning: `{0}` is not in the verification queue.".format(user))
					if len(users) > 1:
						continue
					else:
						return
				sql = 'DELETE FROM `verification_queue` WHERE server={0} AND id={1}'
				sql = sql.format(ctx.message.server.id, user)
				self.cursor.execute(sql)
				self.cursor.commit()
				discord_user = discord.Server.get_member(ctx.message.server, user_id=str(result[count]['user']))
				count += 1
			else:
				if len(ctx.message.mentions) == 0:
					await self.bot.say("If you're not gonna use approval id, atleast mention correctly!")
					return
				for x in ctx.message.mentions:
					if count == len(ctx.message.mentions):
						break
					sql = 'SELECT * FROM `verification_queue` WHERE server={0} AND user={1}'
					sql = sql.format(ctx.message.server.id, x.id)
					result = self.cursor.execute(sql).fetchall()
					if len(result) == 0:
						await self.bot.say(":warning: `{0}` is not in the verification queue.".format(user))
						if len(users) > 1:
							continue
						else:
							return
					sql = 'DELETE FROM `verification_queue` WHERE server={0} AND user={1}'
					sql = sql.format(ctx.message.server.id, x.id)
					self.cursor.execute(sql)
					self.cursor.commit()
					discord_user = discord.Server.get_member(ctx.message.server, user_id=str(result[count2]['user']))
					count2 += 1
			if discord_user is None:
				continue
			try:
				await self.bot.remove_roles(discord_user, role)
			except Exception as e:
				await self.bot.say(code.format(e))
				await self.bot.say(":warning: {0} was removed from the queue however his role could not be removed because I do not have Administrator permissions.\nPlease remove the role manually and give me **Administrator**.".format(user))
				return
			role = discord.utils.get(ctx.message.server.roles, name='Approved')
			if role != None:
				try:
					await self.bot.add_roles(discord_user, role)
				except:
					pass
			await self.bot.say(":white_check_mark: Removed `{0}` from queue!".format(user))
			queue_removed_msg = 'You have been approved/verified for `{0}` and can now message!'.format(ctx.message.server.name)
			await self.bot.send_message(discord_user, queue_removed_msg)

	@verify.command(name='list', pass_context=True, invoke_without_command=True, no_pm=True)
	async def verify_list(self, ctx):
		perms = ctx.message.server.me.permissions_in(ctx.message.channel)
		if perms.manage_roles is False or perms.manage_channels is False:
			if perms.administrator is False:
				await self.bot.say(":warning: `I need Administrator permission to make/add a role to mute on join`")
				return
		sql = 'SELECT * FROM `verification` WHERE server={0}'
		sql = sql.format(ctx.message.server.id)
		result = self.cursor.execute(sql).fetchall()
		if len(result) == 0:
			await self.bot.say(":no_entry: This server does not have approval/verification turned on (`verification <#discord_channel>` to do so)!!!")
			return
		sql = 'SELECT * FROM `verification_queue` WHERE server={0}'
		sql = sql.format(ctx.message.server.id)
		result = self.cursor.execute(sql).fetchall()
		if len(result) == 0:
			await self.bot.say(":no_entry: `There are no users in the verification/approval queue`")
			return
		users = []
		for s in result:
			user = discord.Server.get_member(ctx.message.server, user_id=str(s['user']))
			if user is None:
				continue
			users.append('{0}#{1} ({2})'.format(user.name, user.discriminator, str(s['id'])))
		await self.bot.say("**{0} Users in Queue**\n`{1}`".format(len(users), ', '.join(users)))

	# steam_regex = r"^(http|https|)(\:\/\/|)steamcommunity\.com\/id\/(.*)$"
	@verify.command(name='check', pass_context=True, aliases=['steam', 'link'])
	async def verify_check(self, ctx, stem:str):
		try:
			if ctx.message.channel.is_private is False:
				await self.bot.say(':no_entry: `Private Message only.`')
				return
			sql = 'SELECT * FROM `verification_queue` WHERE user={0}'
			sql = sql.format(ctx.message.author.id)
			result = self.cursor.execute(sql).fetchall()
			if len(result) == 0:
				await self.bot.say(':no_entry: You are not in the verification queue for any server.')
				return
			server_id = result[0]['server']
			sql = 'SELECT * FROM `verification` WHERE server={0}'
			sql = sql.format(server_id)
			result = self.cursor.execute(sql).fetchall()
			if len(result) == 0:
				await self.bot.say(":no_entry: Server you are in queue for disabled verification.")
				return
			sql = 'SELECT * FROM `verification_steam` WHERE server={0} AND user={1}'
			sql = sql.format(server_id, ctx.message.author.id)
			result = self.cursor.execute(sql).fetchall()
			if len(result) != 0:
				await self.bot.say(":no_entry: You've already verified your steam account!")
				return
			sql = 'SELECT id,server FROM `verification_queue` WHERE server={0} AND user={1}'
			sql = sql.format(server_id, ctx.message.author.id)
			result = self.cursor.execute(sql).fetchall()
			if len(result) == 0:
				await self.bot.say(":warning: `{0}` is not in the verification queue.".format(ctx.message.author))
				return
			verification_id = str(result[0]['id'])
			steamId = None
			steamProfile = None
			if steamId is None: 
				steamId = SteamId.fromSteamId("{0}".format(stem))
			if steamId is None: 
				steamId = SteamId.fromSteamId3(stem)
			if steamId is None: 
				steamId = SteamId.fromSteamId64(stem)
			if steamId is None: 
				steamId = SteamId.fromProfileUrl(stem)
			if steamId is None: 
				steamProfile = SteamProfile.fromCustomProfileUrl(stem)
				if steamProfile is None:
					await self.bot.say("`:no_entry: `Bad Steam ID/64/URL`")
					return
				steamId = steamProfile.steamId
			else:
				steamProfile = SteamProfile.fromSteamId(steamId)
			if verification_id in steamProfile.displayName:
				sql = 'INSERT INTO `verification_steam` (`user`, `server`, `steam`, `id`) VALUES (%s, %s, %s, %s)'
				self.cursor.execute(sql, (ctx.message.author.id, server_id, steamId.profileUrl, verification_id))
				self.cursor.commit()
				await self.bot.say(':white_check_mark: `{0}` steam profile submitted and passed steam name check, awaiting moderator approval.'.format(ctx.message.author))
			else:
				await self.bot.say(':warning: **{0}** is not in the steam accounts name.'.format(verification_id))
		except Exception as e:
			await self.bot.say(code.format(e))

	async def verification_task(self):
		if self.bot.shard_id != 0:
			return
		while True:
			sql = 'SELECT * FROM `verification_steam`'
			result = self.cursor.execute(sql).fetchall()
			if len(result) == 0:
				await asyncio.sleep(60)
				continue
			for s in result:
				server = self.bot.manager.get_server(str(s['server']))
				if server:
					user = server.get_member(str(s['user']))
					if user is None:
						continue
					sql = 'SELECT channel FROM `verification` WHERE server={0}'
					sql = sql.format(server.id)
					channel = server.get_channel(str(self.cursor.execute(sql).fetchall()[0]['channel']))
					msg = '**Steam Account Check**\n`{0} (Verification ID: {1})` has submitted their steam profile and passed the name check.\n`Steam Profile:` {2}'.format(user, s['id'], s['steam'])
					await self.bot.send_message(channel, msg)
					sql = 'DELETE FROM `verification_steam` WHERE server={0} AND user={1}'
					sql = sql.format(server.id, user.id)
					self.cursor.execute(sql)
					self.cursor.commit()
			await asyncio.sleep(60)

	async def on_member_join(self, member):
		try:
			if member.bot:
				return
			server = member.server
			sql = 'SELECT * FROM `verification` WHERE server={0}'
			sql = sql.format(server.id)
			result = self.cursor.execute(sql).fetchall()
			if len(result) == 0:
				return
			channel = server.get_channel(str(result[0]['channel']))
			if channel is None:
				raise discord.errors.NotFound
			perms = server.me.permissions_in(channel)
			if perms.manage_roles is False or perms.manage_channels is False:
				if perms.administrator is False:
					await self.remove_verification(server)
					return
			sql = "INSERT INTO `verification_queue` (`user`, `server`, `id`) VALUES (%s, %s, %s)"
			rand = random.randint(0, 99999)
			self.cursor.execute(sql, (member.id, server.id, rand))
			self.cursor.commit()
			role = discord.utils.get(server.roles, name='Awaiting Approval')
			await self.bot.add_roles(member, role)
			for s in server.channels:
				perms = member.permissions_in(s)
				if perms.read_messages is False:
					continue
				overwrite = discord.PermissionOverwrite()
				overwrite.send_messages = False
				overwrite.read_messages = False
				await self.bot.edit_channel_permissions(s, role, overwrite)
			msg = ''
			if result[0]['mentions']:
				for x in result[0]['mentions'].split(' '):
					if 'everyone' in x or 'here' in x:
						msg += '{0} '.format(x)
					else:
						msg += '<@{0}> '.format(x)
				msg += '\n'
			msg += ':warning: `{0}` has joined the server and is awaiting approval\n\nRun `verify {1} or mention` to approve, kick user to remove from the queue.'.format(member, rand)
			await self.bot.send_message(channel, msg, replace_everyone=False, replace_mentions=False)
			join_msg = "You've been placed in the approval queue for `{0}`, please be patient and wait until a staff member approves your join!\n\nIf you'd like to expedite approval (and have a steam account), place **{1}** in your steam name and then run `.verify check <stean_url/id/vanity>`.".format(server.name, rand)
			await self.bot.send_message(member, join_msg)
		except (discord.errors.Forbidden, discord.errors.InvalidArgument, discord.errors.NotFound):
			await self.remove_verification(server)

	async def on_member_remove(self, member):
		try:
			if member.bot:
				return
			server = member.server
			sql = 'SELECT * FROM `verification` WHERE server={0}'
			sql = sql.format(server.id)
			result = self.cursor.execute(sql).fetchall()
			if len(result) == 0:
				return
			sql = 'SELECT * FROM `verification_queue` WHERE server={0} AND user={1}'
			sql = sql.format(server.id, member.id)
			result2 = self.cursor.execute(sql).fetchall()
			if len(result2) == 0:
				return
			sql = 'DELETE FROM `verification_queue` WHERE server={0} AND user={1}'
			sql = sql.format(server.id, member.id)
			self.cursor.execute(sql)
			self.cursor.commit()
			channel = self.bot.get_channel(id=str(result[0]['channel']))
			await self.bot.send_message(channel, ':exclamation: `{0}` has been removed from the approval/verification queue for leaving the server or being kicked.'.format(member))
		except (discord.errors.Forbidden, discord.errors.InvalidArgument, discord.errors.NotFound):
			await self.remove_verification(server)

	async def on_member_ban(self, member):
		try:
			if member.bot:
				return
			server = member.server
			sql = 'SELECT * FROM `verification` WHERE server={0}'
			sql = sql.format(server.id)
			result = self.cursor.execute(sql).fetchall()
			if len(result) == 0:
				return
			sql = 'SELECT * FROM `verification_queue` WHERE server={0} AND user={1}'
			sql = sql.format(server.id, member.id)
			result2 = self.cursor.execute(sql).fetchall()
			if len(result2) == 0:
				return
			sql = 'DELETE FROM `verification_queue` WHERE server={0} AND user={1}'
			sql = sql.format(server.id, member.id)
			self.cursor.execute(sql)
			self.cursor.commit()
			channel = self.bot.get_channel(id=str(result[0]['channel']))
			await self.bot.send_message(channel, ':exclamation: `{0}` has been removed from the approval/verification queue for being banned from the server.'.format(member))
		except (discord.errors.Forbidden, discord.errors.InvalidArgument, discord.errors.NotFound):
			await self.remove_verification(server)

def setup(bot):
	bot.add_cog(Verification(bot))
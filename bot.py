import asyncio, discord
import os, traceback, linecache, logging
import re, time, datetime
import textwrap
from discord.ext import commands
from discord.state import ConnectionState
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from utils import checks
from utils.funcs import Funcs

#Discord Code Block Formats
code = "```py\n{0}\n```"
diff = "```diff\n{0}\n```"

def init_logging(shard_id, bot):
	logging.root.setLevel(logging.INFO)
	logger = logging.getLogger('NotSoBot #{0}'.format(shard_id))
	logger.setLevel(logging.INFO)
	log = logging.getLogger()
	log.setLevel(logging.INFO)
	handler = logging.FileHandler(filename='notsobot_{0}.log'.format(shard_id), encoding='utf-8', mode='a')
	log.addHandler(handler)
	bot.logger = logger
	bot.log = log

class Object(object):
	pass

#Bot Utility Functions/Variables
def init_funcs(bot):
	#Globals
	bot.globals = Object()
	bot.globals.on_ready_write = False
	bot.globals.already_ready = False
	bot.globals.command_errors = False
	bot.globals.cooldown_sent = {}
	bot.globals.command_spam = {}
	bot.globals.spam_sent = {}
	bot.globals.command_deleted_sent = {}
	#MySQL
	global cursor, engine, Session
	if bot.dev_mode:
		db = 'discord_dev'
	elif bot.self_bot:
		db = 'discord_self'
	else:
		db = 'discord'
	engine = create_engine('mysql+pymysql://{0}:@localhost/{1}?charset=utf8mb4'.format(bot.shard_id if not bot.self_bot else '', db), encoding='utf8')
	session_factory = sessionmaker(bind=engine)
	Session = scoped_session(session_factory)
	bot.mysql = Object()
	engine = bot.mysql.engine = engine
	cursor = bot.mysql.cursor = bot.get_cursor
	#Utils
	bot.pruned_messages = []
	funcs = Funcs(bot, cursor)
	bot.funcs = funcs
	bot.escape = funcs.escape
	bot.get_prefix = funcs.get_prefix
	bot.is_blacklisted = funcs.is_blacklisted
	bot.command_check = funcs.command_check
	bot.process_commands = funcs.process_commands
	bot.write_last_time = funcs.write_last_time
	bot.get_last_time = funcs.get_last_time
	bot.restart_program = funcs.restart_program
	bot.queue_message = funcs.queue_message
	bot.get_images = funcs.get_images
	bot.truncate = funcs.truncate
	bot.proxy_request = funcs.proxy_request
	bot.run_process = funcs.run_process
	bot.get_json = funcs.get_json
	bot.bytes_download = funcs.bytes_download
	bot.download = funcs.download
	bot.isimage = funcs.isimage
	bot.isgif = funcs.isgif
	bot.google_keys = funcs.google_keys
	bot.repl = funcs.repl
	bot.command_help = funcs.command_help
	bot.random = funcs.random
	bot.get_text = funcs.get_text
	#Paths
	global discord_path, files_path
	bot.path = Object()
	discord_path = bot.path.discord = funcs.discord_path
	files_path = bot.path.files = funcs.files_path

#Bot Cogs
modules = [
	'mods.Logging',
	'mods.Commands',
	'mods.Moderation',
	'mods.Utils',
	'mods.Info',
	'mods.Fun',
	'mods.Chan',
	'mods.Repl',
	'mods.Stats',
	'mods.Tags',
	'mods.Logs',
	'mods.Wc',
	# 'mods.AI',
	'mods.Changes',
	'mods.Markov',
	'mods.Verification',
	'mods.Nsfw',
	'mods.Reminders',
	'mods.JoinLeave',
	'mods.Afk'
]

#Console Colors
def prRed(prt): print("\033[91m {}\033[00m" .format(prt))
def prGreen(prt): print("\033[92m {}\033[00m" .format(prt))

class NotSoBot(commands.Bot):
	def __init__(self, *args, **kwargs):
		self.loop = kwargs.pop('loop', asyncio.get_event_loop())
		asyncio.get_child_watcher().attach_loop(self.loop)
		self.dev_mode = kwargs.pop('dev_mode', False)
		self.token = os.getenv('bot_token') if not self.dev_mode else os.getenv('bot_beta_token')
		self.self_bot = kwargs.pop('self_bot', False)
		if self.self_bot:
			self.token = os.getenv('notsosuper_token')
		shard_id = kwargs.get('shard_id', 0)
		command_prefix = kwargs.pop('command_prefix', commands.when_mentioned_or('.'))
		init_logging(shard_id, self)
		super().__init__(command_prefix=command_prefix, *args, **kwargs)
		self.remove_command('help')
		init_funcs(self)
		self.owner = None
		self.start_time = time.time()
		self.own_task = None
		self.last_message = None
		self.command_messages = {}

	def __del__(self):
		self.loop.set_exception_handler(lambda *args, **kwargs: None)

	@property
	def get_cursor(self):
		return Session()

	async def on_ready(self):
		if not self.self_bot:
			utc = int(time.time())
			last_time = self.get_last_time()
			if last_time is False:
				downtime = 0
			else:
				downtime = str(utc - int(last_time))
			time_msg = time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(last_time))
			current_time_msg = time.strftime('%m/%d/%Y %H:%M:%S')
			if self.globals.already_ready or downtime == 0:
				msg = '`[Shard {0}]` {1} has <@&211727010932719627>, <@&211727098149076995> since **{2}** for **{3}** second(s) | Current Time: **{4}**.'.format(self.shard_id, self.user.mention, time_msg, downtime, current_time_msg)
			else:
				msg = '`[Shard {0}]` {1} is now <@&211726904774885377>, <@&211727098149076995> since **{2}** for **{3}** second(s) | Current Time: **{4}**\nServers: `{5}`'.format(self.shard_id, self.user.mention, time_msg, downtime, current_time_msg, len(self.servers))
			await self.queue_message('211247117816168449', msg)
			self.globals.on_ready_write = True
			self.write_last_time()
			self.globals.already_ready = True
		for cog in modules:
			try:
				self.load_extension(cog)
			except Exception as e:
				msg = 'Failed to load mod {0}\n{1}: {2}'.format(cog, type(e).__name__, e)
				await self.queue_message('180073721048989696', '```diff\n! Shard #{0}\n- '.format(self.shard_id)+msg+'\n```')
				print(msg)
		if self.self_bot:
			print('------\nSelf Bot\n{0}\n------'.format(self.user))
		else:
			print('------\n{0}\nShard {1}/{2}{3}------'.format(self.user, self.shard_id, self.shard_count-1, '\nDev Mode: Enabled\n' if self.dev_mode else ''))
		await self.change_presence(game=discord.Game(name="https://ropestore.org"))

	async def on_message(self, message):
		self.last_message = message.timestamp
		await self.wait_until_ready()
		if self.globals.on_ready_write:
			self.write_last_time()
		if self.owner is None:
			if self.self_bot:
				self.owner = self.user
			else:
				application_info = await self.application_info()
				self.owner = application_info.owner
		if self.dev_mode and message.author != self.owner:
			return
		elif self.self_bot and message.author != self.owner:
			return
		elif not self.self_bot and message.author == self.user:
			return
		elif message.author.bot:
			return
		blacklisted = await self.is_blacklisted(message)
		if blacklisted:
			return
		prefix_result = await self.get_prefix(message)
		prefixes = prefix_result[0]
		check = prefix_result[1] if not self.self_bot else True
		command = None
		invoker = None
		pm_only = False
		for prefix in prefixes:
			if message.content.lower().startswith(prefix) and check and message.content.lower() != prefix:
				prefix_escape = re.escape(prefix)
				message_regex = re.compile(r'('+prefix_escape+r')'+r'[\s]*(\w+)(.*)', re.I|re.X|re.S)
				match = message_regex.findall(message.content)
				if len(match) == 0:
					return
				match = match[0]
				command = match[1].lower()
				message.content = match[0].lower()+command+match[2]
				if command not in self.commands:
					return
				if message.channel.is_private:
					if command in self.commands and self.commands[command].no_pm:
						pm_only = True
				if pm_only is False:
					cmd = str(self.commands[command])
					command_blacklisted = await self.command_check(message, cmd, prefix)
					if command_blacklisted:
						return
				try:
					await self.send_typing(message.channel)
				except:
					pass
				if message.author != self.owner and str(command) not in ('chan', 'ping', 'markov'):
					utc = int(time.time())
					command_spam = self.globals.command_spam
					if message.channel in command_spam:
						if command_spam[message.channel][1].count(command) >= 8:
							command_time = command_spam[message.channel][0][-1]
							command_sec = int(command_time) - int(utc)
							if utc >= command_time or command_sec == 0:
								del command_spam[message.channel]
							else:
								index = command_spam[message.channel][1].index(command)
								spam_command = command_spam[message.channel][1][index]
								spam_sent = self.globals.spam_sent
								if message.channel in spam_sent:
									sent_time = spam_sent[message.channel]
									sent_sec = int(sent_time) - int(utc)
									if utc >= sent_time or sent_sec == 0:
										del spam_sent[message.channel]
									else:
										return
								spam_sent[message.channel] = utc+4
								try:
									await self.send_message(message.channel, 'stop spamming `{0}`'.format(spam_command))
								except:
									return
								return
						else:
							command_spam[message.channel][0].append(utc+4)
							command_spam[message.channel][1].append(command)
					else:
						command_spam[message.channel] = {0: [utc+4], 1: [command]}
				await self.process_commands(message, command, prefix)
				self.command_messages[message] = [command, prefix]

	async def on_command(self, command, ctx):
		embed = discord.Embed()
		embed.title = '**{0}**'.format(command.name)
		embed.description = 'Shard ID: **{0}**'.format(self.shard_id)
		embed.set_author(name='{0} <{0.id}>'.format(ctx.message.author), icon_url=ctx.message.author.avatar_url)
		embed.add_field(name='Server', value='{0.name} <{0.id}>'.format(ctx.message.server) if ctx.message.server else 'Private Message')
		embed.add_field(name='Channel', value='`{0.name}`'.format(ctx.message.channel))
		embed.add_field(name='Message', value=ctx.message.clean_content+' '.join([x['url'] for x in ctx.message.attachments]), inline=False)
		embed.color = self.funcs.get_color()()
		embed.timestamp = ctx.message.timestamp
		await self.queue_message("178313681786896384", embed)
		if ctx.message.author.id == self.owner.id:
			ctx.command.reset_cooldown(ctx)

	async def on_error(self, event, *args, **kwargs):
		prRed("Error!")
		Current_Time = datetime.datetime.utcnow().strftime("%b/%d/%Y %H:%M:%S UTC")
		prGreen(Current_Time)
		prRed(traceback.format_exc())
		wrapper = textwrap.TextWrapper(initial_indent='! ', subsequent_indent='- ')
		fmt = wrapper.fill(str(traceback.format_exc()))
		await self.queue_message("180073721048989696", diff.format(fmt))

	async def on_command_error(self, e, ctx):
		try:
			if isinstance(e, commands.CommandOnCooldown):
				utc = int(time.time())
				cooldown_sent = self.globals.cooldown_sent
				if ctx.message.channel in cooldown_sent:
					sent_time = cooldown_sent[ctx.message.channel]
					sent_sec = int(sent_time) - int(utc)
					if utc >= sent_time or sent_sec == 0:
						del cooldown_sent[ctx.message.channel]
					else:
						return
				else:
					cooldown_sent[ctx.message.channel] = utc+5
					await self.send_message(ctx.message.channel, ":no_entry: **Cooldown** `Cannot use again for another {:.2f} seconds.`".format(e.retry_after))
			elif isinstance(e, commands.MissingRequiredArgument):
				await self.command_help(ctx)
				ctx.command.reset_cooldown(ctx)
			elif isinstance(e, commands.BadArgument):
				await self.command_help(ctx)
				ctx.command.reset_cooldown(ctx)
			elif isinstance(e, checks.No_Perms):
				await self.send_message(ctx.message.channel, ":no_entry: `No Permission`")
			elif isinstance(e, checks.No_Owner):
				await self.send_message(ctx.message.channel, ":no_entry: `Bot Owner Only`")
			elif isinstance(e, checks.No_Mod):
				await self.send_message(ctx.message.channel, ":no_entry: `Moderator or Above Only`")
			elif isinstance(e, checks.No_Admin):
				await self.send_message(ctx.message.channel, ":no_entry: `Administrator Only`")
			elif isinstance(e, checks.No_Role):
				await self.send_message(ctx.message.channel, ":no_entry: `No Custom Role or Specific Permission`")
			elif isinstance(e, checks.No_Sup):
				await self.send_message(ctx.message.channel, ":no_entry: `Command only for \"Superior Servers Staff\" Server")
			elif isinstance(e, checks.No_ServerandPerm):
				await self.send_message(ctx.message.channel, ":no_entry: `Server specific command or no permission`")
			elif isinstance(e, checks.Nsfw):
				await self.send_message(ctx.message.channel, ":underage: `NSFW command, please add [nsfw] in your channel topic or move to a channel named nsfw!`")
			elif isinstance(e, commands.CheckFailure):
				await self.send_message(ctx.message.channel, ":warning: **Command check failed**\nCauses:\n `1.` Bot is missing `Administrator/Manage_roles` permission.\n `2.` You do not have proper permissions to run the command.\n `3.` The command is not to be used in PM's.")
			elif isinstance(e, commands.CommandInvokeError):
				if 'Forbidden' in str(e):
					await self.send_message(ctx.message.channel, ":warning: "+code.format(str(e)))
				elif 'NotFound' in str(e):
					pass
				elif 'HTTPException' in str(e):
					if 'status code: 400' in str(e):
						try:
							if not ctx.message:
								return
							await self.truncate(ctx.message.content, ctx.message.channel)
						except:
							pass
					elif 'status code: 413' in str(e):
						try:
							await self.send_message(ctx.message.channel, ':warning: `Command failed to upload file: too large (>= 10 MB).`')
						except:
							pass
				else:
					tb = traceback.format_exception(type(e), e.__cause__, e.__cause__.__traceback__)
					embed = discord.Embed()
					embed.title = '**__Command Error__**'
					embed.description = 'Shard: **{0}**'.format(self.shard_id)
					embed.add_field(name='Command', value='{0}'.format(ctx.command.name))
					embed.add_field(name='Message', value=ctx.message.clean_content, inline=False)
					embed.add_field(name='Server', value='{0.name} <{0.id}>'.format(ctx.message.server) if ctx.message.server else 'Private Message')
					embed.add_field(name='Type', value='__{0}__'.format(type(e)))
					embed.add_field(name='File', value=str(e.__traceback__.tb_frame.f_code.co_filename)+'\nLine: **{0}**'.format(e.__traceback__.tb_lineno), inline=False)
					embed.add_field(name='Traceback', value=code.format(''.join(tb)), inline=False)
					embed.set_author(name='{0} <{0.id}>'.format(ctx.message.author), icon_url=ctx.message.author.avatar_url)
					embed.color = discord.Color.red()
					embed.timestamp = datetime.datetime.now()
					await self.queue_message("180073721048989696", embed)
			elif type(e).__name__ == 'NoPrivateMessage':
				try:
					await self.send_message(ctx.message.channel, ':warning: `Command disabled in Private Messaging.`')
				except:
					pass
			elif self.globals.command_errors == True and isinstance(e, commands.CommandNotFound):
				await self.send_message(ctx.message.channel, ":warning: Command `{0}` Not Found!".format(ctx.command.name))
			else:
				if isinstance(e, commands.CommandNotFound):
					return
		except Exception as e:
			print(e)

	async def on_server_join(self, server):
		await self.wait_until_ready()
		embed = discord.Embed()
		embed.title = 'SERVER JOIN'
		embed.description = 'Shard ID: **{0}**'.format(self.shard_id)
		embed.set_author(name='{0} <{0.id}>'.format(server.owner), icon_url=server.owner.avatar_url)
		embed.add_field(name='Server', value='{0.name} <{0.id}>'.format(server))
		embed.add_field(name='Members', value='**{0}**/{1}'.format(sum(1 for x in server.members if x.status == discord.Status.online or x.status == discord.Status.idle), len(server.members)))
		embed.add_field(name='Default Channel', value=server.default_channel)
		embed.add_field(name='Channels', value='Text: `{0}`\nVoice: `{1}`\nTotal: **{2}**'.format(sum(1 for x in server.channels if x.type == discord.ChannelType.text), sum(1 for x in server.channels if x.type == discord.ChannelType.voice), len(server.channels)))
		embed.color = discord.Color.green()
		embed.timestamp = datetime.datetime.now()
		await self.queue_message('211247117816168449', embed)

	async def on_server_remove(self, server):
		await self.wait_until_ready()
		sql = "DELETE FROM `prefix_channel` WHERE server={0}".format(server.id)
		cursor.execute(sql)
		sql = "DELETE FROM `prefix` WHERE server={0}".format(server.id)
		cursor.execute(sql)
		cursor.commit()
		embed = discord.Embed()
		embed.title = 'SERVER LEAVE'
		embed.description = 'Shard ID: **{0}**'.format(self.shard_id)
		embed.set_author(name='{0} <{0.id}>'.format(server.owner), icon_url=server.owner.avatar_url)
		embed.add_field(name='Server', value='{0.name} <{0.id}>'.format(server))
		embed.add_field(name='Members', value='**{0}**/{1}'.format(sum(1 for x in server.members if x.status == discord.Status.online or x.status == discord.Status.idle), len(server.members)))
		embed.color = discord.Color.red()
		embed.timestamp = datetime.datetime.now()
		await self.queue_message('211247117816168449', embed)

	async def on_resumed(self):
		last_time = self.get_last_time()
		time_msg = time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(last_time))
		current_time_msg = time.strftime('%m/%d/%Y %H:%M:%S')
		utc = int(time.time())
		if last_time is None:
			downtime = 0
		else:
			downtime = str(utc - last_time)
		msg = '`[Shard {0}]` {1} has now <@&211727010932719627> after being <@&211727098149076995> since **{2}** for **{3}** second(s) (Current Time: **{4}**)'.format(self.shard_id, self.user.mention, time_msg, downtime, current_time_msg)
		await self.queue_message('211247117816168449', msg)

	async def send_message(self, destination, content=None, *, tts=False, embed=None, replace_mentions=False, replace_everyone=True):
		if content:
			content = str(content)
			if replace_everyone:
				content = content.replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
			if replace_mentions:
				content = await self.funcs.replace_mentions(content)
		return await super().send_message(destination, content, tts=tts, embed=embed)

	def get_member(self, id:str):
		return discord.utils.get(self.get_all_members(), id=id)

	def run(self):
		super().run(self.token)

	async def login(self, *args, **kwargs):
		return await super().login(self.token, bot=False if self.self_bot else True)

	def die(self):
		try:
			self.loop.stop()
			cursor.close_all()
			engine.dispose()
			tasks = asyncio.gather(*asyncio.Task.all_tasks(), loop=self.loop)
			tasks.cancel()
			self.loop.run_forever()
			tasks.exception()
			for handler in self.log.handlers[:]:
				handler.close()
				self.log.removeHandler(handler)
		except Exception as e:
			print(e)

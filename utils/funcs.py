import asyncio, aiohttp, aiosocks, discord
import os, sys, linecache, async_timeout, inspect, traceback
import re, math, random, uuid, time, jsonpickle
from pymysql.converters import escape_item, escape_string, encoders
from contextlib import redirect_stdout
from discord.ext import commands
from discord.ext.commands.errors import CommandNotFound, CommandError
from discord.ext.commands.context import Context
from concurrent.futures import CancelledError, TimeoutError
from io import BytesIO, StringIO

encoders[ord(':')] = '\:'

class DataProtocol(asyncio.SubprocessProtocol):
	def __init__(self, exit_future):
		self.exit_future = exit_future
		self.output = bytearray()

	def pipe_data_received(self, fd, data):
		self.output.extend(data)

	def process_exited(self):
		try:
			self.exit_future.set_result(True)
		except:
			pass

	def pipe_connection_lost(self, fd, exc):
		try:
			self.exit_future.set_result(True)
		except:
			pass
	def connection_made(self, transport):
		self.transport = transport

	def connection_lost(self, exc):
		try:
			self.exit_future.set_result(True)
		except:
			pass

class Funcs():
	def __init__(self, bot, cursor):
		self.bot = bot
		self.cursor = cursor
		self.bot.google_api_keys = open(self.discord_path('utils/keys.txt')).read().split('\n')
		self.bot.google_count = 0
		self.image_mimes = ['image/png', 'image/pjpeg', 'image/jpeg', 'image/x-icon']
		self.session = aiohttp.ClientSession()
		self.mention_regex = re.compile(r"<@!?(?P<id>\d+)>")
		self.colors = ['red', 'blue', 'green', 'gold', 'dark_blue', 'dark_gold', 'dark_green', 'dark_grey', 'dark_magenta', 'dark_orange', 'dark_purple', 'dark_red', 'dark_teal', 'darker_grey', 'default', 'light_grey', 'lighter_grey', 'magenta', 'orange', 'purple', 'teal']
		self.color_count = 0

	def discord_path(self, path):
		return os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), path)

	def files_path(self, path):
		return self.discord_path('files/'+path)

	async def prefix_check(self, s, prefix, prefix_set):
		if prefix_set:
			return True
		count = 0
		for x in s:
			if count == 2:
				break
			elif count == 1:
				if x != prefix:
					break
			if x == prefix:
				count += 1
		if count == 1:
			return True
		return False

	async def get_prefix(self, message):
		if self.bot.dev_mode:
			prefix = ','
		elif self.bot.self_bot:
			prefix = 'self.'
		else:
			prefix = '.'
		prefix_set = False
		if message.channel.is_private is False and message.content.startswith(prefix+"prefix") is False:
			sql = "SELECT prefix FROM `prefix` WHERE server={0}"
			sql = sql.format(message.server.id)
			sql_channel = "SELECT prefix,channel FROM `prefix_channel` WHERE server={0} AND channel={1}"
			sql_channel = sql_channel.format(message.server.id, message.channel.id)
			result = self.cursor.execute(sql_channel).fetchall()
			if result:
				for s in result:
					if s['channel'] == message.channel.id:
						prefix = s['prefix']
						prefix_set = True
						break
			elif not prefix_set:
				result = self.cursor.execute(sql).fetchall()
				if len(result) != 0:
					prefix = result[0]['prefix']
					prefix_set = True
			if prefix_set:
				prefix = prefix.lower()
		mention = commands.bot.when_mentioned(self.bot, message)
		if message.content.startswith(mention):
			check = True
		else:
			check = await self.prefix_check(message.content, prefix, prefix_set)
		return [prefix, mention], check

	async def is_blacklisted(self, message):
		try:
			perms = message.channel.permissions_for(message.server.me)
			if perms.send_messages is False or perms.read_messages is False:
				return True
		except:
			pass
		if message.author.id == self.bot.owner.id:
			return False
		global_blacklist_result = self.cursor.execute('SELECT * FROM `global_blacklist` WHERE user={0}'.format(message.author.id)).fetchall()
		if message.channel.is_private:
			if len(global_blacklist_result) != 0 and message.author.id != bot.owner.id:
				return True
			return False
		muted_check_result = self.cursor.execute('SELECT * FROM `muted` WHERE server={0} AND id={1}'.format(message.server.id, message.author.id)).fetchall()
		if len(muted_check_result) != 0 and message.server.owner != message.author:
			return True
		server_blacklist_result = self.cursor.execute('SELECT * FROM `blacklist` WHERE server={0} AND user={1}'.format(message.server.id, message.author.id)).fetchall()
		channel_blacklist_result = self.cursor.execute('SELECT * FROM `channel_blacklist` WHERE server={0} AND channel={1}'.format(message.server.id, message.channel.id)).fetchall()
		if len(global_blacklist_result) != 0:
			return True
		elif len(server_blacklist_result) != 0:
			return True
		elif len(channel_blacklist_result) != 0:
			if 'blacklist' in message.content:
				return False
			return True
		return False

	async def command_check(self, message, command, prefix='.'):
		if message.author.id == self.bot.owner.id:
			return False
		sql = 'SELECT * FROM `command_blacklist` WHERE type="global" AND command={0}'
		sql = sql.format(self.escape(command))
		result = self.cursor.execute(sql).fetchall()
		if len(result) != 0:
			return True
		if message.channel.is_private:
			return False
		sql = 'SELECT * FROM `command_blacklist` WHERE server={0}'
		sql = sql.format(message.server.id)
		result = self.cursor.execute(sql).fetchall()
		topic_match = None
		if message.channel.topic:
			command_escape = re.escape(command)
			topic_regex = re.compile(r"((\[|\{)(\+|\-)?"+command_escape+r"(\]|\}))", re.I|re.S)
			match = topic_regex.findall(message.channel.topic.lower())
			if match:
				if match[0][2] == '+' or not len(match[0][2]):
					topic_match = False
				elif match[0][2] == '-':
					topic_match = True
		is_admin = False
		try:
			perms = message.channel.permissions_for(message.author)
			if perms.administrator or perms.manage_server or perms.manage_roles:
				is_admin = True
		except:
			pass
		if topic_match:
			await self.bot.send_message(message.channel, ':no_entry: **That command is disabled in this channel.**{0}'.format('\nRemove `[-{1}]` from the channel description to enable the command.' if is_admin else ''))
			return True
		for s in result:
			if s['command'] != command:
				continue
			if s['type'] == 'server':
				if topic_match is False:
					return False
				await self.bot.send_message(message.channel, ':no_entry: **That command is disabled on this server.**{0}'.format("\n`{0}command enable {1}` to enable the command.\n**Alternatively** place `[{1}]` in the channel topic or name.".format(prefix, command) if is_admin else ''))
				return True
			elif s['type'] == 'channel':
				if str(s['channel']) == str(message.channel.id):
					await self.bot.send_message(message.channel, ':no_entry: **That command is disabled in this channel.**{0}'.format("\n`{0}command enable channel {1}` {2} to enable the command".format(prefix, command, message.channel.mention) if is_admin else ''))
					return True
			elif s['type'] == 'role':
				for role in message.author.roles:
					if str(role.id) == str(s['role']):
						await self.bot.send_message(message.channel, ':no_entry: **That command is disabled for role: {1}**{0}'.format("\n`{0}command enable channel {1}` {2} to enable the command.".format(prefix, command, role.mention) if is_admin else ''), role.mention)
						return True
			elif s['type'] == 'user':
				if str(s['user']) == str(message.author.id):
					return True
		return False

	async def process_commands(self, message, c, p):
		_internal_channel = message.channel
		_internal_author = message.author
		view = commands.view.StringView(message.content)
		prefix = p
		invoked_prefix = prefix
		if not isinstance(p, (tuple, list)):
			if not view.skip_string(p):
				return
		else:
			invoked_prefix = discord.utils.find(view.skip_string, prefix)
		if invoked_prefix is None:
			return
		invoker = view.get_word()
		tmp = {
			'bot': self.bot,
			'invoked_with': invoker,
			'message': message,
			'view': view,
			'prefix': invoked_prefix
		}
		ctx = Context(**tmp)
		del tmp
		if c in self.bot.commands:
			command = self.bot.commands[c]
			self.bot.dispatch('command', command, ctx)
			# import pdb; pdb.set_trace()
			try:
				if command in (self.bot.commands['repl'], self.bot.commands['debug']):
					await command.invoke(ctx)
				else:
					with async_timeout.timeout(60):
						await command.invoke(ctx)
			except (aiohttp.errors.TimeoutError, asyncio.TimeoutError, CancelledError, TimeoutError):
				try:
					await self.bot.send_message(message.channel, ':warning: **Command timed out...**')
					return
				except:
					return
			except CommandError as e:
				ctx.command.dispatch_error(e, ctx)
			else:
				self.bot.dispatch('command_completion', command, ctx)
		elif invoker:
			exc = commands.errors.CommandNotFound('Command "{0}" is not found'.format(invoker))
			self.bot.dispatch('command_error', exc, ctx)

	async def queue_message(self, channel_id:str, msg):
		embed = '0'
		if type(msg) == discord.Embed:
			embed = '1'
			msg = jsonpickle.encode(msg)
		else:
			msg = str(msg)
		message_id = random.randint(0, 1000000)
		payload = {'key': 'verysecretkey', 'id': message_id, 'channel_id': channel_id, 'message': msg, 'embed': embed}
		try:
			with aiohttp.Timeout(15):
				async with self.session.post('http://ip:port/queue', data=payload) as r:
					return True
		except (asyncio.TimeoutError, aiohttp.errors.ClientConnectionError, aiohttp.errors.ClientError):
			await asyncio.sleep(5)
			return
		except Exception as e:
			print('queue error: '+str(e))

	async def isimage(self, url:str):
		try:
			with aiohttp.Timeout(5):
				async with self.session.head(url) as resp:
					if resp.status == 200:
						mime = resp.headers.get('Content-type', '').lower()
						if any([mime == x for x in self.image_mimes]):
							return True
						else:
							return False
		except:
			return False

	async def isgif(self, url:str):
		try:
			with aiohttp.Timeout(5):
				async with self.session.head(url) as resp:
					if resp.status == 200:
						mime = resp.headers.get('Content-type', '').lower()
						if mime == "image/gif":
							return True
						else:
							return False
		except:
			return False

	async def download(self, url:str, path:str):
		try:
			with aiohttp.Timeout(5):
				async with self.session.get(url) as resp:
					data = await resp.read()
					with open(path, "wb") as f:
						f.write(data)
		except asyncio.TimeoutError:
			return False

	async def bytes_download(self, url:str):
		try:
			with aiohttp.Timeout(5):
				async with self.session.get(url) as resp:
					data = await resp.read()
					b = BytesIO(data)
					b.seek(0)
					return b
		except asyncio.TimeoutError:
			return False
		except Exception as e:
			print(e)
			return False

	async def get_json(self, url:str):
		try:
			with aiohttp.Timeout(5):
				async with self.session.get(url) as resp:
					try:
						load = await resp.json()
						return load
					except:
						return {}
		except asyncio.TimeoutError:
			return {}

	async def get_text(self, url:str):
		try:
			with aiohttp.Timeout(5):
				async with self.session.get(url) as resp:
					try:
						text = await resp.text()
						return text
					except:
						return False
		except asyncio.TimeoutError:
			return False

	async def run_process(self, code, response=False):
		try:
			loop = self.bot.loop
			exit_future = asyncio.Future(loop=loop)
			create = loop.subprocess_exec(lambda: DataProtocol(exit_future),
																		*code, stdin=None, stderr=None)
			transport, protocol = await asyncio.wait_for(create, timeout=30)
			await exit_future
			if response:
				data = bytes(protocol.output)
				return data.decode('ascii').rstrip()
			return True
		except asyncio.TimeoutError:
			return False
		except Exception as e:
			print(e)
		finally:
			transport.close()

	async def proxy_request(self, url, **kwargs):
		post = kwargs.get('post')
		post = True if post != {} else False
		post_data = kwargs.get('post_data')
		headers = kwargs.get('headers')
		j = kwargs.get('j')
		j = True if j != {} else False
		proxy_addr = aiosocks.Socks5Addr('', 1080)
		proxy_auth = aiosocks.Socks5Auth('', password='')
		proxy_connection = aiosocks.connector.SocksConnector(proxy=proxy_addr, proxy_auth=proxy_auth, remote_resolve=True)
		with aiohttp.ClientSession(connector=proxy_connection) as session:
			async with session.post(url, data=post_data if post else None, headers=headers) as resp:
				if j:
					return await resp.json()
				else:
					return await resp.text()

	async def truncate(self, channel, msg):
		if len(msg) == 0:
			return
		split = [msg[i:i + 1999] for i in range(0, len(msg), 1999)]
		try:
			for s in split:
				await self.bot.send_message(channel, s)
				await asyncio.sleep(0.21)
		except Exception as e:
			await self.bot.send_message(channel, e)

	async def get_attachment_images(self, ctx, check_func):
		last_attachment = None
		img_urls = []
		async for m in self.bot.logs_from(ctx.message.channel, before=ctx.message, limit=25):
			check = False
			if m.attachments:
				last_attachment = m.attachments[0]['url']
				check = await check_func(last_attachment)
			elif m.embeds:
				last_attachment = m.embeds[0]['url']
				check = await check_func(last_attachment)
			if check:
				img_urls.append(last_attachment)
				break
		return img_urls

	async def get_images(self, ctx, **kwargs):
		try:
			message = ctx.message
			channel = ctx.message.channel
			attachments = ctx.message.attachments
			mentions = ctx.message.mentions
			limit = kwargs.pop('limit', 8)
			urls = kwargs.pop('urls', [])
			gif = kwargs.pop('gif', False)
			msg = kwargs.pop('msg', True)
			if gif:
				check_func = self.isgif
			else:
				check_func = self.isimage
			if urls is None:
				urls = []
			elif type(urls) != tuple:
				urls = [urls]
			else:
				urls = list(urls)
			scale = kwargs.pop('scale', None)
			scale_msg = None
			int_scale = None
			if gif is False:
				for user in mentions:
					if user.avatar:
						urls.append('https://discordapp.com/api/users/{0.id}/avatars/{0.avatar}.jpg'.format(user))
					else:
						urls.append(user.default_avatar_url)
					limit += 1
			for attachment in attachments:
				urls.append(attachment['url'])
			if scale:
				scale_limit = scale
				limit += 1
			if urls and len(urls) > limit:
				await self.bot.send_message(channel, ':no_entry: `Max image limit (<= {0})`'.format(limit))
				ctx.command.reset_cooldown(ctx)
				return False
			img_urls = []
			count = 1
			for url in urls:
				user = None
				if url.startswith('<@'):
					continue
				if not url.startswith('http'):
					url = 'http://'+url
				try:
					if scale:
						s_url = url[8:] if url.startswith('https://') else url[7:]
						if str(math.floor(float(s_url))).isdigit():
							int_scale = int(math.floor(float(s_url)))
							scale_msg = '`Scale: {0}`\n'.format(int_scale)
							if int_scale > scale_limit and ctx.message.author.id != self.bot.owner.id:
								int_scale = scale_limit
								scale_msg = '`Scale: {0} (Limit: <= {1})`\n'.format(int_scale, scale_limit)
							continue
				except Exception as e:
					pass
				check = await check_func(url)
				if check is False and gif is False:
					check = await self.isgif(url)
					if check:
						if msg:
							await self.bot.send_message(channel, ":warning: This command is for images, not gifs (use `gmagik` or `gascii`)!")
						ctx.command.reset_cooldown(ctx)
						return False
					elif len(img_urls) == 0:
						name = url[8:] if url.startswith('https://') else url[7:]
						member = self.find_member(message.server, name, 2)
						if member:
							img_urls.append('https://discordapp.com/api/users/{0.id}/avatars/{0.avatar}.jpg'.format(member) if member.avatar else member.default_avatar_url)
							count += 1
							continue
						if msg:
							await self.bot.send_message(channel, ':warning: Unable to download or verify URL is valid.')
						ctx.command.reset_cooldown(ctx)
						return False
					else:
						if msg:
							await self.bot.send_message(channel, ':warning: Image `{0}` is Invalid!'.format(count))
						continue
				elif gif and check is False:
					check = await self.isimage(url)
					if check:
						if msg:
							await self.bot.send_message(channel, ":warning: This command is for gifs, not images (use `magik`)!")
						ctx.command.reset_cooldown(ctx)
						return False
					elif len(img_urls) == 0:
						name = url[8:] if url.startswith('https://') else url[7:]
						member = self.find_member(message.server, name, 2)
						if member:
							img_urls.append('https://discordapp.com/api/users/{0.id}/avatars/{0.avatar}.jpg'.format(member) if member.avatar else member.default_avatar_url)
							count += 1
							continue
						if msg:
							await self.bot.send_message(channel, ':warning: Unable to download or verify URL is valid.')
						ctx.command.reset_cooldown(ctx)
						return False
					else:
						if msg:
							await self.bot.send_message(channel, ':warning: Gif `{0}` is Invalid!'.format(count))
						continue
				img_urls.append(url)
				count += 1
			else:
				if len(img_urls) == 0:
					attachment_images = await self.get_attachment_images(ctx, check_func)
					if attachment_images:
						img_urls.extend([*attachment_images])
					else:
						if msg:
							await self.bot.send_message(channel, ":no_entry: Please input url(s){0}or attachment(s).".format(', mention(s) ' if not gif else ' '))
						ctx.command.reset_cooldown(ctx)
						return False
			if scale:
				if len(img_urls) == 0:
					attachment_images = await self.get_attachment_images(ctx, check_func)
					if attachment_images:
						img_urls.extend([*attachment_images])
					else:
						if msg:
							await self.bot.send_message(channel, ":no_entry: Please input url(s){0}or attachment(s).".format(', mention(s) ' if not gif else ' '))
						ctx.command.reset_cooldown(ctx)
						return False
				return img_urls, int_scale, scale_msg
			if img_urls:
				return img_urls
			return False
		except Exception as e:
			print(e)

	async def google_keys(self):
		keys = self.bot.google_api_keys
		if self.bot.google_count >= len(keys):
			self.bot.google_count = 0
		key = keys[self.bot.google_count]
		self.bot.google_count += 1
		return str(key)

	def write_last_time(self):
		path = self.files_path('last_time_{0}{1}.txt'.format(self.bot.shard_id, '_self' if self.bot.self_bot else ''))
		utc = str(int(time.time()))
		with open(path, 'wb') as f:
			f.write(utc.encode())
			f.close()

	def get_last_time(self):
		path = self.files_path('last_time_{0}{1}.txt'.format(self.bot.shard_id, '_self' if self.bot.self_bot else ''))
		try:
			return int(open(path, 'r').read())
		except:
			return False

	def restart_program(self):
		python = sys.executable
		os.execl(python, python, * sys.argv)

	async def cleanup_code(self, content):
		"""Automatically removes code blocks from the code."""
		if content.startswith('```') and content.endswith('```'):
			clean = '\n'.join(content.split('\n')[1:-1])
		else:
			clean = content.strip('` \n')
		if clean.startswith('http'):
			async with self.session.get(clean) as r:
				clean = await r.text()
		return clean

	def get_syntax_error(self, e):
		return '```py\n{0.text}{1:>{0.offset}}\n{2}: {0}```'.format(e, '^', type(e).__name__)

	async def repl(self, ctx, code):
		msg = ctx.message
		variables = {
				'ctx': ctx,
				'bot': ctx.bot,
				'message': msg,
				'server': msg.server,
				'channel': msg.channel,
				'author': msg.author,
				'last': None,
				'commands': commands,
				'discord': discord,
				'asyncio': asyncio,
				'cursor': self.cursor
		}
		cleaned = await self.cleanup_code(code)
		if cleaned in ('quit', 'exit', 'exit()'):
			await self.bot.say('Exiting.')
			return 'exit'
		executor = exec
		if cleaned.count('\n') == 0:
			try:
				code = compile(cleaned, '<repl session>', 'eval')
			except SyntaxError:
				pass
			else:
				executor = eval
		if executor is exec:
			try:
				code = compile(cleaned, '<repl session>', 'exec')
			except SyntaxError as e:
				await self.bot.say(self.get_syntax_error(e))
				return False
		fmt = None
		stdout = StringIO()
		try:
			with redirect_stdout(stdout):
				result = executor(code, variables)
				if inspect.isawaitable(result):
					result = await result
		except Exception as e:
			value = stdout.getvalue()
			fmt = '```py\n{}{}\n```'.format(value, traceback.format_exc())
		else:
			value = stdout.getvalue()
			if result is not None:
				fmt = '```py\n{}{}\n```'.format(value, result)
				variables['last'] = result
			elif value:
				fmt = '```py\n{}\n```'.format(value)
		return fmt

	async def command_help(self, ctx):
		if ctx.invoked_subcommand:
			cmd = ctx.invoked_subcommand
		else:
			cmd = ctx.command
		pages = self.bot.formatter.format_help_for(ctx, cmd)
		for page in pages:
			await self.bot.send_message(ctx.message.channel, page.replace("\n", "fix\n", 1))

	def escape(self, obj, mapping=encoders):
		if isinstance(obj, str):
			return "'" + escape_string(obj) + "'"
		return escape_item(obj, 'utf8mb4', mapping=mapping)

	async def replace_mentions(self, txt:str):
		match = self.mention_regex.findall(txt)
		if match:
			for i in match:
				user = discord.utils.get(self.bot.get_all_members(), id=str(i))
				if user is None:
					user = await self.bot.get_user_info(i)
				txt = re.sub(re.compile('(<@\!?{0}>)'.format(user.id)), '@{0}'.format(user), txt)
		return txt

	def find_member(self, server, name, steps=2):
		member = None
		match = self.mention_regex.search(name)
		if match:
			member = server.get_member(match.group('id'))
		if not member:
			name = name.lower()
			checks = [lambda m: m.name.lower() == name or m.display_name.lower() == name, lambda m: m.name.lower().startswith(name) or m.display_name.lower().startswith(name) or m.id == name, lambda m: name in m.display_name.lower() or name in m.name.lower()]
			for i in range(steps if steps <= len(checks) else len(checks)):
				if i == 3:
					member = discord.utils.find(checks[1], self.bot.get_all_members())
				else:
					member = discord.utils.find(checks[i], server.members)
				if member:
					break
		return member

	def random(self, image=False, ext:str=False):
		h = str(uuid.uuid4().hex)
		if image:
			return '{0}.{1}'.format(h, ext) if ext else h+'.png'
		return h

	async def is_nsfw(self, message):
		channel = message.channel
		if channel.is_private:
			return True
		name = channel.name.lower()
		if name == 'nsfw' or name == '[nsfw]':
			return True
		elif name == 'no-nsfw' or name == 'sfw':
			return False
		split = name.split()
		if 'nsfw' in name:
			try:
				i = split.index('nsfw')
			except:
				i = None
			if len(split) > 1 and i != None and split[i-1] != 'no':
				return True
			elif i is None:
				split = name.split('-')
				try:
					i = split.index('nsfw')
				except:
					i = None
				if len(split) > 1 and i != None and split[i-1] != 'no':
					return True
		if channel.topic != None:
			topic = channel.topic.lower()
			split = topic.split()
			if '{nsfw}' in topic or '[nsfw]' in topic or topic == 'nsfw':
				return True
			elif 'nsfw' in topic and 'sfw' not in split:
				try:
					i = split.index('nsfw')
				except:
					i = None
				if len(split) > 1 and i != None and split[i-1] != 'no':
					return True
				elif i is None:
					split = topic.split('-')
					try:
						i = split.index('nsfw')
					except:
						i = None
					if len(split) > 1 and i != None and split[i-1] != 'no':
						return True
		return False

	def get_color(self):
		if self.color_count >= len(self.colors):
			self.color_count = 0
		color = self.colors[self.color_count]
		self.color_count += 1
		return getattr(discord.Color, color)

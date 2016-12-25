import asyncio, discord, aiohttp
import os, sys, traceback
import re, json, io, copy, random, hashlib
import time, pytz 
import textblob, tabulate
from discord.ext import commands
from sys import argv, path
from io import BytesIO
from utils import checks
from mods.cog import Cog

cool = "```xl\n{0}\n```"
code = "```py\n{0}\n```"
#hard coded color roles cause I don't want to rewrite this and deal with discord roles, lul

class Utils(Cog):
	def __init__(self, bot):
		super().__init__(bot)
		self.cursor = bot.mysql.cursor
		self.discord_path = bot.path.discord
		self.files_path = bot.path.files
		self.download = bot.download
		self.bytes_download = bot.bytes_download
		self.get_json = bot.get_json
		self.truncate = bot.truncate
		self.ping_responses = ['redacted']
		self.ping_count = random.randint(0, len(self.ping_responses)-1)
		self.color_roles = ['red', 'green', 'blue', 'purple', 'orange', 'black', 'white', 'cyan', 'lime', 'pink', 'yellow', 'lightred', 'lavender', 'salmon', 'darkblue', 'darkpurple']

	@commands.command(pass_context=True)
	@commands.cooldown(1, 10)
	async def status(self, ctx, *, status:str):
		"""changes bots status"""
		await self.bot.change_presence(game=discord.Game(name=status))
		await self.bot.say("ok, status changed to ``" + status + "``")

	@commands.command(pass_context=True)
	@checks.is_owner()
	async def say(self, ctx, *, text:str):
		"""have me say something (owner only cuz exploits)???"""
		await self.bot.say(text)

	@commands.command(pass_context=True, hidden=True)
	@checks.is_owner()
	async def debug(self, ctx, *, code : str):
		code = code.strip('` ')
		python = '```py\n{}\n```'
		result = None
		variables = {
			'bot': self.bot,
			'ctx': ctx,
			'message': ctx.message,
			'server': ctx.message.server,
			'channel': ctx.message.channel,
			'author': ctx.message.author,
			'cursor': self.cursor
		}
		env.update(globals())
		try:
			result = eval(code, variables)
		except Exception as e:
			await self.bot.say(python.format(type(e).__name__ + ': ' + str(e)))
			return
		if asyncio.iscoroutine(result):
			result = await result
		await self.bot.say(python.format(result))

	@commands.command(pass_context=True)
	@checks.is_owner()
	async def load(self, ctx, *, module:str):
		mod = "mods.{0}".format(module)
		msg = await self.bot.say("ok, loading `{0}`".format(mod))
		try:
			ctx.bot.load_extension(mod)
		except ImportError:
			await self.bot.say(':warning: Module does not exist.')
			return
		except Exception as e:
			await self.bot.say(code.format(e))
			return
		else:
			await self.bot.edit_message(msg, "ok, loaded `{0}`".format(mod))

	@commands.command(pass_context=True)
	@checks.is_owner()
	async def unload(self, *, module:str):
		mod = "mods.{0}".format(module)
		if module in self.bot.cogs.keys():
			msg = await self.bot.say("ok, unloading `{0}`".format(mod))
			ctx.bot.unload_extension(mod)
			await self.bot.edit_message(msg, "ok, unloaded `{0}`".format(mod))
		else:
			await self.bot.say(':warning: Module does not exist.')

	@commands.group(pass_context=True, invoke_without_command=True)
	@checks.is_owner()
	async def reload(self, ctx, *, module:str):
		mod = "mods.{0}".format(module)
		msg = await self.bot.say("ok, reloading `{0}`".format(mod))
		try:
			ctx.bot.unload_extension(mod)
		except:
			await self.bot.say(':warning: Module does not exist.')
			return
		try:
			ctx.bot.load_extension(mod)
		except Exception as e:
			await self.bot.say(code.format(e))
			return
		await self.bot.edit_message(msg, "ok, reloaded `{0}`".format(module))

	@commands.command()
	@checks.is_owner()
	async def update(self):
		await self.bot.say("ok brb, killing my self")
		self.bot.funcs.restart_program()

	@commands.command()
	@checks.is_owner()
	async def die(self):
		await self.bot.say("Drinking bleach.....")
		await self.bot.logout()

	# @commands.command(pass_context=True)
	# async def evaljs(self, *, code:str):
	# 	"""eval JS code in Node.JS"""
	# 	code_clean = "{0}".format(code.strip("```"))
	# 	node = execjs.get("Node")
	# 	execute = node.eval(code_clean)
	# 	try:
	# 		result = node.eval(code_clean)
	# 		await self.bot.say(code.format(result))
	# 	except execjs.ProgramError as e:
	# 		await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

	@commands.command(pass_context=True)
	@checks.is_owner()
	async def loop(self, ctx, times:int, *, command):
		"""Loop a command a x times."""
		try:
			msg = copy.copy(ctx.message)
			msg.content = command
			for i in range(times):
				await self.bot.process_commands(msg, command.split()[0][1:], '.')
		except Exception as e:
			await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

	@commands.command(pass_context=True)
	async def ping(self, ctx):
		"""Ping the bot server."""
		try:
			ptime = time.time()
			x = await self.bot.say("ok, pinging.")
			ping = time.time() - ptime
			if self.ping_count >= len(self.ping_responses):
				self.ping_count = 0
			kek = self.ping_responses[self.ping_count]
			self.ping_count += 1
			msg = "ok, it took `{0:.01f}` seconds to ping **{1}**{2}".format(ping, kek, '\nlook how slow python is.' if ping > 1 else '.')
			rand = True if random.randint(0, 10) % 2 == 0 else False
			if rand:
				msg = u"\u202E " + msg[::-1].replace('\n', '\n\u202E')
			await self.bot.edit_message(x, msg)
		except Exception as e:
			await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

	@commands.command()
	async def speedtest(self):
		msg = await self.bot.run_process(["speedtest-cli", "--simple", "--share"], True)
		await self.bot.say(cool.format(msg.replace("", "SERVER IP").replace("\n", "\n").replace("\"", "").replace("b'", "").replace("'", "")))

	@commands.command()
	async def iping(self, *, ip:str):
		msg = await self.bot.run_process(["ping", "-c", "4", "{0}".format(ip)], True)
		await self.bot.say(cool.format(msg))

	@commands.command(pass_context=True, no_pm=True, aliases=['colour'])
	@commands.cooldown(1, 10)
	@commands.bot_has_permissions(manage_roles=True)
	async def color(self, ctx, color:str=None):
		"""Set your color!"""
		try:
			if ctx.message.server is None: return
			roles = list((map(str, ctx.message.author.roles)))
			server_roles = list((map(str, ctx.message.server.roles)))
			server_color_roles = [i for e in server_roles for i in self.color_roles if e == i]
			if len(server_color_roles) != len(self.color_roles):
				await self.bot.say(":warning: Server either does not have color roles or all the bots color roles\nAsk an Administrator to run the addcolors command\nor make sure you have all the roles in the colors command.")
				return
			if color is None:
				await self.bot.say("You didn\'t input a color, here\'s a list\n```{0}```\nUse .color <color_name>".format(", ".join(self.color_roles)))
				return
			color = color.lower()
			role = discord.utils.find(lambda r: r.name.startswith(color), list(ctx.message.server.roles))
			fix = list(set(' '.join(map(str, ctx.message.author.roles)).split(' ')) & set(self.color_roles))
			fix.append("aaa")
			erole = discord.utils.find(lambda r: r.name.startswith(fix[0]), list(ctx.message.server.roles))
			if any([color == x for x in self.color_roles]) == False and color != "none":
				await self.bot.say("You have input an invalid color, here\'s a list\n```{0}```\nUse .color <color_name>".format(", ".join(self.color_roles)))
				return
			if color != "none":
				if erole != None:
					await self.bot.remove_roles(ctx.message.author, erole)
					await asyncio.sleep(0.25)
					await self.bot.add_roles(ctx.message.author, role)
					await self.bot.say("Changing {0}'s color to `{1}`".format(ctx.message.author.mention, color))
				else:
					await asyncio.sleep(0.25)
					await self.bot.add_roles(ctx.message.author, role)
					await self.bot.say("Added color `{0}` to {1}".format(color, ctx.message.author.mention))
			elif color == "none" and any([roles == x for x in self.color_roles]):
				await asyncio.sleep(0.25)
				await self.bot.remove_roles(ctx.message.author, erole)
				await self.bot.say("Removed color from {0}".format(ctx.message.author.mention))
			else:
				if erole != None:
					await asyncio.sleep(0.25)
					await self.bot.remove_roles(ctx.message.author, erole)
					await self.bot.say("Removed color from {0}".format(ctx.message.author.mention))
				else:
					await self.bot.say("You don't have a color to remove!")
		except Exception as e:
			print(e)
			await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

	@commands.command(pass_context=True, aliases=['uncolour'])
	@commands.cooldown(1, 10)
	@commands.bot_has_permissions(manage_roles=True)
	async def uncolor(self, ctx):
		"""Removes color if set."""
		try:
			if ctx.message.server is None: return
			roles = list((map(str, ctx.message.author.roles)))
			server_roles = list((map(str, ctx.message.server.roles)))
			server_color_roles = [i for e in server_roles for i in self.color_roles if e == i]
			if len(server_color_roles) != len(self.color_roles):
				await self.bot.say(":warning: Server either does not have color roles or all the bots color roles\nAsk an Administrator to run the addcolors command\nor make sure you have all the roles in the colors command.")
				return
			fix = list(set(' '.join(map(str, ctx.message.author.roles)).split(' ')) & set(self.color_roles))
			fix.append("aaa")
			erole = discord.utils.find(lambda r: r.name.startswith(fix[0]), list(ctx.message.server.roles))
			if erole != None:
				await self.bot.remove_roles(ctx.message.author, erole)
				await self.bot.say("ok, removed color `{0}` from {1}".format(erole, ctx.message.author.mention))
			else:
				await self.bot.say("You don't have a color to remove!")
		except Exception as e:
				await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

	@commands.command(pass_context=True, aliases=['colours'])
	@commands.cooldown(1, 10)
	@commands.bot_has_permissions(manage_roles=True)
	async def colors(self, ctx):
		"""Returns color roles available to use in '.color' command."""
		if ctx.message.server is None: return
		await self.bot.say("Role Colors Available\n```{0}```\nUse .color <color_name> to set your color!".format(", ".join(self.color_roles)))

	@commands.command(pass_context=True, aliases=['addcolour'], no_pm=True)
	@commands.bot_has_permissions(manage_roles=True)
	@checks.admin_or_perm(manage_roles=True)
	async def addcolor(self, ctx, name, color:discord.Colour):
		"""Add a color role with the inputted name and Hex Color"""
		try:
				if ctx.message.server is None: return
				roles = list(map(str, ctx.message.server.roles))
				for s in roles:
					if re.search(r'^' + s + r'$', name):
						await self.bot.say("There's already a role with this name!")
						return
				await self.bot.create_role(server=ctx.message.server, permissions=permissions, name=name, color=color)
				await self.bot.say("Added role with name `{0}` and color `{1}`".format(name, color))
		except Exception as e:
				await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

	@commands.command(pass_context=True, aliases=['addcolours'], no_pm=True)
	@commands.cooldown(1, 500)
	@checks.admin_or_perm(manage_roles=True)
	async def addcolors(self, ctx):
		"""Add color roles to current server"""
		try:
			server_roles = list((map(str, ctx.message.server.roles)))
			server_color_roles = [i for e in server_roles for i in self.color_roles if e == i]
			if len(server_color_roles) == len(self.color_roles):
				await self.bot.say(":warning: Server already has the color roles!")
				return
			color = discord.Colour(int("FF0000", 16))
			color2 = discord.Colour.green()
			color3 = discord.Colour(int("9E00FF", 16))
			color4 = discord.Colour.blue()
			color5 = discord.Colour.orange()
			color6 = discord.Colour(int("0F0000", 16))
			color7 = discord.Colour(int("FFFFFF", 16))
			color8 = discord.Colour(int("08F8FC", 16))
			color9 = discord.Colour(int("00FF00", 16))
			color10 = discord.Colour(int("FF69B4", 16))
			color11 = discord.Colour(int("FBF606", 16))
			color12 = discord.Colour(int("FF4C4C", 16))
			color13 = discord.Colour(int("D1D1FF", 16))
			color14 = discord.Colour(int("FFA07A", 16))
			color15 = discord.Colour(int("002EFF", 16))
			color16 = discord.Colour(int("570679", 16))
			permissions = discord.Permissions.none()
			await self.bot.create_role(server=ctx.message.server, permissions=permissions, name='red', color=color)
			await asyncio.sleep(0.4)
			await self.bot.create_role(server=ctx.message.server, permissions=permissions, name='green', color=color2)
			await asyncio.sleep(0.4)
			await self.bot.create_role(server=ctx.message.server, permissions=permissions, name='purple', color=color3)
			await asyncio.sleep(0.4)
			await self.bot.create_role(server=ctx.message.server, permissions=permissions, name='blue', color=color4)
			await asyncio.sleep(0.4)
			await self.bot.create_role(server=ctx.message.server, permissions=permissions, name='orange', color=color5)
			await asyncio.sleep(0.4)
			await self.bot.create_role(server=ctx.message.server, permissions=permissions, name='black', color=color6)
			await asyncio.sleep(0.4)
			await self.bot.create_role(server=ctx.message.server, permissions=permissions, name='white', color=color7)
			await asyncio.sleep(0.4)
			await self.bot.create_role(server=ctx.message.server, permissions=permissions, name='cyan', color=color8)
			await asyncio.sleep(0.4)
			await self.bot.create_role(server=ctx.message.server, permissions=permissions, name='lime', color=color9)
			await asyncio.sleep(0.4)
			await self.bot.create_role(server=ctx.message.server, permissions=permissions, name='pink', color=color10)
			await asyncio.sleep(0.4)
			await self.bot.create_role(server=ctx.message.server, permissions=permissions, name='yellow', color=color11)
			await asyncio.sleep(0.4)
			await self.bot.create_role(server=ctx.message.server, permissions=permissions, name='lightred', color=color12)
			await asyncio.sleep(0.4)
			await self.bot.create_role(server=ctx.message.server, permissions=permissions, name='lavender', color=color13)
			await asyncio.sleep(0.4)
			await self.bot.create_role(server=ctx.message.server, permissions=permissions, name='salmon', color=color14)
			await asyncio.sleep(0.4)
			await self.bot.create_role(server=ctx.message.server, permissions=permissions, name='darkblue', color=color15)
			await asyncio.sleep(0.4)
			await self.bot.create_role(server=ctx.message.server, permissions=permissions, name='darkpurple', color=color16)
			await self.bot.say("Added colors (16)\n```{0}```".format(", ".join(self.color_roles)))
			await self.bot.say("You might need to re-order the new color ranks to the top of the roles\nif they are not working!")
		except Exception as e:
			await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

	@commands.command(pass_context=True)
	async def mentions(self, ctx, max_messages:int=3000, idk=None):
		"""Searches through inputed amount (Max 3000) of bot messages to find any mentions for you.\n Results sent via PM."""
		count = max_messages
		found = False
		if max_messages > 3000 and ctx.message.author.id != self.bot.owner.id:
			await self.bot.say("2 many messages (<= 3000)")
			return
		if max_messages == 0:
			await self.bot.say("Please input a number of messages to search through!\n Ex: `.mentions 20` searches through 20 messages if you were mentioned.")
		if max_messages > 0:
			await self.bot.say("Sending results over PM `{0}`".format(ctx.message.author.name))
		async for message in self.bot.logs_from(ctx.message.channel, limit=max_messages):
			count = count - 1
			if ctx.message.author.mention in message.content:
				found = True
				await self.bot.send_message(ctx.message.author, "{0} has mentioned you in \"{1}\"\nTime: `{2}`".format(message.author.mention, message.content, message.timestamp.strftime('%m/%d/%Y %H:%M:%S')))
			elif "<@!" + ctx.message.author.id + ">" in message.content:
				found = True
				await self.bot.send_message(ctx.message.author, "{0} has mentioned you in \"{1}\"\nTime: `{2}`".format(message.author.mention, message.content, message.timestamp.strftime('%m/%d/%Y %H:%M:%S')))
			elif idk != None and "@everyone" in message.content:
				found = True
				await self.bot.send_message(ctx.message.author, "{0} has mentioned you in \"1}\"\nTime: `{2}`".format(message.author.mention, message.content, message.timestamp.strftime('%m/%d/%Y %H:%M:%S')))
			elif idk != None and "@here" in message.content:
				found = True
				await self.bot.send_message(ctx.message.author, "{0} has mentioned you in \"{1}\"\nTime: `{2}`".format(message.author.mention, message.content, message.timestamp.strftime('%m/%d/%Y %H:%M:%S')))
			elif count == 0 and found == False:
				await self.bot.send_message(ctx.message.author, "No messages found with {0} mentioned \nwithin the given max message search amount!".format(ctx.message.author.mention))

	@commands.command(pass_context=True)
	async def search(self, ctx, max_messages:int=None, *, text:str):
		"""Searches through inputed amount (Max 2000) of bot messages to\n find the text you inputed.\n Results sent via PM.\n Ex: '.search 10 text'"""
		try:
			if max_messages is None:
				await self.bot.say("Please input a number of messages to search through!\n Ex: `.text 20 TEXT` searches through 20 messages with the text you inputed.")
				return
			count = max_messages
			text = text.lower()
			if max_messages > 2000 and ctx.message.author.id != bot.owner.id:
				await self.bot.say("2 many messages (<= 2000)")
				return
			if max_messages > 0:
				await self.bot.say("Sending results over PM `{0}`".format(ctx.message.author))
			found_msgs = []
			async for message in self.bot.logs_from(ctx.message.channel, limit=max_messages):
				count = count - 1
				if message.content != ctx.message.content and text in message.content.lower():
					found_msgs.append("`{0}` has been found in message (ID: {4}) \"{1}\"\nAuthor: `{2}`\nTime: `{3}`".format(text, message.content, message.author.name, message.timestamp.strftime('%m/%d/%Y %H:%M:%S'), message.id))
				elif count == 0 and not found_msgs:
					await self.bot.send_message(ctx.message.author, "No messages found with `{0}` \nwithin the given max message search amount!".format(text))
					return
			await self.truncate(ctx.message.author, '\n'.join(found_msgs))
		except Exception as e:
			await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

	@commands.command(pass_context=True)
	@commands.cooldown(1, 15)
	async def gist(self, ctx, content:str):
		payload = {
			'name': 'NotSoBot - By: {0}.'.format(ctx.message.author),
			'text': content,
			'private': '1',
			'expire': '0'
		}
		with aiohttp.ClientSession() as session:
			async with session.post('https://spit.mixtape.moe/api/create', data=payload) as r:
				url = await r.text()
		await self.bot.say('Uploaded to paste, URL: <{0}>'.format(url))

	@commands.command(pass_context=True)
	@checks.is_owner()
	async def setavatar(self, ctx, url:str):
		"""Changes the bots avatar.\nOwner only ofc."""
		try:
			b = await self.bytes_download(url)
			await self.bot.edit_profile(avatar=b)
			await self.bot.send_file(ctx.message.channel, b, content="Avatar has been changed to:")
		except Exception as e:
			await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

	@commands.command(pass_context=True)
	@checks.is_owner()
	async def setname(self, ctx, *, name:str):
		"""Changes the bots name.\nOwner only ofc."""
		try:
			await self.bot.edit_profile(username=name)
			await self.bot.say("ok, username changed to `{0}`".format(name))
		except Exception as e:
			await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

	async def do_sed(self, message, text=None):
		try:
			if not message.channel:
				return
			log_before = message
			path = None
			match = None
			found = False
			text = message.content if not text else text
			match = text.split('/')
			if match[0] != "s" and match[0] != "sed":
				if not self.bot.self_bot and match[0] != 're':
					return
			if len(match) != 1 and match[1] != '':
				text_one = match[1]
			else:
				await self.bot.send_message(message.channel, "Error: Invalid Syntax\n`s/text to find (you are missing this)/text to replace with/`")
				return
			if len(match) >= 3:
				text_two = match[2]
			else:
				await self.bot.send_message(message.channel, "Error: Invalid Syntax\n`s/text to find/text to replace with (you are missing this)/`")
				return
			if len(match) == 4:
				text_three = match[3]
			else:
				text_three = ''
			rand = str(random.randint(0, 999))
			path = self.files_path('sed_{0}.txt'.format(rand))
			if text_three == '':
				cmd = ['sed', 's/{0}/{1}/g'.format(text_one, text_two), path]
			else:
				cmd = ['sed', 's/{0}/{1}/{2}'.format(text_one, text_two, text_three), path]
			async for m in self.bot.logs_from(message.channel, limit=50, before=log_before):
				if self.bot.self_bot:
					if m.author != self.bot.owner:
						continue
				if not found and not m.content.startswith('.s') and not m.content.startswith('s/') and not m.content.startswith('sed/') and re.search(text_one, m.content):
					found = True
					open(path, 'w').close()
					with io.open(path, "a", encoding='utf8') as f:
						f.write(m.content)
						f.close()
					x = await self.bot.run_process(cmd, True)
					if self.bot.self_bot:
						await self.bot.delete_message(message)
						await self.bot.edit_message(m, x)
						return
					msg = "{0}: {1}".format(m.author.name, x)
			if found:
				await self.bot.send_message(message.channel, msg)
			else:
				await self.bot.send_message(message.channel, "No messages found with `{0}`!".format(text_one))
		except discord.errors.Forbidden:
			return
		except Exception as e:
			await self.bot.say(type(e).__name__ + ': ' + str(e))
		if path:
			os.remove(path)

	@commands.command(pass_context=True)
	async def s(self, ctx, *, text:str=None):
		await self.do_sed(ctx.message, text)

	async def on_message(self, message):
		if message.content[:2] == 's/' or message.content.startswith('sed/'):
			if message.channel.is_private is False:
				if message.server.me.permissions_in(message.channel).send_messages is False:
					return
			await self.do_sed(message)
		elif self.bot.self_bot and message.content.startswith('re/'):
			await self.do_sed(message)

	@commands.command(pass_context=True)
	@commands.cooldown(1, 10)
	async def screenshot(self, ctx, *, url:str):
			try:
				x = await self.bot.say("ok, processing")
				if "http" not in url:
					url = "https://" + url
				depot = DepotManager.get()
				driver = webdriver.PhantomJS()
				driver.set_window_size(1024, 768) # set the window size that you need 
				driver.get(url)
				location = self.files_path('screenshot.png')
				driver.save_screenshot(location)
				if os.path.getsize(location) <= 3150:
					await self.bot.say("No screenshot was able to be taken\n Most likely cloudflare blocked me.")
					return
				await self.bot.delete_message(x)
				await self.bot.say("ok, here\'s a screenshot of `{0}`".format(url))
				await self.bot.send_file(ctx.message.channel, location)
			except Exception as e:
				await self.bot.say(code.format(type(e).__name__ + ': ' + str(e)))

	@commands.command(pass_context=True, aliases=['showadmins', 'onlineadmins', 'modsonline', 'mods', 'onlinemods'])
	async def admins(self, ctx):
		"""Show current online admins and mods"""
		# roles_ = ['admin', 'mod', 'moderator', 'administrator', 'owner', 'underadministrator', 'moderators', 'founder']
		admin_perms = ['administrator', 'manage_server']
		mod_perms = ['manage_messages', 'ban_members', 'kick_members']
		admin_roles = []
		mod_roles = []
		online = []
		for role in ctx.message.server.roles:
			perms = []
			for s in role.permissions:
				perms.append(s)
			for x in admin_perms:
				for s in perms:
					if s[0] == x and s[1] == True:
							admin_roles.append(role.name.lower())
			for x in mod_perms:
				for s in perms:
					if s[0] == x and s[1] == True and role.name.lower() not in admin_roles:
							mod_roles.append(role.name.lower())
		for member in ctx.message.server.members:
			if member.bot:
				continue
			emote = ''
			roles = list((map(str, member.roles)))
			roles = list(map(lambda x: x.lower(), roles))
			if member.status == discord.Status.online:
				emote = '<:vpOnline:212789758110334977> '
			elif member.status == discord.Status.idle:
				emote = '<:vpAway:212789859071426561> '
			elif member.status == discord.Status.offline or member.status == discord.Status.invisible:
				emtote = '<:vpOffline:212790005943369728> '
			elif member.status == discord.Status.dnd:
				continue
			else:
				emtote = '<:vpOffline:212790005943369728> '
			if ctx.message.server.owner == member:
				online.append(emote+'**Admin** `{0}`'.format(member.name))
			for x in roles:
				for s in admin_roles:
					if x == s:
						not_in_thing = True
						for idfk in online:
							if '**Admin** `{0}`'.format(member.name) == idfk or '**Mod** `{0}`'.format(member.name) == idfk:
								not_in_thing = False
								break
						if not_in_thing:
							online.append(emote+'**Admin** `{0}`'.format(member.name))
				for s in mod_roles:
					if x == s:
						not_in_thing = True
						for idfk in online:
							if '**Mod** `{0}`'.format(member.name) == idfk or '**Admin** `{0}`'.format(member.name) == idfk:
								not_in_thing = False
								break
						if not_in_thing:
							online.append(emote+'**Mod** `{0}`'.format(member.name))
		if len(online) == 0:
			await self.bot.say("No staff were found that are online!")
			return
		msg = ''
		for s in online:
			msg += '{0}\n'.format(s)
		await self.bot.say("**Online Staff**\n"+msg)

	@commands.command(aliases=['tl', 'tr'])
	async def translate(self, lang1:str, lang2:str, *, text:str=None):
		if text is None:
			text = lang2
		try:
			translated = textblob.TextBlob(text).translate(from_lang=lang1, to=lang2)
		except textblob.exceptions.NotTranslated:
			await self.bot.say('Translation error.')
		else:
			await self.bot.say(translated)

	@commands.command(pass_context=True, aliases=['rcount'])
	async def rolecount(self, ctx, *, rolename:str):
		rolename = rolename.lower()
		rolee = None
		for role in ctx.message.server.roles:
			if role.is_everyone:
				continue
			if role.name.lower() in rolename or role.name.lower() == rolename:
				rolee = role
				break
		if rolee is None:
			await self.bot.say(':no_entry: `Role not found.`')
			return
		count = 0
		for member in ctx.message.server.members:
			if rolee in member.roles:
				count += 1
		await self.bot.say('There is **{0}** members in the role `{1}`'.format(count, rolee.name))

	@commands.group(name='hash', invoke_without_command=True)
	async def hash_cmd(self, *, txt:str):
		"""MD5 Encrypt Text"""
		md5 = hashlib.md5(txt.encode()).hexdigest()
		await self.bot.say('**MD5**\n'+md5)

	@hash_cmd.command(name='sha1')
	async def hash_sha1(self, *, txt:str):
		"""SHA1 Encrypt Text"""
		sha = hashlib.sha1(txt.encode()).hexdigest()
		await self.bot.say('**SHA1**\n'+sha)

	@hash_cmd.command(name='sha256')
	async def hash_sha256(self, *, txt:str):
		"""SHA256 Encrypt Text"""
		sha256 = hashlib.sha256(txt.encode()).hexdigest()
		await self.bot.say('**SHA256**\n'+sha256)

	@hash_cmd.command(name='sha512')
	async def hash_sha512(self, *, txt:str):
		"""SHA512 Encrypt Text"""
		sha512 = hashlib.sha512(txt.encode()).hexdigest()
		await self.bot.say('**SHA512**\n'+sha512)

	@commands.command()
	@checks.is_owner()
	async def googleapitest(self):
		try:
			from mods.Fun import google_api
			dead_keys = []
			for key in google_api:
				with aiohttp.ClientSession() as session:
					async with session.get('https://www.googleapis.com/customsearch/v1?key={0}&cx=015418243597773804934:it6asz9vcss&q=test'.format(key)) as r:
						load = await r.json()
				try:
					if load['error']:
						dead_keys.append(key)
						continue
				except KeyError:
					pass
			if dead_keys:
				await self.bot.say('Dead Keys (**{0}**/{1}): `{2}`'.format(len(dead_keys), len(google_api), ', '.join(dead_keys)))
			else:
				await self.bot.say('woah, no dead keys!')
		except Exception as e:
			await self.bot.say(e)

	@commands.group(pass_context=True, aliases=['feedback', 'contact'], invoke_without_command=True)
	@commands.cooldown(1, 20, commands.BucketType.server)
	async def complain(self, ctx, *, message:str):
		message = message
		if len(ctx.message.mentions):
			for s in ctx.message.mentions:
				message = message.replace(s.mention, '@'+s.name).replace('<@!{0}>'.format(s.id), '@'+s.name)
		sql = 'INSERT INTO `feedback` (`shard`, `user`, `channel`) VALUES (%s, %s, %s)'
		self.cursor.execute(sql, (self.bot.shard_id, ctx.message.author.id, ctx.message.channel.id))
		self.cursor.commit()
		sql = 'SELECT `id` FROM `feedback` ORDER BY `id` DESC LIMIT 1'
		f_id = int(self.cursor.execute(sql).fetchall()[0]['id'])
		await self.bot.queue_message("186704399677128704", "**Feedback #__{5}__**\nShard: `{6}`\nUser: **{0}** `<{0.id}>`\nServer: `{1.name} <{1.id}>`\nChannel: `{2.name} <{2.id}>`\nTime: __{3}__\nMessage:```{4}```".format(ctx.message.author, ctx.message.server, ctx.message.channel, ctx.message.timestamp.strftime('%m/%d/%Y %H:%M:%S'), message, f_id, self.bot.shard_id))
		await self.bot.say("ok, left feedback")

	@complain.command(name='respond', invoke_without_command=True)
	@checks.is_owner()
	async def complain_respond(self, f_id, *, message:str):
		if f_id == '|' or f_id == 'latest':
			sql = 'SELECT `id` FROM `feedback` ORDER BY `id` DESC LIMIT 1'
			f_id = int(self.cursor.execute(sql).fetchall()[0]['id'])
		sql = 'SELECT * FROM `feedback` WHERE id={0}'
		sql = sql.format(f_id)
		result = self.cursor.execute(sql).fetchall()
		if len(result) == 0:
			await self.bot.say('Invalid Feedback ID!')
			return
		target = await self.bot.get_user_info(str(result[0]['user']))
		try:
			await self.bot.send_message(target, '**In Response to Feedback #__{0}__**\n{1}'.format(result[0]['id'], message))
			await self.bot.say(':white_check_mark: Sent response!')
		except:
			await self.bot.say(':warning: Error sending response.')

def setup(bot):
	bot.add_cog(Utils(bot))
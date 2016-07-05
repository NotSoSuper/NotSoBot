import asyncio
import discord
import pymysql
import os
import re
import random
import math
import time
import aiohttp
import requests
import numpy as np
import PIL
import requests_cache
import glob
from discord.ext import commands
from utils import checks

cool = "```xl\n{0}\n```"
code = "```py\n{0}\n```"

connection = pymysql.connect(host='',
                     user='',
                     password='',
                     db='',
                     charset='',
                     cursorclass=pymysql.cursors.DictCursor)
cursor = connection.cursor()

sql_injection = ['DROP', 'FROM', 'TABLE', 'SELECT', 'SELECT *', 'ALTER', 'UPDATE', 'INSERT', 'DELETE']

async def download(url:str, path:str):
	with aiohttp.ClientSession() as session:
		async with session.get(url) as resp:
			data = await resp.read()
			with open(path, "wb") as f:
				f.write(data)
				f.close()

class Logs():
	def __init__(self, bot):
		self.bot = bot

	async def avatar_cache(self):
		servers = self.bot.servers
		for server in servers:
			path_ = "/root/discord/files/cache/{0}.jpg".format(server.id)
			if os.path.isfile(path_) == False and server.icon != None:
				print("downloading server icon {0}".format(server.icon))
				await download("https://cdn.discordapp.com/icons/{0}/{1}.jpg".format(server.id, server.icon), path_)
			members = server.members
			for member in members:
				path = "/root/discord/files/cache/{0}.jpg".format(member.id)
				if os.path.isfile(path) == False and member.avatar != None:
					print("downloading avatar {0}".format(member.avatar))
					await download("https://cdn.discordapp.com/avatars/{0}/{1}.jpg".format(member.id, member.avatar), path)
				else:
					continue
		# for s in glob.glob("/root/discord/files/cache/*.jpg"):
		# 	if os.path.getsize(s) == 127:
		# 		os.remove(s)
		# 	else:
		# 		continue

	def remove_server(self, server):
		remove_sql = "DELETE FROM `logs` WHERE server={0}"
		remove_sql = remove_sql.format(server.id)
		cursor.execute(remove_sql)
		connection.commit()

	@commands.command(pass_context=True, invoke_without_command=True, aliases=['slogs', 'adminlogs'])
	@checks.admin_or_perm(manage_server=True)
	async def serverlogs(self, ctx, channel:discord.Channel=None):
		"""Setup Server Logs for a Specific Channel or Current Channel"""
		sql = "INSERT INTO `logs` (`server`, `channel`, `user`) VALUES (%s, %s, %s)"
		if channel == None:
			chan = ctx.message.channel
		else:
			chan = channel
		update_sql = "UPDATE `logs` SET channel={0} WHERE server={1}"
		update_sql = update_sql.format(chan.id, ctx.message.server.id)
		remove_sql = "DELETE FROM `logs` WHERE server={0}"
		remove_sql = remove_sql.format(ctx.message.server.id)
		check = "SELECT server,channel FROM `logs` WHERE channel={0}"
		check = check.format(chan.id)
		cursor.execute(check)
		result = cursor.fetchall()
		if len(result) == 0:
			cursor.execute(sql, (ctx.message.server.id, chan.id, ctx.message.author.id))
			connection.commit()
			await self.bot.say(":white_check_mark: Set Server Logs to Channel \"{0.name} <{0.id}>\"".format(chan))
		elif result[0]['channel'] == ctx.message.channel.id:
			cursor.execute(remove_sql)
			connection.commit()
			await self.bot.say(":white_check_mark: Disabled Server Logs")
		else:
			cursor.execute(update_sql)
			connection.commit()
			await self.bot.say(":white_check_mark: Updated Server Logs Channel to \"{0.name} <{0.id}>\"".format(chan))

	@commands.command()
	@checks.is_owner()
	async def updatecache(self):
		"""Update Avatar and Server Icon Cache"""
		await self.bot.say("ok, updating cache")
		await self.avatar_cache()

	async def on_command(self, command, ctx):
		try:
			if ctx.message.channel.is_private:
				return
			sql = "SELECT server,channel FROM `logs` WHERE server={0}"
			sql = sql.format(ctx.message.server.id)
			cursor.execute(sql)
			result = cursor.fetchall()
			if len(result) == 0:
				return
			channel = result[0]['channel']
			server = result[0]['server']
			if ctx.message.server.id != server:
				return
			if len(ctx.message.content) > 2000:
				ctx.message.content = ctx.message.content[:2000]+"\n:warning: Message Truncated (<= 2000)"
			if len(ctx.message.mentions) != 0:
				for s in ctx.message.mentions:
					ctx.message.content = ctx.message.content.replace(s.mention, s.name)
			msg = "User: {0} <{1}>\n".format(ctx.message.author, ctx.message.author.id).replace("'", "")
			msg += "Command: {0}\n".format(ctx.invoked_with)
			msg += "Server: {0}\n".format(ctx.message.server.name).replace("'", "")
			msg += "Channel: {0}\n".format(ctx.message.channel.name).replace("'", "")
			msg2 = "`Context Message`: \"{0}\"".format(ctx.message.content)
			target = discord.Object(id=channel)
			await self.bot.send_message(target, "`[{0}]` :exclamation: **Command Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg)+msg2)
		except discord.errors.Forbidden:
			self.remove_server(ctx.message.server)

	async def on_message_delete(self, message):
		try:
			if message.channel.is_private:
				return
			if message.author == self.bot.user:
				return
			off_check = "SELECT id FROM `muted` WHERE server={0} AND id={1}"
			off_check = off_check.format(message.server.id, message.author.id)
			cursor.execute(off_check)
			off_results = cursor.fetchall()
			if len(off_results) != 0:
				return
			sql = "SELECT server,channel FROM `logs` WHERE server={0}"
			sql = sql.format(message.server.id)
			cursor.execute(sql)
			result = cursor.fetchall()
			if len(result) == 0:
				return
			channel = result[0]['channel']
			server = result[0]['server']
			if message.server.id != server:
				return
			if message.channel.id == channel:
				return
			if len(message.content) > 2000:
				message.content = message.content[:2000]+"\n:warning: Message Truncated (<= 2000)"
			message.content = message.content.replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
			if len(message.mentions) != 0:
				for s in message.mentions:
					message.content = message.content.replace(s.mention, s.name)
			msg = "User: {0} <{1}>\n".format(message.author, message.author.id).replace("'", "")
			msg += "Channel: {0.name} <{0.id}>\n".format(message.channel).replace("'", "")
			msg2 = "`Deleted Message`: \"{0}\"".format(message.content)
			target = discord.Object(id=channel)
			await self.bot.send_message(target, "`[{0}]` :x: **Message Delete Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg)+msg2)
		except discord.errors.Forbidden:
			self.remove_server(message.server)

	async def on_message_edit(self, before, after):
		try:
			if before.channel.is_private:
				return
			if before.content == after.content:
				return
			if before.author == self.bot.user:
				return
			sql = "SELECT server,channel FROM `logs` WHERE server={0}"
			sql = sql.format(before.server.id)
			cursor.execute(sql)
			result = cursor.fetchall()
			if len(result) == 0:
				return
			channel = result[0]['channel']
			server = result[0]['server']
			if before.server.id != server:
				return
			if before.channel.id == channel:
				return
			if len(before.content) > 2000:
				before.content = before.content[:2000]+"\n:warning: Message Truncated (<= 2000)"
			if len(after.content) > 2000:
				after.content = after.content[:2000]+"\n:warning: Message Truncated (<= 2000)"
			before.content = before.content.replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
			after.content = after.content.replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
			if len(before.mentions) != 0:
				for s in before.mentions:
					before.content = before.content.replace(s.mention, s.name)
			if len(after.mentions) != 0:
				for s in after.mentions:
					after.content = after.content.replace(s.mention, s.name)
			msg = "User: {0} <{1}>\n".format(before.author.name, before.author.id).replace("'", "")
			msg += "Channel: {0}\n".format(before.channel.name).replace("'", "")
			msg2 = "`Before`: \"{0}\"\n".format(before.content)
			msg2 += "`After`: \"{0}\"".format(after.content)
			target = discord.Object(id=channel)
			await self.bot.send_message(target, "`[{0}]`:warning: **Message Edit Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg)+msg2)
		except discord.errors.Forbidden:
			self.remove_server(after.server)

	async def on_channel_delete(self, channel):
		try:
			sql = "SELECT server,channel FROM `logs` WHERE server={0}"
			sql = sql.format(channel.server.id)
			cursor.execute(sql)
			result = cursor.fetchall()
			if len(result) == 0:
				return
			chan = result[0]['channel']
			if channel.id == chan:
				remove_sql = "DELETE FROM `logs` WHERE server={0}"
				remove_sql = remove_sql.format(channel.server.id)
				cursor.execute(remove_sql)
				connection.commit()
				return
			server = result[0]['server']
			if channel.server.id != server:
				return
			a = channel.server
			msg = "Channel Deleted: {0} <{1}>\n".format(channel.name, channel.id).replace("'", "")
			target = discord.Object(id=chan)
			await self.bot.send_message(target, "`[{0}]` :x: **Channel Delete Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
		except discord.errors.Forbidden:
			self.remove_server(channel.server)

	async def on_channel_create(self, channel):
		try:
			if channel.is_private:
				return
			sql = "SELECT server,channel FROM `logs` WHERE server={0}"
			sql = sql.format(channel.server.id)
			cursor.execute(sql)
			result = cursor.fetchall()
			if len(result) == 0:
				return
			chan = result[0]['channel']
			server = result[0]['server']
			if channel.server.id != server:
				return
			a = channel.server
			msg = "Channel Created: {0} <{1}>\n".format(channel.name, channel.id).replace("'", "")
			target = discord.Object(id=chan)
			await self.bot.send_message(target, "`[{0}]` :white_check_mark: **Channel Create Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
		except discord.errors.Forbidden:
			self.remove_server(channel.server)

	async def on_channel_update(self, before, after):
		try:
			sql = "SELECT server,channel FROM `logs` WHERE server={0}"
			sql = sql.format(before.server.id)
			cursor.execute(sql)
			result = cursor.fetchall()
			if len(result) == 0:
				return
			channel = result[0]['channel']
			server = result[0]['server']
			if before.server.id != server:
				return
			a = before.server
			msg = "Channel Edited: {0} <{1}>\n".format(before.name, before.id).replace("'", "")
			msg += "Channel Created: {0}\n".format(before.created_at)
			msg += "Channel Type: {0}\n".format(str(after.type))
			if before.name != after.name:
				msg += "Name Before: {0}\n".format(before.name)
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
			await self.bot.send_message(target, "`[{0}]` :warning: **Channel Edit Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
		except discord.errors.Forbidden:
			self.remove_server(after.server)

	async def on_member_join(self, member):
		try:
			if member == self.bot.user:
				return
			sql = "SELECT server,channel FROM `logs` WHERE server={0}"
			sql = sql.format(member.server.id)
			cursor.execute(sql)
			result = cursor.fetchall()
			if len(result) == 0:
				return
			channel = result[0]['channel']
			server = result[0]['server']
			if member.server.id != server:
				return
			a = member.server
			msg = "Member Joined: {0.name} <{0.id}>\n".format(member)
			msg += "Server: {0.name} <{0.id}>\n".format(a).replace("'", "")
			target = discord.Object(id=channel)
			await self.bot.send_message(target, "`[{0}]` :inbox_tray: **Member Join Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
		except discord.errors.Forbidden:
			self.remove_server(member.server)

	async def on_member_remove(self, member):
		try:
			if member == self.bot.user:
				return
			sql = "SELECT server,channel FROM `logs` WHERE server={0}"
			sql = sql.format(member.server.id)
			cursor.execute(sql)
			result = cursor.fetchall()
			if len(result) == 0:
				return
			channel = result[0]['channel']
			server = result[0]['server']
			if member.server.id != server:
				return
			a = member.server
			msg = "Left the server: {0.name} <{0.id}>\n".format(member)
			# msg += "Server: {0.name} <{0.id}>\n".format(a).replace("'", "")
			target = discord.Object(id=channel)
			await self.bot.send_message(target, "`[{0}]` :outbox_tray: **Member Leave Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
		except discord.errors.Forbidden:
			self.remove_server(member.server)

	async def on_member_ban(self, member):
		try:
			if member == self.bot.user:
				return
			sql = "SELECT server,channel FROM `logs` WHERE server={0}"
			sql = sql.format(member.server.id)
			cursor.execute(sql)
			result = cursor.fetchall()
			if len(result) == 0:
				return
			channel = result[0]['channel']
			server = result[0]['server']
			if member.server.id != server:
				return
			msg = "User Banned: {0.name} <{0.id}>\n".format(member)
			target = discord.Object(id=channel)
			await self.bot.send_message(target, "`[{0}]` :outbox_tray: **Member Ban Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
		except discord.errors.Forbidden:
			self.remove_server(member.server)

	async def on_member_unban(self, server, member):
		try:
			if member == self.bot.user:
				return
			sql = "SELECT server,channel FROM `logs` WHERE server={0}"
			sql = sql.format(server.id)
			cursor.execute(sql)
			result = cursor.fetchall()
			if len(result) == 0:
				return
			channel = result[0]['channel']
			serverr = result[0]['server']
			if server.id != serverr:
				return
			msg = "Unbanned User: {0.name} <{0.id}>\n".format(member)
			target = discord.Object(id=channel)
			await self.bot.send_message(target, "`[{0}]` :white_check_mark: **Member Unban Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
		except discord.errors.Forbidden:
			self.remove_server(server)

	async def on_member_update(self, before, after):
		try:
			if before == self.bot.user:
				return
			sql = "SELECT server,channel FROM `logs` WHERE server={0}"
			sql = sql.format(before.server.id)
			cursor.execute(sql)
			result = cursor.fetchall()
			if len(result) == 0:
				return
			channel = result[0]['channel']
			server = result[0]['server']
			if before.server.id != server:
				return
			target = discord.Object(id=channel)
			if before.avatar != after.avatar:
				msg = "User: {0.name} <{0.id}>\n".format(after)
				before_p = '/root/discord/files/cache/{0}.jpg'.format(before.id)
				after_p = '/root/discord/files/avatars/after_avatar.jpg'
				if os.path.isfile(before_p) == False or os.path.getsize(before_p) == 127:
					return
				if before.avatar == None:
					await download("https://cdn.discordapp.com/avatars/{0}/{1}.jpg".format(after.id, after.avatar), after_p)
					if os.path.isfile(after_p) == False or os.path.getsize(after_p) == 127:
						return
					await self.bot.send_message(target, ":frame_photo: **New Avatar Log**\n"+cool.format(msg))
					await self.bot.send_file(target, after_p)
					await self.avatar_cache()
					return
				await download("https://cdn.discordapp.com/avatars/{0}/{1}.jpg".format(after.id, after.avatar), after_p)
				if os.path.isfile(after_p) == False or os.path.getsize(after_p) == 127:
					return
				list_im = [before_p, after_p]
				imgs    = [PIL.Image.open(i) for i in list_im]
				min_shape = sorted( [(np.sum(i.size), i.size ) for i in imgs])[0][1]
				imgs_comb = np.hstack( (np.asarray( i.resize(min_shape) ) for i in imgs ) )
				imgs_comb = PIL.Image.fromarray( imgs_comb)
				new_p = '/root/discord/files/avatars/avatar.jpg'
				imgs_comb.save(new_p)
				await self.bot.send_message(target, "`[{0}]` :frame_photo: **Avatar Change Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
				await self.bot.send_file(target, new_p)
				await download("https://cdn.discordapp.com/avatars/{0}/{1}.jpg".format(after.id, after.avatar), before_p)
				os.system("rm /root/discord/files/avatars/*")
				await self.avatar_cache()
			if before.name != after.name:
				msg = "User Name Before: {0.name} <{0.id}>\n".format(before)
				msg += "User Name After: {0.name}\n".format(after)
				await self.bot.send_message(target, "`[{0}]` :name_badge: **Name Change Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
			if before.nick != None:
				if before.nick != after.nick:
					msg = "User: {0.name} <{0.id}>\n".format(after)
					msg += "Nickname Before: {0}\n".format(before.nick)
					msg += "Nickname After: {0}\n".format(after.nick)
					await self.bot.send_message(target, "`[{0}]` :warning: **Nickname Change Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
			elif after.nick != None:
				msg = "User: {0.name} <{0.id}>\n".format(after)
				msg += "Nickname: {0}\n".format(after.nick)
				await self.bot.send_message(target, "`[{0}]` :warning: **Nickname Create Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
			if before.roles != after.roles:
				msg = "User: {0.name} <{0.id}>\n".format(after)
				r_b = ", ".join(map(str, before.roles)).replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
				r_a = ", ".join(map(str, after.roles)).replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
				msg += "Roles Before: {0}\n".format(r_b)
				msg += "Roles After: {0}\n".format(r_a)
				await self.bot.send_message(target, "`[{0}]` :bangbang: **Roles Change Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
			await self.avatar_cache()
		except discord.errors.Forbidden:
			self.remove_server(after.server)

	async def on_server_update(self, before, after):
		try:
			sql = "SELECT server,channel FROM `logs` WHERE server={0}"
			sql = sql.format(before.id)
			cursor.execute(sql)
			result = cursor.fetchall()
			if len(result) == 0:
				return
			channel = result[0]['channel']
			server = result[0]['server']
			if before.id != server:
				return
			target = discord.Object(id=channel)
			if before.icon != after.icon:
				msg = "Server: {0.name} <{0.id}>\n".format(after)
				before_p = '/root/discord/files/cache/{0}.jpg'.format(before.id)
				after_p = '/root/discord/files/avatars/after_icon.jpg'
				if before.icon == None:
					await download("https://cdn.discordapp.com/icons/{0}/{1}.jpg".format(after.id, after.icon), after_p)
					await self.bot.send_message(target, "`[{0}]` :frame_photo: **New Server Icon Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
					await self.bot.send_file(target, after_p)
					await self.avatar_cache()
					return
				await download("https://cdn.discordapp.com/icons/{0}/{1}.jpg".format(after.id, after.icon), after_p)
				list_im = [before_p, after_p]
				imgs    = [PIL.Image.open(i) for i in list_im]
				min_shape = sorted( [(np.sum(i.size), i.size ) for i in imgs])[0][1]
				imgs_comb = np.hstack( (np.asarray( i.resize(min_shape) ) for i in imgs ) )
				imgs_comb = PIL.Image.fromarray( imgs_comb)
				new_p = '/root/discord/files/avatars/icon.jpg'
				imgs_comb.save(new_p)
				await self.bot.send_message(target, "`[{0}]` :frame_photo: **Server Icon Change Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
				await self.bot.send_file(target, new_p)
				await download("https://cdn.discordapp.com/avatars/{0}/{1}.jpg".format(after.id, after.icon), before_p)
				os.system("rm /root/discord/files/avatars/*")
				await self.avatar_cache()
			if before.name != after.name:
				msg = "Server Name Before: {0}\n".format(before.name)
				msg += "Server Name After: {0}\n".format(after.name)
				await self.bot.send_message(target, "`[{0}]` :name_badge: **Server Name Change Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
			if before.region != after.region:
				msg = "Server Region Before: {0}\n".format(str(before.region))
				msg += "Server Region After: {0}\n".format(str(after.region))
				await self.bot.send_message(target, "`[{0}]` :globe_with_meridians: **Server Region Change Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
			await self.avatar_cache()
		except discord.errors.Forbidden:
			self.remove_server(after.server)

	async def on_server_role_create(self, role):
		try:
			sql = "SELECT server,channel FROM `logs` WHERE server={0}"
			sql = sql.format(role.server.id)
			cursor.execute(sql)
			result = cursor.fetchall()
			if len(result) == 0:
				return
			channel = result[0]['channel']
			server = result[0]['server']
			if role.server.id != server:
				return
			target = discord.Object(id=channel)
			# r_b = ', '.join(map(str, role.server.roles)).replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
			msg = "Server Role Created: {0}\n".format(role.name.replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere'))
			perms = []
			a = ""
			for s in role.permissions:
				perms.append(s)
			for s in perms:
				a += "Permission: {0}, {1}|".format(s[0], s[1])
			msg += "Role Permissions: \n[{0}]\n".format(a)
			# msg += "Server Roles List: \n[{0}]\n".format(r_b)
			await self.bot.send_message(target, "`[{0}]` :bangbang: **Server Roles Create Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
		except discord.errors.Forbidden:
			self.remove_server(role.server)

	async def on_server_role_delete(self, role):
		try:
			sql = "SELECT server,channel FROM `logs` WHERE server={0}"
			sql = sql.format(role.server.id)
			cursor.execute(sql)
			result = cursor.fetchall()
			if len(result) == 0:
				return
			channel = result[0]['channel']
			server = result[0]['server']
			if role.server.id != server:
				return
			target = discord.Object(id=channel)
			r_b = ', '.join(map(str, role.server.roles)).replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
			msg = "Server Role Deleted: {0}\n".format(role.name.replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere'))
			await self.bot.send_message(target, "`[{0}]` :bangbang: **Server Roles Delete Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
		except discord.errors.Forbidden:
			self.remove_server(role.server)

	async def on_server_role_update(self, before, after):
		try:
			sql = "SELECT server,channel FROM `logs` WHERE server={0}"
			sql = sql.format(before.server.id)
			cursor.execute(sql)
			result = cursor.fetchall()
			if len(result) == 0:
				return
			channel = result[0]['channel']
			server = result[0]['server']
			if before.server.id != server:
				return
			target = discord.Object(id=channel)
			msg = "Role: {0} <{1}>\n".format(before.name.replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere'), before.id)
			if before.permissions != after.permissions:
				msg = "Role: {0}\n".format(after.name.replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere'))
				perms = []
				a = ""
				for s in after.permissions:
					perms.append(s)
				for s in perms:
					a += "Permission: {0}, {1}|".format(s[0], s[1])
				msg += "Permissions: \n[{0}]\n".format(a)
				await self.bot.send_message(target, ":bangbang: **Server Roles Permission Log**\n"+cool.format(msg))
				msg = "Role: {0} <{1}>\n".format(before.name.replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere'), before.id)
			if before.name != after.name:
				msg += "Role Name Before: {0}\n".format(before.name.replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere'))
				msg += "Role Name After: {0}\n".format(after.name.replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere'))
			if before.position != after.position:
				msg += "Position Before: {0}\n".format(before.position)
				msg += "Position After: {0}\n".format(after.position)
			await self.bot.send_message(target, "`[{0}]` :bangbang: **Server Roles Update Log**\n".format(time.strftime("%I:%M:%S %p"))+cool.format(msg))
		except discord.errors.Forbidden:
			self.remove_server(after.server)

def setup(bot):
    bot.add_cog(Logs(bot))
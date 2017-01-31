import discord
import asyncio
import pymysql
import sqlalchemy
from discord.ext import commands
from utils import checks
from mods.cog import Cog

class Logging(Cog):
	def __init__(self, bot):
		super().__init__(bot)
		self.cursor = bot.mysql.cursor

	async def on_message(self, message):
		if message.author == self.bot.user:
			return
		sql = "INSERT INTO `messages` (`shard`, `server`, `server_name`, `channel`, `channel_name`, `user`, `user_id`, `message_id`, `action`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
		is_pm = True if message.channel.is_private else None
		server = message.server.id if not is_pm else None
		server_name = message.server.name if not is_pm else 'Private Message'
		channel = message.channel.id if not is_pm else None
		channel_name = message.channel.name if not is_pm else None
		user = str(message.author)
		user_id = message.author.id
		message_id = message.id
		action = 0
		self.cursor.execute(sql, (self.bot.shard_id, server, server_name, channel, channel_name, user, user_id, message_id, action))
		self.cursor.commit()
		# print("({0} <{1}>) {2} <{3}> | {4} <{5}> | {6}".format(server_name, server, channel_name, channel, user, user_id, message.clean_content))

	async def on_message_edit(self, before, after):
		if before.author == self.bot.user:
			return
		if before.content == after.content:
			return
		sql = "INSERT INTO `messages` (`shard`, `server`, `server_name`, `channel`, `channel_name`, `user`, `user_id`, `message_id`, `action`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
		is_pm = True if before.channel.is_private else None
		server = before.server.id if not is_pm else None
		server_name = before.server.name if not is_pm else 'Private Message'
		channel = before.channel.id if not is_pm else None
		channel_name = before.channel.name if not is_pm else None
		user = str(before.author)
		user_id = before.author.id
		message_id = before.id
		action = 2
		self.cursor.execute(sql, (self.bot.shard_id, server, server_name, channel, channel_name, user, user_id, message_id, action))
		self.cursor.commit()

	async def on_message_delete(self, message):
		if message.author == self.bot.user:
			return
		sql = "INSERT INTO `messages` (`shard`, `server`, `server_name`, `channel`, `channel_name`, `user`, `user_id`, `message_id`, `action`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
		is_pm = True if message.channel.is_private else None
		server = message.server.id if not is_pm else None
		server_name = message.server.name if not is_pm else 'Private Message'
		channel = message.channel.id if not is_pm else None
		channel_name = message.channel.name if not is_pm else None
		user = str(message.author)
		user_id = message.author.id
		message_id = message.id
		action = 1
		self.cursor.execute(sql, (self.bot.shard_id, server, server_name, channel, channel_name, user, user_id, message_id, attachment, action))
		self.cursor.commit()

	async def on_command(self, command, ctx):
		sql = "INSERT INTO `command_logs` (`shard`, `server`, `server_name`, `channel`, `channel_name`, `user`, `user_id`, `command`, `message`, `message_id`, `attachment`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
		message = ctx.message
		is_pm = True if message.channel.is_private else None
		server = message.server.id if not is_pm else None
		server_name = message.server.name if not is_pm else 'Private Message'
		channel = message.channel.id if not is_pm else None
		channel_name = message.channel.name if not is_pm else None
		user = str(message.author)
		user_id = message.author.id
		message_id = message.id
		attachment = ", ".join([attachment['url'] for attachment in message.attachments]) if message.attachments else None
		try:
			self.cursor.execute(sql, (self.bot.shard_id, server, server_name, channel, channel_name, user, user_id, command.name, message.content, message_id, attachment))
			self.cursor.commit()
		except (pymysql.err.IntegrityError, sqlalchemy.exc.IntegrityError, pymysql.err.IntegrityError):
			return

def setup(bot):
	bot.add_cog(Logging(bot))

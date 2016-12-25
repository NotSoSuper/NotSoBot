import asyncio
import discord
import os
import re
import random
import math
import io
import sys, traceback
import linecache
from io import StringIO
from itertools import islice, cycle
from discord.ext import commands
from utils import checks
from mods.cog import Cog

#old code (hence the sql mess), y fix

cool = "```xl\n{0}\n```"
code = "```py\n{0}\n```"

def check_int(k):
	if k[0] in ('-', '+'):
		return k[1:].isdigit()
	return k.isdigit()

class Tags(Cog):
	def __init__(self, bot):
		super().__init__(bot)
		self.cursor = bot.mysql.cursor
		self.escape = bot.escape
		self.discord_path = bot.path.discord
		self.files_path = bot.path.files
		self.truncate = bot.truncate

	def tag_formatter(self, s:str):
		s = s.encode("utf-8")
		s = s.decode('utf-8', 'ignore')
		s = u'\u180E' + s
		s = s.replace('@everyone', '@\u200beveryone')
		s = s.replace('@here', '@\u200bhere')
		s = s.replace("'", "\'")
		s = s.replace('"', "'")
		return s

	#new parser redacted

	@commands.group(pass_context=True, invoke_without_command=True, aliases=['t', 'ta', 'tags'], no_pm=True)
	async def tag(self, ctx, txt:str, *after):
		"""Base command for tags, call it with a valid tag to display a tag"""
		txt = self.tag_formatter(txt)
		exists_sql = "SELECT tag FROM `tags` WHERE tag={0} AND server is NULL"
		exists_sql = exists_sql.format(self.escape(txt))
		exists_result = self.cursor.execute(exists_sql).fetchall()
		if len(exists_result) == 0:
			await self.bot.say(":no_entry: Tag \"{0}\" does not exist!".format(txt))
			return
		check_sql = "SELECT server FROM `tags` WHERE server={0} AND tag={1}"
		check_sql = check_sql.format(ctx.message.server.id, self.escape(txt))
		check_result = self.cursor.execute(check_sql).fetchall()
		if len(check_result) == 0:
			sql = "SELECT content FROM `tags` WHERE tag={0} AND server is NULL"
			sql = sql.format(self.escape(txt))
		else:
			sql = "SELECT content FROM `tags` WHERE server={0} AND tag={1}"
			sql = sql.format(ctx.message.server.id, self.escape(txt))
		result = self.cursor.execute(sql).fetchall()
		content = result[0]['content']
		content = await self.parser(ctx, content, after)
		content = self.tag_formatter(content)
		await self.truncate(ctx.message.channel, content)

	@tag.command(name='add', aliases=['create', 'make'], pass_context=True, no_pm=True)
	@commands.cooldown(1, 20)
	async def tag_add(self, ctx, tag:str=None, *, txt:str=None):
		"""Add a tag"""
		if tag is None:
			await self.bot.say("Error: Invalid Syntax\nPlease input the tags name\n`.tag add <tag_name> <--this one <tag_content>`")
			return
		if txt is None:
			await self.bot.say("Error: Invalid Syntax\nPlease input something for the tag to contain\n`.tag add <tag_name> <tag_content> <--this one`")
			return
		if len(txt) > 1950:
			await self.bot.say(":no_entry: Tag Text Limit <= 1950")
			return
		tag = self.tag_formatter(tag)
		txt = self.tag_formatter(txt)
		tag_sql = "INSERT INTO `tags` (`user`, `tag`, `content`, `server_created`) VALUES (%s, %s, %s, %s)"
		server_sql = "INSERT INTO `tags` (`server`, `user`, `tag`, `content`) VALUES (%s, %s, %s, %s)"
		check_sql = "SELECT tag,server_created FROM `tags` WHERE tag={0} AND server is NULL"
		check_sql = check_sql.format(self.escape(tag))
		global_check_sql = "SELECT server FROM `tags` WHERE server={0} AND tag={1}"
		global_check_sql = global_check_sql.format(ctx.message.server.id, self.escape(tag))
		check_result = self.cursor.execute(check_sql).fetchall()
		if len(check_result) == 0:
			self.cursor.execute(tag_sql, (ctx.message.author.id, tag, txt, ctx.message.server.id))
			self.cursor.commit()
			await self.bot.say(":white_check_mark: Added Tag \"{0}\"".format(tag))
		else:
			global_result = self.cursor.execute(global_check_sql).fetchall()
			if len(global_result) == 0 and check_result[0]['server_created'] != ctx.message.server.id:
				self.cursor.execute(server_sql, (ctx.message.server.id, ctx.message.author.id, tag, txt))
				self.cursor.commit()
				await self.bot.say(":white_check_mark: Added Server Tag \"{0}\"".format(tag))
			else:
				await self.bot.say(":no_entry: Tag \"{0}\" already exists!".format(tag))

	@tag.command(name='remove', aliases=['delete'], pass_context=True, no_pm=True)
	async def tag_remove(self, ctx, *, txt:str=None):
		""""Remove a tag you own"""
		if txt is None:
			await self.bot.say("Error: Invalid Syntax\nPlease input something to remove from your tags\n`.tag remove <tag_name>`")
			return
		sql = "DELETE FROM `tags` WHERE user={0} AND server is NULL AND tag={1}"
		sql_server = "DELETE FROM `tags` WHERE server={0} AND user={1} AND tag={2}"
		sql_all = "DELETE FROM `tags` WHERE user={1}"
		sql = sql.format(ctx.message.author.id, self.escape(txt))
		sql_server = sql_server.format(ctx.message.server.id, ctx.message.author.id, self.escape(txt))
		sql_all = sql_all.format(ctx.message.server.id, ctx.message.author.id)
		check_sql = "SELECT tag FROM `tags` WHERE tag={0} AND user={1} AND server is NULL"
		check_sql = check_sql.format(self.escape(txt), ctx.message.author.id)
		global_check_sql = "SELECT server FROM `tags` WHERE server={0} AND user={1} AND tag={2}"
		global_check_sql = global_check_sql.format(ctx.message.server.id, ctx.message.author.id, self.escape(txt))
		if txt == "all":
			self.cursor.execute(sql_all)
			self.cursor.commit()
			await self.bot.say(":white_check_mark: Removed `all` of your tags")
			return
		global_result = self.cursor.execute(global_check_sql).fetchall()
		if len(global_result) == 0:
			check_result = self.cursor.execute(check_sql).fetchall()
			if len(check_result) == 0:
				await self.bot.say(":x: Error: Tag \"{0}\" does not exist or you don't own it!".format(txt))
			else:
				self.cursor.execute(sql)
				self.cursor.commit()
				await self.bot.say(":white_check_mark: Removed Tag \"{0}\"".format(txt))
		else:
			self.cursor.execute(sql_server)
			self.cursor.commit()
			await self.bot.say(":white_check_mark: Removed Server Tag \"{0}\"".format(txt))

	@tag.command(name='edit', pass_context=True, no_pm=True)
	async def tag_edit(self, ctx, tag:str=None, *, txt:str=None):
		"""Edit a tag you own"""
		try:
			if tag is None:
				await self.bot.say("Error: Invalid Syntax\nPlease input the tags name\n`.tag edit <tag_name> <--this one <tag_edited_content>`")
				return
			if txt is None:
				await self.bot.say("Error: Invalid Syntax\nPlease input something to edit the tag with\n`.tag edit <tag_name> <tag_edited_content> <--this one`")
				return
			if len(txt) > 1500:
				await self.bot.say(":no_entry: Tag Text Limit <= 1500")
				return
			txt = self.tag_formatter(txt)
			edit_sql = "UPDATE `tags` SET content={0} WHERE tag={1} AND user={2} AND server is NULL"
			edit_sql = edit_sql.format(self.escape(txt), self.escape(tag), ctx.message.author.id)
			edit_server_sql = "UPDATE `tags` SET content={0} WHERE server={1} AND tag={2} AND user={3}"
			edit_server_sql = edit_server_sql.format(self.escape(txt), ctx.message.server.id, self.escape(tag), ctx.message.author.id)
			check_sql = "SELECT tag FROM `tags` WHERE tag={0} AND user={1} AND server is NULL"
			check_sql = check_sql.format(self.escape(tag), ctx.message.author.id)
			global_check_sql = "SELECT server FROM `tags` WHERE server={0} AND tag={1} AND user={2}"
			global_check_sql = global_check_sql.format(ctx.message.server.id, self.escape(tag), ctx.message.author.id)
			check_result = self.cursor.execute(check_sql).fetchall()
			if len(check_result) == 0:
				global_result = self.cursor.execute(global_check_sql).fetchall()
				if len(global_result) == 0:
					await self.bot.say(":x: Error: Tag \"{0}\" does not exist or you don't own it!".format(tag))
				else:
					self.cursor.execute(edit_server_sql)
					self.cursor.commit()
					await self.bot.say(":white_check_mark: Succesfuly edited server tag \"{0}\"".format(tag))
			else:
				self.cursor.execute(edit_sql)
				self.cursor.commit()
				await self.bot.say(":white_check_mark: Succesfuly edited tag \"{0}\"".format(tag))
		except Exception as e:
			print(e)

	@tag.command(name='view', aliases=['raw'], pass_context=True, no_pm=True)
	async def tag_view(self, ctx, *, txt:str=None):
		"""Raw text of a tag"""
		if txt is None:
		  await self.bot.say("Error: Invalid Syntax\nPlease input something to remove from your tags\n`.tag remove <tag_name>`")
		  return
		txt = self.tag_formatter(txt)
		view_sql = "SELECT content FROM `tags` WHERE tag={0}"
		view_sql = view_sql.format(self.escape(txt))
		view_server_sql = "SELECT content FROM `tags` WHERE server={0} AND tag={1}"
		view_server_sql = view_server_sql.format(ctx.message.server.id, self.escape(txt))
		check_sql = "SELECT tag FROM `tags` WHERE tag={0} AND server is NULL"
		check_sql = check_sql.format(self.escape(txt))
		global_check_sql = "SELECT server FROM `tags` WHERE server={0} AND tag={1}"
		global_check_sql = global_check_sql.format(ctx.message.server.id, self.escape(txt))
		check_result = self.cursor.execute(check_sql).fetchall()
		if len(check_result) == 0:
			await self.bot.say(":x:	Error: Tag \"{0}\" does not exists!".format(txt))
			return
		else:
			global_result = self.cursor.execute(global_check_sql).fetchall()
			if len(global_result) == 0:
				view_result = self.cursor.execute(view_sql).fetchall()
				content = view_result[0]['content']
			else:
				view_server_result = self.cursor.execute(view_server_sql).fetchall()
				content = view_server_result[0]['content']
		content = self.tag_formatter(content)
		await self.bot.say("**Raw Tag \"{0}\"**\n{1}".format(txt, content))

	@tag.command(name='view2', aliases=['raw2'], pass_context=True, no_pm=True)
	async def tag_view2(self, ctx, *, txt:str):
		"""Raw text of your tag in a codeblock"""
		if txt is None:
		  await self.bot.say("Error: Invalid Syntax\nPlease input something to remove from your tags\n`.tag remove <tag_name>`")
		  return
		txt = self.tag_formatter(txt)
		view_sql = "SELECT content FROM `tags` WHERE tag={0} AND server is NULL"
		view_sql = view_sql.format(self.escape(txt))
		view_server_sql = "SELECT content FROM `tags` WHERE server={0} AND tag={1}"
		view_server_sql = view_server_sql.format(ctx.message.server.id, self.escape(txt))
		check_sql = "SELECT tag FROM `tags` WHERE tag={0} AND server is NULL"
		check_sql = check_sql.format(self.escape(txt))
		global_check_sql = "SELECT server FROM `tags` WHERE server={0} AND tag={1}"
		global_check_sql = global_check_sql.format(ctx.message.server.id, self.escape(txt))
		check_result = self.cursor.execute(check_sql).fetchall()
		if len(check_result) == 0:
			await self.bot.say(":x:	Error: Tag \"{0}\" does not exists!".format(txt))
			return
		else:
			global_result = self.cursor.execute(global_check_sql).fetchall()
			if len(global_result) == 0:
				view_result = self.cursor.execute(view_sql).fetchall()
				content = view_result[0]['content']
			else:
				view_server_result = self.cursor.execute(view_server_sql).fetchall()
				content = view_server_result[0]['content']
		content = self.tag_formatter(content)
		await self.bot.say("**Raw Tag \"{0}\"**\n".format(txt)+code.format(content))

	@tag.group(name='list', aliases=['mytags'], pass_context=True, no_pm=True)
	async def tag_list(self, ctx, user:discord.User=None):
		"""List all your tags or a users"""
		try:
			if user == None:
				user = ctx.message.author
			sql = 'SELECT * FROM `tags` WHERE user={0}'
			sql = sql.format(user.id)
			result = self.cursor.execute(sql).fetchall()
			if len(result) == 0:
				await self.bot.say(":no_entry: User `{0}` does not own any tags!".format(user))
				return
			results = ""
			mention = False
			tag_len = 0
			for s in result:
				tag_len += len(s['tag'])
			if tag_len >= 1999:
				for s in result:
					if s['server'] == ctx.message.server.id:
						results += '-Server Tag (Current)- {0}\n'.format(s['tag'])
					elif s['server'] and s['server'] != ctx.message.server.id:
						continue
					else:
						results += s['tag'] + "\n"
				txt = StringIO(results)
				txt.seek(0)
				await self.bot.send_file(ctx.message.channel, txt, content=':warning: Tag list too large for discord text, results uploaded.', filename='taglist_{0}.txt'.format(user.name))
				del txt
			else:
				for s in result:
					t = s['tag'].replace('<@', '<@\u200b')
					if s['server'] == ctx.message.server.id:
						results += '**Server Tag**: `{0}` '.format(t)
					elif s['server'] != None and s['server'] != ctx.message.server.id:
						continue
					else:
						results += "`" + t + "` "
				await self.truncate(ctx.message.channel, "**List of {0}'s Tags**\n{1}".format(user.name, results))
		except Exception as e:
			await self.bot.say(e)

	@tag_list.command(name='all', aliases=['alltags'], pass_context=True, no_pm=True)
	async def tag_list_all(self, ctx):
		"""List All Tags"""
		try:
			sql = 'SELECT tag,server FROM `tags`'
			result = self.cursor.execute(sql).fetchall()
			if len(result) == 0:
				await self.bot.say(":no_entry: There are no tags!")
				return
			results = ""
			for s in result:
				if s['server']:
					results += 'Server Tag ({0}): {1}\n'.format(s['server'], s['tag'])
				else:
					results += s['tag'] + "\n"
			txt = StringIO(results)
			txt.seek(0)
			await self.bot.upload(txt, content=':warning: All tags!', filename='alltags.txt')
		except Exception as e:
			await self.bot.say(e)

	@tag.command(name='owner', aliases=['whoowns', 'whomade'], pass_context=True, no_pm=True)
	async def tag_owner(self, ctx, *, txt:str):
		"""Who owns a tag?"""
		txt = self.tag_formatter(txt)
		owner_sql = "SELECT user FROM `tags` WHERE tag={0} AND server is NULL"
		owner_sql = owner_sql.format(self.escape(txt))
		owner_server_sql = "SELECT user FROM `tags` WHERE tag={0} AND server={1}"
		owner_server_sql = owner_server_sql.format(self.escape(txt), ctx.message.server.id)
		check_sql = "SELECT tag FROM `tags` WHERE tag={0} AND server is NULL"
		check_sql = check_sql.format(self.escape(txt))
		global_check_sql = "SELECT server FROM `tags` WHERE server={0} AND tag={1}"
		global_check_sql = global_check_sql.format(ctx.message.server.id, self.escape(txt))
		check_result = self.cursor.execute(check_sql).fetchall()
		if len(check_result) == 0:
			await self.bot.say(":x:	Error: Tag \"{0}\" does not exists!".format(txt))
			return
		else:
			servertag = False
			global_result = self.cursor.execute(global_check_sql).fetchall()
			if len(global_result) == 0:
				result = self.cursor.execute(owner_sql).fetchall()
				tag_owner = result[0]['user']
			else:
				result = self.cursor.execute(owner_server_sql).fetchall()
				tag_owner = result[0]['user']
				servertag = True
		user = await self.bot.get_user_info(str(tag_owner))
		if servertag:
			server_msg = 'Server '
		else:
			server_msg = ''
		await self.bot.say(":information_source: {0}Tag \"{1}\" is owned by `{2}`".format(server_msg, txt, user))

	@tag.command(name='random', pass_context=True, no_pm=True)
	async def tag_random(self, ctx):
		"""Random tag"""
		try:
			sql = "SELECT * FROM `tags` ORDER BY RAND() LIMIT 1"
			result = self.cursor.execute(sql).fetchall()
			tag = result[0]['tag']
			content = result[0]['content']
			content = self.tag_formatter(content)
			content = await self.parser(ctx, content, ())
			await self.bot.say("**Tag: {0}**\n{1}".format(tag, content))
		except Exception as e:
			await self.bot.say(e)

	@tag.group(name='search', aliases=['find'], pass_context=True, no_pm=True)
	async def tag_search(self, ctx, *, txt:str):
		"""Search for a tag"""
		txt = self.tag_formatter(txt)
		sql = "SELECT * FROM `tags` WHERE tag LIKE '%{0}%' AND (server IS NULL OR server={1})"
		sql = sql.format(self.escape(txt)[1:-1], ctx.message.server.id)
		result = self.cursor.execute(sql).fetchall()
		if len(result) == 0:
			await self.bot.say(":exclamation: No results found for tags like `{0}`".format(txt))
			return
		results = ""
		for s in result:
			owner_id = s['user']
			tag = s['tag']
			tag = self.tag_formatter(tag)
			if owner_id == ctx.message.author.id:
				results += "Tag: `{0}` | Owner: <@{1}>\n".format(tag, owner_id)
			else:
				user = await self.bot.get_user_info(str(owner_id))
				results += "Tag: `{0}` | Owner: **{1}**\n".format(tag, user)
		await self.truncate(ctx.message.channel, ":white_check_mark: Results:\n{1}".format(txt, results))

	@tag_search.command(name='content', pass_context=True, no_pm=True)
	async def tag_search_content(self, ctx, *, txt:str):
		txt = self.tag_formatter(txt)
		sql = "SELECT * FROM `tags` WHERE content LIKE {0} AND server IS NOT NULL"
		sql = sql.format("%"+self.escape(txt)+"%")
		result = self.cursor.execute(sql).fetchall()
		if len(result) == 0:
			await self.bot.say(":exclamation: No results found for tags with content like `{0}`".format(txt))
			return
		results = ""
		for s in result:
			owner_id = s['user']
			tag = s['tag']
			tag = self.tag_formatter(tag)
			results += "Tag Name: {0} | Owner: <@{1}>\n".format(tag, owner_id)
		await self.bot.say("**Results For Tags With Content Like `{0}`**\n{1}".format(txt, results))

	@tag.group(name='forceremove', pass_context=True, no_pm=True)
	@checks.is_owner()
	async def tag_fm(self, ctx, *, txt:str=None):
		"""Force remove a tag"""
		if txt is None:
			await self.bot.say(":no_entry: Please Input a Tag for the user to delete!")
			return
		txt = self.tag_formatter(txt)
		sql = "DELETE FROM `tags` WHERE tag={0} AND server IS NULL"
		sql = sql.format(self.escape(txt))
		sql_server = "DELETE FROM `tags` WHERE server={0} AND tag={1}"
		sql_server = sql_server.format(ctx.message.server.id, self.escape(txt))
		check_sql = "SELECT tag FROM `tags` WHERE tag={0} AND server IS NULL"
		check_sql = check_sql.format(self.escape(txt))
		global_check_sql = "SELECT server FROM `tags` WHERE server={0} AND tag={1}"
		global_check_sql = global_check_sql.format(ctx.message.server.id, self.escape(txt))
		check_result = self.cursor.execute(check_sql).fetchall()
		if len(check_result) == 0:
			await self.bot.say(":x:	Error: Tag \"{0}\" does not exists!".format(txt))
			return
		else:
			global_result = self.cursor.execute(global_check_sql).fetchall()
			if len(global_result) == 0:
				self.cursor.execute(sql)
				self.cursor.commit()
				await self.bot.say(":white_check_mark: Force Removed Tag \"{0}\"".format(txt))
			else:
				self.cursor.execute(sql_server)
				self.cursor.commit()
				await self.bot.say(":white_check_mark: Force Removed Server Tag \"{0}\"".format(txt))

	@tag_fm.command(name='user', pass_context=True, no_pm=True)
	async def tag_fm_user(self, ctx, user:discord.User=None, *, txt:str):
		if user is None:
			await self.bot.say(":no_entry: Please Input a User!")
			return
		if txt is None:
			await self.bot.say(":no_entry: Please Input a Tag for the user to delete!")
			return
		txt = self.tag_formatter(txt)
		owner_id = user.id	
		sql = "DELETE FROM `tags` WHERE tag={0} AND user={1} AND server IS NULL"
		sql = sql.format(self.escape(txt), owner_id)
		sql_server = "DELETE FROM `tags` WHERE server={0} AND user={1} tag={2}"
		sql_server = sql_server.format(ctx.message.server.id, owner_id, self.escape(txt))
		check_sql = "SELECT tag FROM `tags` WHERE tag={0} AND user={1} AND server IS NULL"
		check_sql = check_sql.format(self.escape(txt), owner_id)
		global_check_sql = "SELECT server FROM `tags` WHERE server={0} AND user={1} AND tag={2}"
		global_check_sql = global_check_sql.format(ctx.message.server.id, owner_id, self.escape(txt))
		check_result = self.cursor.execute(check_sql).fetchall()
		if len(check_result) == 0:
			await self.bot.say(":x:	Error: Tag \"{0}\" by user `{1}` does not exists!".format(txt, user.name))
			return
		else:
			global_result = self.cursor.execute(global_check_sql).fetchall()
			if len(global_result) == 0:
				self.cursor.execute(sql)
				self.cursor.commit()
			else:
				self.cursor.execute(sql_server)
				self.cursor.commit()
		await self.bot.say(":white_check_mark: Force Removed Tag \"{0}\" owned by `{1}`".format(txt, user.name))

	@tag.command(name='gift', pass_context=True, no_pm=True)
	async def tag_gift(self, ctx, tag:str, user:discord.User):
		"""Gift/Give a Tag to a User\nTransfer Ownership"""
		tag = self.tag_formatter(tag)
		sql = "UPDATE `tags` SET user={0} WHERE tag={1} AND user={2} AND server is NULL"
		sql = sql.format(user.id, self.escape(tag), ctx.message.author.id)
		server_sql = "UPDATE `tags` SET user={3} WHERE server={0} AND tag={1} AND user={2}"
		server_sql = server_sql.format(ctx.message.server.id, self.escape(tag), ctx.message.author.id, user.id)
		check_sql = "SELECT tag FROM `tags` WHERE tag={0} AND user={1} AND server is NULL"
		check_sql = check_sql.format(self.escape(tag), ctx.message.author.id)
		global_check_sql = "SELECT server FROM `tags` WHERE server={0} AND tag={1} AND user={2}"
		global_check_sql = global_check_sql.format(ctx.message.server.id, self.escape(tag), ctx.message.author.id)
		check_result = self.cursor.execute(check_sql).fetchall()
		if len(check_result) == 0:
			await self.bot.say(":x:	Error: Tag \"{0}\" does not exist or you don't own it!".format(tag))
			return
		else:
			global_result = self.cursor.execute(global_check_sql).fetchall()
			if len(global_result) == 0:
				self.cursor.execute(sql)
				self.cursor.commit()
				await self.bot.say(":white_check_mark: Gifted Tag \"{0}\" to `{1}`".format(tag, user))
			else:
				self.cursor.execute(server_sql)
				self.cursor.commit()
				await self.bot.say(":white_check_mark: Gifted Server Tag \"{0}\" to `{1}`".format(tag, user))

	@tag.command(name='rename', pass_context=True, no_pm=True)
	async def tag_rename(self, ctx, tag:str, new:str):
		"""Rename your tag"""
		tag = self.tag_formatter(tag)
		sql = "UPDATE `tags` SET tag={0} WHERE tag={1} AND user={2} AND server IS NULL"
		sql = sql.format(self.escape(new), self.escape(tag), ctx.message.author.id)
		server_sql = "UPDATE `tags` SET tag={0} WHERE server={1} AND tag={2} AND user={3}"
		server_sql = server_sql.format(self.escape(new), ctx.message.server.id, self.escape(tag), ctx.message.author.id)
		check_sql = "SELECT tag FROM `tags` WHERE tag={0} AND user={1} AND server IS NULL"
		check_sql = check_sql.format(self.escape(tag), ctx.message.author.id)
		tag_check_sql = "SELECT * FROM `tags` WHERE tag={0}"
		tag_check_sql = tag_check_sql.format(self.escape(new))
		global_check_sql = "SELECT server FROM `tags` WHERE server={0} AND tag={1} AND user={2}"
		global_check_sql = global_check_sql.format(ctx.message.server.id, self.escape(tag), ctx.message.author.id)
		check_result = self.cursor.execute(check_sql).fetchall()
		tag_check_results = self.cursor.execute(tag_check_sql).fetchall()
		if len(check_result) == 0:
			await self.bot.say(":x:	Error: Tag \"{0}\" does not exist or you don't own it!".format(tag))
			return
		elif len(tag_check_results) != 0:
			await self.bot.say(':no_entry: Tag with name \"{0}\" already exists.'.format(new))
			return
		else:
			global_result = self.cursor.execute(global_check_sql).fetchall()
			if len(global_result) == 0:
				self.cursor.execute(sql)
				self.cursor.commit()
				await self.bot.say(":white_check_mark: Renamed Tag \"{0}\" to {1}".format(tag, new))
			else:
				self.cursor.execute(server_sql)
				self.cursor.commit()
				await self.bot.say(":white_check_mark: Renamed Server Tag \"{0}\" to {1}".format(tag, new))

def setup(bot):
	bot.add_cog(Tags(bot))
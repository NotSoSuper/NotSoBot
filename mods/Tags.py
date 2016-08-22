import asyncio
import discord
import pymysql
import os
import re
import random
import math
import io
import sys, traceback
import linecache
from io import StringIO
from itertools import islice, cycle
from subprocess import check_output
from discord.ext import commands
from utils import checks

cool = "```xl\n{0}\n```"
code = "```py\n{0}\n```"

sql_injection = ['DROP', 'FROM', 'TABLE', 'SELECT', 'SELECT *', 'ALTER', 'UPDATE', 'INSERT', 'DELETE']

def check_int(k):
	if k[0] in ('-', '+'):
		return k[1:].isdigit()
	return k.isdigit()

class Tags():
	def __init__(self, bot):
		self.bot = bot
		self.connection = bot.mysql.connection
		self.cursor = bot.mysql.cursor
		self.discord_path = bot.path.discord
		self.files_path = bot.path.files

	def tag_formatter(self, s:str):
		if len(s) > 1500:
			return s[:1500]+"\n:warning: Tag Truncated\nTag Text limit <= 1500"
		s = s.encode("utf-8")
		s = s.decode('utf-8', 'ignore')
		s = u'\u180E' + s
		s = s.replace('@everyone', '@\u200beveryone')
		s = s.replace('@here', '@\u200bhere')
		s = s.replace("'", "\'")
		s = s.replace('"', "'")
		return s

	async def parser(self, ctx, txt:str, after:str=None):
# -------------------------STATIC {} SCRIPTING-------------------------
		regex_2 = r"\{(.+?)\}"
		match_2 = re.compile(regex_2).findall(txt)
		for s in match_2:
			txt = txt.replace("{user}", ctx.message.author.name)
			txt = txt.replace("{id}", ctx.message.author.id)
			txt = txt.replace("{usermention}", ctx.message.author.mention)
			if ctx.message.author.nick != None:
				txt = txt.replace("{nick}", ctx.message.author.nick)
			else:
				txt = txt.replace("{nick}", ctx.message.author.name)
			txt = txt.replace("{discrim}", ctx.message.author.discriminator)
			txt = txt.replace("{server}", ctx.message.server.name)
			txt = txt.replace("{serverid}", ctx.message.server.id)
			txt = txt.replace("{channel}", ctx.message.channel.name)
			txt = txt.replace("{channelid}", ctx.message.channel.id)
			if after != None and "{args}" in txt:
				txt = txt.replace("{args}", after)
			else:
				txt = txt.replace("{args}", "")
			if after != None and "{arg:" in txt:
				a = after.split()
				pos = s.replace("arg:", "")
				txt = txt.replace("{{arg:{0}}}".format(pos), a[int(pos)])
			else:
				pos = s.replace("arg:", "")
				txt = txt.replace("{{arg:{0}}}".format(pos), "")
			if after != None and "{argslen}" in txt:
				a = after.split()
				txt = txt.replace("{argslen}", str(len(a)))
			else:
				txt = txt.replace("{argslen}", "0")
			txt = txt.replace("{avatar}", "https://cdn.discordapp.com/avatars/{0}/{1}.jpg".format(ctx.message.author.id, ctx.message.author.avatar))
			if "{randuser}" in txt:
				m_c = len(ctx.message.server.members)
				rand = random.randint(1, m_c)
				count = 0
				random_user = ""
				for member in ctx.message.server.members:
					if count == rand:
						random_user = member
					else:
						count += 1
						continue
				txt = txt.replace("{randuser}", random_user.name)
			if "{randonline}" in txt:
				m_c = len(ctx.message.server.members)
				rand = random.randint(1, m_c)
				count = 1
				random_online_user = ""
				for member in ctx.message.server.members:
					if member.status == discord.Status.online:
						if count == rand:
							random_online_user = member.name
							break
						else:
							count += 1
							continue
					else:
						continue
				txt = txt.replace("{randonline}", random_online_user)
			if "{randchannel}" in txt:
				c_c = len(ctx.message.server.channels)
				rand = random.randint(1, c_c)
				count = 0
				for channel in ctx.message.server.channels:
					if count == rand:
						random_channel = channel.name
					else:
						count += 1
						continue
				txt = txt.replace("{randchannel}", random_channel)
# -------------------------DYNAMIC {s:s|s} SCRIPTING-------------------------
		regex_1 = r"\{(.+?):(.+?)\|(.+?)\}"
		match_1 = re.compile(regex_1).findall(txt)
		for s in match_1:
			if len(match_1) >= 1 and len(match_1[0]) < 3:
				return "Invalid replace/range scripting function, incorrect number of arguments passed in for \n{function:arg1|arg2} (arg1 and arg2 must have value)."
			arg = s[1]
			arg2 = s[2]
			if s[0] == "replace":
				txt = txt.replace("{{replace:{0}|{1}}}".format(arg, arg2), "")
				txt = re.sub(arg, arg2, txt)
			elif s[0] == "range":
				if check_int(arg) and check_int(arg2):
					rand = random.randint(int(arg), int(arg2))
					txt = txt.replace("{{range:{0}|{1}}}".format(arg, arg2), str(rand))
				else:
					txt = txt.replace("{{range:{0}|{1}}}".format(arg, arg2), "Range: Invalid Numbers")
# -------------------------IF/CONDITIONS SCRIPTING-------------------------
		if_regex = r"^\{(.+?):(.+?)\|(.+?)\|(.+?)\|then:(.+?)\|else:(.+?)\}$"
		if_match = re.compile(if_regex).findall(txt)
		for s in if_match:
			# if len(if_match) >= 1 and s[0] == "if" and len(if_match[0]) != 6:
			# 	return "Invalid tag, incorrect number of arguments passed in for \n{if:something|condition|something|then:sometext|else:sometext} Valid Conditions/Comparisons: `|=| (Equal) |<| (Less then) |>| (Greater then)`." # |~| (Rounded equal, Case-insensitive)
			if_arg = s[1]
			conditional = s[2]
			if_check_arg = s[3]
			then_arg = s[4]
			else_arg = s[5]
			if conditional == "=":
				if if_arg == if_check_arg:
					txt = txt.replace("{{if:{0}|{1}|{2}|then:{3}|else:{4}}}".format(if_arg, conditional, if_check_arg, then_arg, else_arg), then_arg)
				else:
					txt = txt.replace("{{if:{0}|{1}|{2}|then:{3}|else:{4}}}".format(if_arg, conditional, if_check_arg, then_arg, else_arg), else_arg)
			elif conditional == "<":
				if check_int(if_arg) and check_int(if_check_arg) and int(if_arg) < int(if_check_arg):
					txt = txt.replace("{{if:{0}|{1}|{2}|then:{3}|else:{4}}}".format(if_arg, conditional, if_check_arg, then_arg, else_arg), then_arg)
				elif check_int(if_arg) and check_int(if_check_arg):
					txt = txt.replace("{{if:{0}|{1}|{2}|then:{3}|else:{4}}}".format(if_arg, conditional, if_check_arg, then_arg, else_arg), else_arg)
				elif len(if_arg) < len(if_check_arg):
					txt = txt.replace("{{if:{0}|{1}|{2}|then:{3}|else:{4}}}".format(if_arg, conditional, if_check_arg, then_arg, else_arg), then_arg)
				else:
					txt = txt.replace("{{if:{0}|{1}|{2}|then:{3}|else:{4}}}".format(if_arg, conditional, if_check_arg, then_arg, else_arg), else_arg)
			elif conditional == ">":
				if check_int(if_arg) and check_int(if_check_arg) and int(if_arg) > int(if_check_arg):
					txt = txt.replace("{{if:{0}|{1}|{2}|then:{3}|else:{4}}}".format(if_arg, conditional, if_check_arg, then_arg, else_arg), then_arg)
				elif check_int(if_arg) and check_int(if_check_arg):
					txt = txt.replace("{{if:{0}|{1}|{2}|then:{3}|else:{4}}}".format(if_arg, conditional, if_check_arg, then_arg, else_arg), else_arg)
				elif len(if_arg) > len(if_check_arg):
					txt = txt.replace("{{if:{0}|{1}|{2}|then:{3}|else:{4}}}".format(if_arg, conditional, if_check_arg, then_arg, else_arg), then_arg)
				else:
					txt = txt.replace("{{if:{0}|{1}|{2}|then:{3}|else:{4}}}".format(if_arg, conditional, if_check_arg, then_arg, else_arg), else_arg)
# -------------------------DYNAMIC {*:*} SCRIPTING-------------------------
		regex_3 = r"\{(.+?):(.+?)\}"
		match_3 = re.compile(regex_3).findall(txt)
		for s in match_3:
			if s[0] == "choose":
				split_c = s[1].split("|")
				txt = txt.replace("{{choose:{0}}}".format(s[1]), random.choice(split_c))
			elif s[0] == "lua":
				path = '/root/discord/files/lua/script.lua'
				f = open(path,'w')
				clean_lua = s[1].replace('"', "\'")
				if "function" in clean_lua:
					f.write('local sandbox = require"sandbox"\nlocal sf = sandbox.protect({0})\nprint(sf())'.format(clean_lua))
				else:
					f.write('local sandbox = require"sandbox"\nsandbox.run("{0}")'.format(clean_lua))
				f.close()
				try:
					lua = check_output(["luajit", "/root/discord/files/lua/script.lua"]).decode()
				except Exception as e:
					lua = ":warning: Lua Script Error or Loop Quota Exceeded"
				txt = txt.replace("{{lua:{0}}}".format(s[1]), str(lua))
				open(path, 'w').close()
			elif s[0] == "math":
				split = s[1].split("|")
				math_result = ""
				math_count = len(split)
				math_c = 1
				for k in split:
					if check_int(k):
						math_c += 1
						math_result += k
						if math_c == math_count:
							result = str(eval(math_result))
							txt = txt.replace("{{math:{0}}}".format(s[1]), result)
						else:
							continue
					else:
						math_c += 1
						math_result += k
		if len(txt) > 1500:
			return ":no_entry: **Truncated**\nTag Output Too Long (<= 1500)\n {0}".format(txt[:1500])
		else:
			return txt

	@commands.group(pass_context=True, invoke_without_command=True, aliases=['t', 'ta', 'tags'])
	async def tag(self, ctx, txt:str, *after):
		"""Base command for tags, call it with a valid tag to display a tag"""
		txt = self.tag_formatter(txt)
		exists_sql = 'SELECT tag FROM `tags` WHERE tag="{0}" AND server=""'
		exists_sql = exists_sql.format(txt)
		self.cursor.execute(exists_sql)
		exists_result = self.cursor.fetchall()
		if len(exists_result) == 0:
			await self.bot.say(":no_entry: Tag \"{0}\" does not exist!".format(txt))
			return
		check_sql = 'SELECT server FROM `tags` WHERE server={0} AND tag="{1}"'
		check_sql = check_sql.format(ctx.message.server.id, txt)
		self.cursor.execute(check_sql)
		check_result = self.cursor.fetchall()
		not_global = True
		if len(check_result) == 0:
			pass
		else:
			not_global = False
		if not_global:
			sql = 'SELECT content FROM `tags` WHERE tag="{0}" AND server=""'
			sql = sql.format(txt)
		else:
			sql = 'SELECT content FROM `tags` WHERE server={0} AND tag="{1}"'
			sql = sql.format(ctx.message.server.id, txt)
		self.cursor.execute(sql)
		result = self.cursor.fetchall()
		content = result[0]['content']
		content = await self.parser(ctx, content, after)
		content = self.tag_formatter(content)
		# await self.bot.say("**Tag: {0}**\n{1}".format(txt, content))
		await self.bot.say("{0}".format(content))

	@tag.command(name='add', aliases=['create', 'make'], pass_context=True)
	async def _tag_add(self, ctx, tag:str=None, *, txt:str=None):
		"""Add a tag"""
		if tag == None:
			await self.bot.say("Error: Invalid Syntax\nPlease input the tags name\n`.tag add <tag_name> <--this one <tag_content>`")
			return
		if txt == None:
			await self.bot.say("Error: Invalid Syntax\nPlease input something for the tag to contain\n`.tag add <tag_name> <tag_content> <--this one`")
			return
		if len(txt) > 1500:
			await self.bot.say(":no_entry: Tag Text Limit <= 1500")
			return
		txt = self.tag_formatter(txt)
		for s in sql_injection:
			if s in tag:
				await self.bot.say("Error: `Exploit Detected`\nPlease try another tag.")
				return
			elif s in txt:
				await self.bot.say("Error: `Exploit Detected`\nPlease try another tag.")
				return
			if len(ctx.message.mentions) > 0:
				mention = True
		tag_sql = "INSERT INTO `tags` (`id`, `tag`, `content`, `server_created`) VALUES (%s, %s, %s, %s)"
		server_sql = "INSERT INTO `tags` (`server`, `id`, `tag`, `content`) VALUES (%s, %s, %s, %s)"
		check_sql = 'SELECT tag,server_created FROM `tags` WHERE tag="{0}" AND server=""'
		check_sql = check_sql.format(tag)
		global_check_sql = 'SELECT server FROM `tags` WHERE server={0} AND tag="{1}"'
		global_check_sql = global_check_sql.format(ctx.message.server.id, tag)
		self.cursor.execute(check_sql)
		check_result = self.cursor.fetchall()
		if len(check_result) == 0:
			self.cursor.execute(tag_sql, (ctx.message.author.id, tag, txt, ctx.message.server.id))
			self.connection.commit()
		else:
			self.cursor.execute(global_check_sql)
			global_result = self.cursor.fetchall()
			if len(global_result) == 0 and check_result[0]['server_created'] != ctx.message.server.id:
				self.cursor.execute(server_sql, (ctx.message.server.id, ctx.message.author.id, tag, txt))
				self.connection.commit()
			else:
				await self.bot.say(":no_entry: Tag \"{0}\" already exists!".format(tag))
				return
		await self.bot.say(":white_check_mark: Added tag \"{0}\"".format(tag))

	@tag.command(name='remove', aliases=['delete'], pass_context=True)
	async def _tag_remove(self, ctx, *, txt:str=None):
		""""Remove a tag you own"""
		if txt == None:
			await self.bot.say("Error: Invalid Syntax\nPlease input something to remove from your tags\n`.tag remove <tag_name>`")
			return
		for s in sql_injection:
			if s in txt:
				await self.bot.say("Error: `Exploit Detected`\nPlease try another tag.")
				return
		sql = 'DELETE FROM `tags` WHERE id={0} AND server="" AND tag="{1}"'
		sql_server = 'DELETE FROM `tags` WHERE server={0} AND id={1} AND tag="{2}"'
		sql_all = "DELETE FROM `tags` WHERE id={1}"
		sql = sql.format(ctx.message.author.id, txt)
		sql_server = sql_server.format(ctx.message.server.id, ctx.message.author.id, txt)
		sql_all = sql_all.format(ctx.message.server.id, ctx.message.author.id)
		check_sql = 'SELECT tag FROM `tags` WHERE tag="{0}" AND server=""'
		check_sql = check_sql.format(txt)
		global_check_sql = 'SELECT server FROM `tags` WHERE server={0} AND tag="{1}"'
		global_check_sql = global_check_sql.format(ctx.message.server.id, txt)
		self.cursor.execute(check_sql)
		check_result = self.cursor.fetchall()
		if len(check_result) == 0 and txt != "all":
			await self.bot.say(":x: Error: Tag \"{0}\" does not exists/you don't own it!".format(txt))
			return
		elif txt == "all":
			self.cursor.execute(sql_all)
			self.connection.commit()
			await self.bot.say(":white_check_mark: Removed `all` of your tags")
			return
		else:
			self.cursor.execute(global_check_sql)
			global_result = self.cursor.fetchall()
			if len(global_result) == 0:
				self.cursor.execute(sql)
				self.connection.commit()
			else:
				self.cursor.execute(sql_server)
				self.connection.commit()
		await self.bot.say(":white_check_mark: Removed tag \"{0}\"".format(txt))

	@tag.command(name='edit', pass_context=True)
	async def _tag_edit(self, ctx, tag:str=None, *, txt:str=None):
		"""Edit a tag you own"""
		if tag == None:
			await self.bot.say("Error: Invalid Syntax\nPlease input the tags name\n`.tag edit <tag_name> <--this one <tag_edited_content>`")
			return
		if txt == None:
			await self.bot.say("Error: Invalid Syntax\nPlease input something to edit the tag with\n`.tag edit <tag_name> <tag_edited_content> <--this one`")
			return
		if len(txt) > 1500:
			await self.bot.say(":no_entry: Tag Text Limit <= 1500")
			return
		for s in sql_injection:
			if s in tag:
				await self.bot.say("Error: `Exploit Detected`\nPlease try another tag.")
				return
			elif s in txt:
				await self.bot.say("Error: `Exploit Detected`\nPlease try another tag.")
				return
		txt = self.tag_formatter(txt)
		edit_sql = 'UPDATE `tags` SET content="{0}" WHERE tag="{1}" AND id={2} AND server=""'
		edit_sql = edit_sql.format(txt, tag, ctx.message.author.id)
		edit_server_sql = 'UPDATE `tags` SET content="{0}" WHERE server={1} AND tag="{2}" AND id={3}'
		edit_server_sql = edit_server_sql.format(txt, ctx.message.server.id, tag, ctx.message.author.id)
		check_sql = 'SELECT tag FROM `tags` WHERE tag="{0}" AND id={1} AND server=""'
		check_sql = check_sql.format(tag, ctx.message.author.id)
		global_check_sql = 'SELECT server FROM `tags` WHERE server={0} AND tag="{1}" AND id={2}'
		global_check_sql = global_check_sql.format(ctx.message.server.id, tag, ctx.message.author.id)
		self.cursor.execute(check_sql)
		check_result = self.cursor.fetchall()
		if len(check_result) == 0:
			await self.bot.say(":x:	Error: Tag \"{0}\" does not exists/you don't own it!".format(tag))
			return
		else:
			self.cursor.execute(global_check_sql)
			global_result = self.cursor.fetchall()
			if len(global_result) == 0:
				self.cursor.execute(edit_sql)
				self.connection.commit()
			else:
				self.cursor.execute(edit_server_sql)
				self.connection.commit()
		await self.bot.say(":white_check_mark: Succesfuly edited tag \"{0}\"".format(tag))

	@tag.command(name='view', aliases=['raw'], pass_context=True)
	async def _tag_view(self, ctx, *, txt:str=None):
		"""Raw text of a tag"""
		if txt == None:
		  await self.bot.say("Error: Invalid Syntax\nPlease input something to remove from your tags\n`.tag remove <tag_name>`")
		  return
		for s in sql_injection:
		  if s in txt:
		    await self.bot.say("Error: `Exploit Detected`\nPlease try another tag.")
		    return
		view_sql = 'SELECT content FROM `tags` WHERE tag="{0}"'
		view_sql = view_sql.format(txt)
		view_server_sql = 'SELECT content FROM `tags` WHERE server={0} AND tag="{1}"'
		view_server_sql = view_server_sql.format(ctx.message.server.id, txt)
		check_sql = 'SELECT tag FROM `tags` WHERE tag="{0}" AND server=""'
		check_sql = check_sql.format(txt)
		global_check_sql = 'SELECT server FROM `tags` WHERE server={0} AND tag="{1}"'
		global_check_sql = global_check_sql.format(ctx.message.server.id, txt)
		self.cursor.execute(check_sql)
		check_result = self.cursor.fetchall()
		if len(check_result) == 0:
			await self.bot.say(":x:	Error: Tag \"{0}\" does not exists!".format(txt))
			return
		else:
			self.cursor.execute(global_check_sql)
			global_result = self.cursor.fetchall()
			if len(global_result) == 0:
				self.cursor.execute(view_sql)
				view_result = self.cursor.fetchall()
				content = view_result[0]['content']
			else:
				self.cursor.execute(view_server_sql)
				view_server_result = self.cursor.fetchall()
				content = view_server_result[0]['content']
		content = self.tag_formatter(content)
		await self.bot.say("**Raw Tag \"{0}\"**\n{1}".format(txt, content))

	@tag.command(name='view2', aliases=['raw2'], pass_context=True)
	async def _tag_view2(self, ctx, *, txt:str):
		"""Raw text of your tag in a codeblock"""
		if txt == None:
		  await self.bot.say("Error: Invalid Syntax\nPlease input something to remove from your tags\n`.tag remove <tag_name>`")
		  return
		for s in sql_injection:
		  if s in txt:
		    await self.bot.say("Error: `Exploit Detected`\nPlease try another tag.")
		    return
		view_sql = 'SELECT content FROM `tags` WHERE tag="{0}" AND server=""'
		view_sql = view_sql.format(txt)
		view_server_sql = 'SELECT content FROM `tags` WHERE server={0} AND tag="{1}"'
		view_server_sql = view_server_sql.format(ctx.message.server.id, txt)
		check_sql = 'SELECT tag FROM `tags` WHERE tag="{0}" AND server=""'
		check_sql = check_sql.format(txt)
		global_check_sql = 'SELECT server FROM `tags` WHERE server={0} AND tag="{1}"'
		global_check_sql = global_check_sql.format(ctx.message.server.id, txt)
		self.cursor.execute(check_sql)
		check_result = self.cursor.fetchall()
		if len(check_result) == 0:
			await self.bot.say(":x:	Error: Tag \"{0}\" does not exists!".format(txt))
			return
		else:
			self.cursor.execute(global_check_sql)
			global_result = self.cursor.fetchall()
			if len(global_result) == 0:
				self.cursor.execute(view_sql)
				view_result = self.cursor.fetchall()
				content = view_result[0]['content']
			else:
				self.cursor.execute(view_server_sql)
				view_server_result = self.cursor.fetchall()
				content = view_server_result[0]['content']
		content = self.tag_formatter(content)
		await self.bot.say("**Raw Tag \"{0}\"**\n".format(txt)+code.format(content))

	@tag.group(name='list', aliases=['mytags'], pass_context=True, invoke_without_command=True)
	async def _tag_list(self, ctx, user:discord.User=None):
		"""List all your tags or a users"""
		sql = 'SELECT tag FROM `tags` WHERE id={0} AND server="" OR server={1}'
		if user == None:
			sql = sql.format(ctx.message.author.id, ctx.message.server.id)
		else:
			sql = sql.format(user.id, ctx.message.server.id)
		self.cursor.execute(sql)
		result = self.cursor.fetchall()
		if len(result) == 0 and user == None:
			await self.bot.say(":no_entry: {0} does not own any tags!".format(ctx.message.author.mention))
			return
		elif len(result) == 0 and user != None:
			await self.bot.say(":no_entry: User `{0}` does not own any tags!".format(user.name))
			return
		results = ""
		mention = False
		tag_len = 0
		for s in result:
			tag_len += len(s['tag'])
		if tag_len > 1500:
			for s in result:
			  results += s['tag'] + "\n"
			txt = StringIO(results.encode('utf-8'))
			if user == None:
				await self.bot.send_file(ctx.message.channel, txt.getvalue(), content=':warning: Tag list too large for discord text, results uploaded.', filename='taglist_{0}.txt'.format(ctx.message.author.name))
			else:
				await self.bot.send_file(ctx.message.channel, txt.getvalue(), content=':warning: Tag list too large for discord text, results uploaded.', filename='taglist_{0}.txt'.format(user.name))
			del txt
			return
		else:
			for s in result:
			  s['tag'] = s['tag'].replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
			  if "<@" in s['tag']:
			    results += s['tag'] + " "
			  else:
			    results += "`" + s['tag'] + "` "
		if user == None:
			await self.bot.say("**List of {0}'s Tags**\n{1}".format(ctx.message.author.mention, results))
		else:
			await self.bot.say("**List of {0}'s Tags**\n{1}".format(user.name, results))

	@_tag_list.command(name='all', aliases=['alltags'], pass_context=True, invoke_without_command=True)
	async def _tag_list_all(self, ctx):
		"""List All Tags"""
		sql = 'SELECT tag FROM `tags`'
		self.cursor.execute(sql)
		result = self.cursor.fetchall()
		if len(result) == 0:
			await self.bot.say(":no_entry: There are no tags!".format(ctx.message.author.mention))
			return
		results = ""
		mention = False
		for s in result:
			results += s['tag'] + "\n"
		txt = StringIO(results.encode('utf-8'))
		await self.bot.send_file(ctx.message.channel, txt.getvalue(), content=':warning: All tags.', filename='tags.txt')

	@tag.command(name='owner', aliases=['whoowns', 'whomade'], pass_context=True)
	async def _tag_owner(self, ctx, *, txt:str):
		"""Who owns a tag?"""
		for s in sql_injection:
		  if s in txt:
		    await self.bot.say("Error: `Exploit Detected`\nPlease try another tag.")
		    return
		owner_sql = 'SELECT id FROM `tags` WHERE tag="{0}" AND server=""'
		owner_sql = owner_sql.format(txt)
		owner_server_sql = 'SELECT id FROM `tags` WHERE tag="{0}" AND server={1}'
		owner_server_sql = owner_server_sql.format(txt, ctx.message.server.id)
		check_sql = 'SELECT tag FROM `tags` WHERE tag="{0}" AND server=""'
		check_sql = check_sql.format(txt)
		global_check_sql = 'SELECT server FROM `tags` WHERE server={0} AND tag="{1}"'
		global_check_sql = global_check_sql.format(ctx.message.server.id, txt)
		self.cursor.execute(check_sql)
		check_result = self.cursor.fetchall()
		if len(check_result) == 0:
			await self.bot.say(":x:	Error: Tag \"{0}\" does not exists!".format(txt))
			return
		else:
			self.cursor.execute(global_check_sql)
			global_result = self.cursor.fetchall()
			if len(global_result) == 0:
				self.cursor.execute(owner_sql)
				result = self.cursor.fetchall()
				tag_owner = result[0]['id']
			else:
				self.cursor.execute(owner_server_sql)
				result = self.cursor.fetchall()
				tag_owner = result[0]['id']
		user = None
		for server in self.bot.servers:
			if user == None:
				user = discord.Server.get_member(server, user_id=tag_owner)
			else:
				break
		if user == None:
			await self.bot.say(":white_check_mark: Tag \"{0}\" is owned by <@{1}> (Not on any servers I'm on)".format(txt, tag_owner))
		else:
			await self.bot.say(":white_check_mark: Tag \"{0}\" is owned by {1}".format(txt, user))

	@tag.command(name='random', pass_context=True, invoke_without_command=True)
	async def _tag_random(self, ctx):
		"""Random tag"""
		sql = "SELECT * FROM `tags` ORDER BY RAND() LIMIT 1"
		self.cursor.execute(sql)
		result = self.cursor.fetchall()
		tag = result[0]['tag']
		content = result[0]['content']
		content = self.tag_formatter(content)
		content = self.tag_formatter(content)
		content = await self.parser(ctx, content)
		await self.bot.say("Tag: {0}\n{1}".format(tag, content))

	@tag.group(name='search', aliases=['find'], pass_context=True)
	async def _tag_search(self, ctx, *, txt:str):
		"""Search for a tag"""
		for s in sql_injection:
		  if s in txt:
		    await self.bot.say("Error: `Exploit Detected`\nPlease try another tag.")
		    return
		sql = "SELECT * FROM `tags` WHERE tag LIKE '%{0}%'"
		sql = sql.format(txt)
		self.cursor.execute(sql)
		result = self.cursor.fetchall()
		if len(result) == 0:
			await self.bot.say(":exclamation: No results found for tags like `{0}`".format(txt))
			return
		results = ""
		for s in result:
			owner_id = s['id']
			tag = s['tag']
			tag = self.tag_formatter(tag)
			if owner_id == ctx.message.author.id:
				results += "Tag: `{0}` | Owner: <@{1}>\n".format(tag, owner_id)
			else:
				user = None
				for server in self.bot.servers:
					if user == None:
						user = discord.Server.get_member(server, user_id=owner_id)
					else:
						break
				if user != None:
					results += "Tag: {0} | Owner: `{1}`\n".format(tag, user)
				else:
					results += "Tag: {0} | Owner: <@{1}>\n".format(tag, owner_id)
		await self.bot.say("**Results For Tags Like `{0}`**\n{1}".format(txt, results))

	@_tag_search.command(name='content', pass_context=True)
	async def _tag_search_content(self, ctx, *, txt:str):
		for s in sql_injection:
		  if s in txt:
		    await self.bot.say("Error: `Exploit Detected`\nPlease try another tag.")
		    return
		sql = 'SELECT * FROM `tags` WHERE content LIKE "%{0}%"'
		sql = sql.format(txt)
		self.cursor.execute(sql)
		result = self.cursor.fetchall()
		if len(result) == 0:
			await self.bot.say(":exclamation: No results found for tags with content like `{0}`".format(txt))
			return
		results = ""
		for s in result:
			owner_id = s['id']
			tag = s['tag']
			tag = self.tag_formatter(tag)
			results += "Tag Name: {0} | Owner: <@{1}>\n".format(tag, owner_id)
		await self.bot.say("**Results For Tags With Content Like `{0}`**\n{1}".format(txt, results))

	@tag.group(name='forceremove', pass_context=True)
	@checks.is_owner()
	async def _tag_fm(self, ctx, *, txt:str=None):
		"""Force remove a tag"""
		if txt == None:
			await self.bot.say(":no_entry: Please Input a Tag for the user to delete!")
			return
		sql = 'DELETE FROM `tags` WHERE tag="{0}" AND server=""'
		sql = sql.format(txt)
		sql_server = 'DELETE FROM `tags` WHERE server={0} AND tag="{1}"'
		sql_server = sql_server.format(ctx.message.server.id, txt)
		check_sql = 'SELECT tag FROM `tags` WHERE tag="{0}" AND server=""'
		check_sql = check_sql.format(txt)
		global_check_sql = 'SELECT server FROM `tags` WHERE server={0} AND tag="{1}"'
		global_check_sql = global_check_sql.format(ctx.message.server.id, txt)
		self.cursor.execute(check_sql)
		check_result = self.cursor.fetchall()
		if len(check_result) == 0:
			await self.bot.say(":x:	Error: Tag \"{0}\" does not exists!".format(txt))
			return
		else:
			self.cursor.execute(global_check_sql)
			global_result = self.cursor.fetchall()
			if len(global_result) == 0:
				self.cursor.execute(sql)
				self.connection.commit()
			else:
				self.cursor.execute(sql_server)
				self.connection.commit()
		await self.bot.say(":white_check_mark: Force Removed Tag \"{0}\"".format(txt))

	@_tag_fm.command(name='user', pass_context=True)
	async def _tag_fm_user(self, ctx, user:discord.User=None, *, txt:str):
		if user == None:
			await self.bot.say(":no_entry: Please Input a User!")
			return
		if txt == None:
			await self.bot.say(":no_entry: Please Input a Tag for the user to delete!")
			return
		owner_id = user.id	
		sql = 'DELETE FROM `tags` WHERE tag="{0}" AND id={1} AND server=""'
		sql = sql.format(txt, owner_id)
		sql_server = 'DELETE FROM `tags` WHERE server={0} AND id={1} tag="{2}"'
		sql_server = sql_server.format(ctx.message.server.id, owner_id, txt)
		check_sql = 'SELECT tag FROM `tags` WHERE tag="{0}" AND id={1} AND server=""'
		check_sql = check_sql.format(txt, owner_id)
		global_check_sql = 'SELECT server FROM `tags` WHERE server={0} AND id={1} AND tag="{2}"'
		global_check_sql = global_check_sql.format(ctx.message.server.id, owner_id, txt)
		self.cursor.execute(check_sql)
		check_result = self.cursor.fetchall()
		if len(check_result) == 0:
			await self.bot.say(":x:	Error: Tag \"{0}\" by user `{1}` does not exists!".format(txt, user.name))
			return
		else:
			self.cursor.execute(global_check_sql)
			global_result = self.cursor.fetchall()
			if len(global_result) == 0:
				self.cursor.execute(sql)
				self.connection.commit()
			else:
				self.cursor.execute(sql_server)
				self.connection.commit()
		await self.bot.say(":white_check_mark: Force Removed Tag \"{0}\" owned by `{1}`".format(txt, user.name))

	@tag.command(name='gift', pass_context=True)
	async def _tag_gift(self, ctx, tag:str, user:discord.User):
		"""Gift/Give a Tag to a User\nTransfer Ownership"""
		sql = 'UPDATE `tags` SET id={0} WHERE tag="{1}" AND id={0} AND server=""'
		sql = sql.format(user.id, tag)
		server_sql = 'UPDATE `tags` SET id={3} WHERE server={0} AND tag="{1}" AND id={2}'
		server_sql = server_sql.format(ctx.message.server.id, tag, ctx.message.author.id, user.id)
		check_sql = 'SELECT tag FROM `tags` WHERE tag="{0}" AND id={1} AND server=""'
		check_sql = check_sql.format(tag, ctx.message.author.id)
		global_check_sql = 'SELECT server FROM `tags` WHERE server={0} AND tag="{1}" AND id={2}'
		global_check_sql = global_check_sql.format(ctx.message.server.id, tag, ctx.message.author.id)
		self.cursor.execute(check_sql)
		check_result = self.cursor.fetchall()
		if len(check_result) == 0:
			await self.bot.say(":x:	Error: Tag \"{0}\" does not exists/you don't own it!".format(tag))
			return
		else:
			self.cursor.execute(global_check_sql)
			global_result = self.cursor.fetchall()
			if len(global_result) == 0:
				self.cursor.execute(sql)
				self.connection.commit()
			else:
				self.cursor.execute(server_sql)
				self.connection.commit()
		await self.bot.say(":white_check_mark: Gifted Tag \"{0}\" to {1}".format(tag, user.mention))

def setup(bot):
    bot.add_cog(Tags(bot))
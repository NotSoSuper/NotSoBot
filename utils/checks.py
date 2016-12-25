from discord.ext import commands
import discord.utils
import json
import os

class No_Owner(commands.CommandError): pass
class No_Perms(commands.CommandError): pass
class No_Role(commands.CommandError): pass
class No_Admin(commands.CommandError): pass
class No_Mod(commands.CommandError): pass
class No_Sup(commands.CommandError): pass
class No_ServerandPerm(commands.CommandError): pass
class Nsfw(commands.CommandError): pass

owner_id = '130070621034905600'

def is_owner_check(message):
	if message.author.id == owner_id:
		return True
	raise No_Owner()

def is_owner():
	return commands.check(lambda ctx: is_owner_check(ctx.message))

def check_permissions(ctx, perms):
	msg = ctx.message
	if msg.author.id == owner_id:
		return True
	ch = msg.channel
	author = msg.author
	resolved = ch.permissions_for(author)
	if all(getattr(resolved, name, None) == value for name, value in perms.items()):
		return True
	return False

def role_or_perm(t, ctx, check, **perms):
	if check_permissions(ctx, perms):
		return True
	ch = ctx.message.channel
	author = ctx.message.author
	if ch.is_private:
		return False
	role = discord.utils.find(check, author.roles)
	if role is not None:
		return True
	if t:
		return False
	else:
		raise No_Role()

# def role_or_perm(t, ctx, check, **perms):
#   if check_permissions(ctx, perms):
#     return True
#   ch = ctx.message.channel
#   author = ctx.message.author
#   if ch.is_private:
#     return False
#   role = discord.utils.find(check, author.roles)
#   if role is not None:
#     return True
#   if t == 0:
#     raise No_Mod()
#   elif t == 1:
#     raise No_Admin()
#   else:
#     raise No_Role()

admin_perms = ['administrator', 'manage_server']
mod_perms = ['manage_messages', 'ban_members', 'kick_members']

mod_roles = ('mod', 'moderator')
def mod_or_perm(**perms):
	def predicate(ctx):
		if ctx.message.channel.is_private:
			return True
		if role_or_perm(True, ctx, lambda r: r.name.lower() in mod_roles, **perms):
			return True
		for role in ctx.message.author.roles:
			role_perms = []
			for s in role.permissions:
				role_perms.append(s)
			for s in role_perms:
				for x in mod_perms:
					if s[0] == x and s[1] == True:
						return True
				for x in admin_perms:
					if s[0] == x and s[1] == True:
						return True
		raise No_Mod()
	return commands.check(predicate)

admin_roles = ('admin', 'administrator', 'mod', 'moderator', 'owner', 'god', 'manager', 'boss')
def admin_or_perm(**perms):
	def predicate(ctx):
		if ctx.message.channel.is_private:
			return True
		if role_or_perm(True, ctx, lambda r: r.name.lower() in admin_roles, **perms):
			return True
		for role in ctx.message.author.roles:
			role_perms = []
			for s in role.permissions:
				role_perms.append(s)
			for s in role_perms:
				for x in admin_perms:
					if s[0] == x and s[1] == True:
						return True
		raise No_Admin()
	return commands.check(predicate)

def is_in_servers(*server_ids):
	def predicate(ctx):
		server = ctx.message.server
		if server is None:
			return False
		return server.id in server_ids
	return commands.check(predicate)

def server_and_perm(ctx, *server_ids, **perms):
	if ctx.message.channel.is_private:
		return False
	server = ctx.message.server
	if server is None:
		return False
	if server.id in server_ids:
		if check_permissions(ctx, perms):
			return True
		return False
	raise No_ServerandPerm()

def sup(ctx):
	server = ctx.message.server
	if server.id == "197938366530977793":
		return True
	raise No_Sup()

def nsfw():
	def predicate(ctx):
		channel = ctx.message.channel
		if channel.is_private:
			return True
		name = channel.name.lower()
		if name == 'nsfw' or name == '[nsfw]':
			return True
		elif name == 'no-nsfw' or name == 'sfw':
			raise Nsfw()
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
		raise Nsfw()
	return commands.check(predicate)

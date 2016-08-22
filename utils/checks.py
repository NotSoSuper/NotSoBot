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

with open(os.path.join(os.getenv('discord_path', '~/discord/'), "utils/config.json")) as f:
  config = json.load(f)

def is_owner_check(message):
  if message.author.id == config['ownerid']:
    return True
  raise No_Owner()

def is_owner():
  return commands.check(lambda ctx: is_owner_check(ctx.message))

def check_permissions(ctx, perms):
  msg = ctx.message
  if msg.author.id == config['ownerid']:
    return True
  ch = msg.channel
  author = msg.author
  resolved = ch.permissions_for(author)
  if all(getattr(resolved, name, None) == value for name, value in perms.items()):
    return True
  raise No_Perms()

def role_or_perm(ctx, check, **perms):
  if check_permissions(ctx, perms):
    return True
  ch = ctx.message.channel
  author = ctx.message.author
  if ch.is_private:
    return False
  role = discord.utils.find(check, author.roles)
  if role is not None:
    return True
  raise No_Role()

mod_roles = ('mod', 'moderator')
def mod_or_perm(**perms):
  def predicate(ctx):
    if role_or_perm(ctx, lambda r: r.name.lower() in mod_roles, **perms):
      return True
    raise No_Mod()
  return commands.check(predicate)

admin_roles = ('admin', 'administrator', 'mod', 'moderator', 'owner', 'god', 'manager', 'boss')
def admin_or_perm(**perms):
  def predicate(ctx):
    if role_or_perm(ctx, lambda r: r.name.lower() in admin_roles, **perms):
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
    if channel.name.lower() == 'nsfw':
      return True
    if channel.topic != None:
      if '{nsfw}' in channel.topic.lower() or '[nsfw]' in channel.topic.lower() or 'nsfw' == channel.topic.lower():
        return True
      if 'nsfw' in channel.topic.split() and 'sfw' not in channel.topic.split():
        return True
    raise Nsfw()
  return commands.check(predicate)

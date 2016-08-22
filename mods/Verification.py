import discord
import asyncio
import pymysql
import random
from discord.ext import commands
from utils import checks

cool = "```xl\n{0}\n```"
code = "```py\n{0}\n```"

class Verification():
  def __init__(self, bot):
    self.bot = bot
    self.connection = bot.mysql.connection
    self.cursor = bot.mysql.cursor

  @commands.group(pass_context=True, aliases=['onjoinverify', 'approval'], invoke_without_command=True)
  @checks.admin_or_perm(manage_server=True)
  async def verification(self, ctx, channel:discord.Channel=None, *, mentions:str=None):
    if ctx.message.server.me.permissions_in(ctx.message.channel).manage_roles == False and ctx.message.server.me.permissions_in(ctx.message.channel).manage_channels == False:
      if ctx.message.server.me.permissions_in(ctx.message.channel).administrator == False:
        await self.bot.say(":warning: `I need Administrator permission to make/add a role to mute on join`")
        return
    if channel == None:
      channel = ctx.message.channel
    sql = 'SELECT * FROM `verification` WHERE server={0}'
    sql = sql.format(ctx.message.server.id)
    self.cursor.execute(sql)
    result = self.cursor.fetchall()
    if len(result) == 0:
      if mentions == None:
        sql = "INSERT INTO `verification` (`server`, `channel`) VALUES (%s, %s)"
        self.cursor.execute(sql, (ctx.message.server.id, channel.id))
        self.connection.commit()
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
        self.connection.commit()
        await self.bot.say(":white_check_mark: Enabled user approval/verification on join, all requests will go to {0} (`verification <#discord_channel>` to change) and mention `{0}`!".format(channel.mention, ', '.join(mention_names)))
      permissions = discord.Permissions()
      permissions.read_messages = True
      try:
        await self.bot.create_role(ctx.message.server, name='Awaiting Approval', color=discord.Colour(int("FF0000", 16)), permissions=permissions)
      except Exception as e:
        print(e)
        await self.bot.say(":warning: For some reason I couldn't create the \"Awaiting Approval\" role and users won't be muted, please create it (same name) and disable all the permissions you don't want unapproved-users to have.\nMake sure I have the administrator permission!")
    elif channel == None:
      sql = 'UPDATE `verification` SET channel={0} WHERE server={1}'
      sql = sql.format(channel.id, ctx.message.server.id)
      self.connection.commit()
      await self.bot.say(":white_check_mark: Set approval/verification channel to {0}".format(channel.mention))
    else:
      sql = 'DELETE FROM `verification` WHERE server={0}'
      sql = sql.format(ctx.message.server.id)
      self.cursor.execute(sql)
      self.connection.commit()
      try:
        role = discord.utils.get(ctx.message.server.roles, name='Awaiting Approval')
      except:
        role = None
      try:
        await self.bot.delete_role(ctx.message.server, role)
      except discord.errors.Forbidden:
        await self.bot.say("could not remove role, you took my perms away :(")
      except discord.errors.NotFound:
        await self.bot.say("nice, you already removed the role")
      except:
        await self.bot.say("nice, you already removed the role")
      await self.bot.say(":negative_squared_cross_mark: **Disabled** user approval on join")

  @verification.command(name='mention', aliases=['mentions'], pass_context=True, invoke_without_command=True)
  @checks.admin_or_perm(manage_server=True)
  async def verification_mention(self, ctx, *mentions:str):
    if ctx.message.server.me.permissions_in(ctx.message.channel).manage_roles == False and ctx.message.server.me.permissions_in(ctx.message.channel).manage_channels == False:
      if ctx.message.server.me.permissions_in(ctx.message.channel).administrator == False:
        await self.bot.say(":warning: `I need Administrator permission to make/add a role to mute on join`")
        return
    sql = 'SELECT * FROM `verification` WHERE server={0}'
    sql = sql.format(ctx.message.server.id)
    self.cursor.execute(sql)
    result = self.cursor.fetchall()
    if len(result) == 0:
      await self.bot.say(":no_entry: This server does not have approval/verification turned on (`verification <#discord_channel>` to do so)!!!")
      return
    if len(mentions) == 0:
      sql = 'UPDATE `verification` SET mentions=NULL WHERE server={0}'
      sql = sql.format(ctx.message.server.id)
      self.cursor.execute(sql)
      self.connection.commit()
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
      self.cursor.execute(sql)
      mention_results = self.cursor.fetchall()
      update = False
      if mention_results[0]['mentions'] != None:
        update = True
        things = mention_results[0]['mentions'].split()
        for x in things:
          mention_ids.append(x)
      sql = 'UPDATE `verification` SET mentions="{0}" WHERE server={1}'
      sql = sql.format(' '.join(mention_ids), ctx.message.server.id)
      self.cursor.execute(sql)
      self.connection.commit()
      if update:
        await self.bot.say(":white_check_mark: Updated mentions to include `{0}` on user join for approval".format(', '.join(mention_names)))
      else:
        await self.bot.say(":white_check_mark: Set `{0}` to be mentioned on user join for approval".format(', '.join(mention_names)))

  @commands.group(pass_context=True, invoke_without_command=True)
  @checks.mod_or_perm(manage_server=True)
  async def verify(self, ctx, *users:str):
    if ctx.message.server.me.permissions_in(ctx.message.channel).manage_roles == False and ctx.message.server.me.permissions_in(ctx.message.channel).manage_channels == False:
      if ctx.message.server.me.permissions_in(ctx.message.channel).administrator == False:
        await self.bot.say(":warning: `I need Administrator permission to make/add a role to mute on join`")
        return
    if len(users) == 0:
      await self.bot.say("pls input users to verify thx")
      return
    sql = 'SELECT * FROM `verification` WHERE server={0}'
    sql = sql.format(ctx.message.server.id)
    self.cursor.execute(sql)
    result = self.cursor.fetchall()
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
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        if len(result) == 0:
          await self.bot.say(":warning: `{0}` is not in the verification queue.".format(user))
          if len(users) > 1:
            continue
          else:
            return
        sql = 'DELETE FROM `verification_queue` WHERE server={0} AND id={1}'
        sql = sql.format(ctx.message.server.id, user)
        self.cursor.execute(sql)
        self.connection.commit()
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
          self.cursor.execute(sql)
          result = self.cursor.fetchall()
          if len(result) == 0:
            await self.bot.say(":warning: `{0}` is not in the verification queue.".format(user))
            if len(users) > 1:
              continue
            else:
              return
          sql = 'DELETE FROM `verification_queue` WHERE server={0} AND user={1}'
          sql = sql.format(ctx.message.server.id, x.id)
          self.cursor.execute(sql)
          self.connection.commit()
          discord_user = discord.Server.get_member(ctx.message.server, user_id=str(result[count2]['user']))
          count2 += 1
      if discord_user == None:
        continue
      try:
        await self.bot.remove_roles(discord_user, role)
      except Exception as e:
        await self.bot.say(code.format(e))
        await self.bot.say(":warning: {0} was removed from the queue however his role could not be removed because I do not have Administrator permissions.\nPlease remove the role manually and give me **Administrator**.".format(user))
        return
      await self.bot.say(":white_check_mark: Removed `{0}` from queue!".format(user))
      queue_removed_msg = 'You have been approved/verified for `{0}` and can now message!'.format(ctx.message.server.name)
      await self.bot.send_message(user, queue_removed_msg)

  @verify.command(name='list', pass_context=True, invoke_without_command=True)
  async def verify_list(self, ctx):
    if ctx.message.server.me.permissions_in(ctx.message.channel).manage_roles == False and ctx.message.server.me.permissions_in(ctx.message.channel).manage_channels == False:
      if ctx.message.server.me.permissions_in(ctx.message.channel).administrator == False:
        await self.bot.say(":warning: `I need Administrator permission to make/add a role to mute on join`")
        return
    sql = 'SELECT * FROM `verification` WHERE server={0}'
    sql = sql.format(ctx.message.server.id)
    self.cursor.execute(sql)
    result = self.cursor.fetchall()
    if len(result) == 0:
      await self.bot.say(":no_entry: This server does not have approval/verification turned on (`verification <#discord_channel>` to do so)!!!")
      return
    sql = 'SELECT * FROM `verification_queue` WHERE server={0}'
    sql = sql.format(ctx.message.server.id)
    self.cursor.execute(sql)
    result = self.cursor.fetchall()
    if len(result) == 0:
      await self.bot.say(":no_entry: `There are no users in the verification/approval queue`")
      return
    users = []
    for s in result:
      user = discord.Server.get_member(ctx.message.server, user_id=str(s['user']))
      if user == None:
        continue
      users.append('{0}#{1} ({2})'.format(user.name, user.discriminator, str(s['id'])))
    await self.bot.say("**{0} Users in Queue**\n`{1}`".format(len(users), ', '.join(users)))

  async def remove_verification(self, server):
    sql = 'DELETE FROM `verification` WHERE server={0}'
    sql = sql.format(server.id)
    self.cursor.execute(sql)
    self.connection.commit()
    sql = 'DELETE FROM `verification_queue` WHERE server={0}'
    sql = sql.format(server.id)
    self.cursor.execute(sql)
    self.connection.commit()
    try:
      await self.bot.send_message(server.owner, ":warning: One of your server administrators (or you) have enabled approval/verification on user join.\n\nAdministrator permission was taken away from me making the feature unusable, I need Administrator permission to make/add a role to mute on join.\n\n`The system has been automatically disabled, re-enable anytime if you please.`")
    except:
      pass

  async def on_member_join(self, member):
    try:
      if member.bot:
        return
      server = member.server
      sql = 'SELECT * FROM `verification` WHERE server={0}'
      sql = sql.format(server.id)
      self.cursor.execute(sql)
      result = self.cursor.fetchall()
      if len(result) == 0:
        return
      channel = server.get_channel(str(result[0]['channel']))
      if channel == None:
        raise discord.errors.NotFound
      if server.me.permissions_in(channel).manage_roles == False and server.me.permissions_in(channel).manage_channels == False:
        if server.me.permissions_in(channel).administrator == False:
          await self.remove_verification(server)
          return
      sql = "INSERT INTO `verification_queue` (`user`, `server`, `id`) VALUES (%s, %s, %s)"
      rand = random.randint(0, 99999)
      self.cursor.execute(sql, (member.id, server.id, rand))
      self.connection.commit()
      role = discord.utils.get(server.roles, name='Awaiting Approval')
      await self.bot.add_roles(member, role)
      for s in server.channels:
        perms = member.permissions_in(s)
        if perms.read_messages == False:
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
      await self.bot.send_message(channel, msg)
      join_msg = "You've been placed in the approval queue for `{0}`, please be patient and wait until a staff member approves your join!".format(server.name)
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
      self.cursor.execute(sql)
      result = self.cursor.fetchall()
      if len(result) == 0:
        return
      sql = 'SELECT * FROM `verification_queue` WHERE server={0} AND user={1}'
      sql = sql.format(server.id, member.id)
      self.cursor.execute(sql)
      result2 = self.cursor.fetchall()
      if len(result2) == 0:
        return
      sql = 'DELETE FROM `verification_queue` WHERE server={0} AND user={1}'
      sql = sql.format(server.id, member.id)
      self.cursor.execute(sql)
      self.connection.commit()
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
      self.cursor.execute(sql)
      result = self.cursor.fetchall()
      if len(result) == 0:
        return
      sql = 'SELECT * FROM `verification_queue` WHERE server={0} AND user={1}'
      sql = sql.format(server.id, member.id)
      self.cursor.execute(sql)
      result2 = self.cursor.fetchall()
      if len(result2) == 0:
        return
      sql = 'DELETE FROM `verification_queue` WHERE server={0} AND user={1}'
      sql = sql.format(server.id, member.id)
      self.cursor.execute(sql)
      self.connection.commit()
      channel = self.bot.get_channel(id=str(result[0]['channel']))
      await self.bot.send_message(channel, ':exclamation: `{0}` has been removed from the approval/verification queue for being banned from the server.'.format(member))
    except (discord.errors.Forbidden, discord.errors.InvalidArgument, discord.errors.NotFound):
      await self.remove_verification(server)

def setup(bot):
  bot.add_cog(Verification(bot))
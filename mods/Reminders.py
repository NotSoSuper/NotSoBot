import discord
import asyncio
import re
import timestring
from datetime import datetime
from discord.ext import commands

code = "```py\n{0}\n```"

class Reminders():
  def __init__(self, bot):
    self.bot = bot
    self.connection = bot.mysql.reminder_connection
    self.cursor = bot.mysql.reminder_cursor
    self.bot.loop.create_task(self.remind_task())

  async def get_reminders(self):
    sql = 'SELECT * FROM `reminders`'
    self.cursor.execute(sql)
    result = self.cursor.fetchall()
    if len(result) == 0:
      return False
    reminds = {}
    for s in result:
      s['user'] = str(s['user'])
      if s['user'] in reminds:
        if s['time'] in reminds[s['user']]:
          continue
        reminds[s['user']][0].append(s['time'])
        reminds[s['user']][1].append(s['message'])
      else:
        reminds[s['user']] = [[s['time']], [s['message']]]
    return reminds

  async def remind_due(self, when:int):
    utc = datetime.utcnow()
    utc_ = int(utc.strftime("%s"))
    return utc_ >= when

  async def remove_reminder(self, user:int, time:int):
    sql = 'DELETE FROM `reminders` WHERE user={0} AND time={1}'
    sql = sql.format(user, time)
    self.cursor.execute(sql)
    self.connection.commit()

  async def remind_task(self):
    await self.bot.wait_until_ready()
    while self.bot.is_closed == False:
      reminders = await self.get_reminders()
      if reminders == False:
        await asyncio.sleep(5)
        continue
      for user in reminders:
        count = 0
        for t in reminders[user][0]:
          is_due = await self.remind_due(int(t))
          if is_due:
            message = reminders[user][1][count]
            discord_user = None
            for server in self.bot.servers:
              if discord_user == None:
                discord_user = discord.Server.get_member(server, user_id=user)
              else:
                break
            if discord_user != None:
              if message == None:
                await self.bot.send_message(discord_user, ":alarm_clock: Reminder: `time is up!`")
              else:
                await self.bot.send_message(discord_user, ":alarm_clock: Reminder: `{0}`.".format(message))
            count += 1
            await self.remove_reminder(user, t)
      await asyncio.sleep(2)

  TimeUnits = {
    's'  : 1,
    'm'  : 60,
    'mi' : 60,
    'h'  : 3600,
    'd'  : 86400, 
    'w'  : 604800,
    'mo' : 2592000,
    'y'  : 31536000
  }
  remind_regex = re.compile(r"(\d*)([a-z])", re.IGNORECASE)
  @commands.group(pass_context=True, aliases=['reminder'], invoke_without_command=True)
  async def remind(self, ctx, when:str, *, text:str=None):
    match = self.remind_regex.findall(when)
    if len(match) == 0:
      await self.bot.say(':warning: `Invalid Time Format`\n**Example:** `1d2h (1 day, 2 hours)`')
      return
    utc = datetime.utcnow()
    utc_ = int(utc.strftime("%s"))
    idk = True
    try:
      for x in match:
        for s in x:
          if idk:
            succ = s
            idk = False
          else:
            hah = int(succ)*self.TimeUnits[s]
            time = int(hah)+int(utc_)
            idk = True
    except Exception as e:
      try:
        time = int(timestring.Date(when).to_unixtime())
        if utc_ >= time:
          await self.bot.say(':warning: `Invalid Time Format`\n**Example:** `1d2h (1 day, 2 hours)`')
          return
      except:
        await self.bot.say(':warning: `Invalid Time Format`\n**Example:** `1d2h (1 day, 2 hours)`')
        return
    sql = 'INSERT INTO `reminders` (`user`, `time`, `message`) VALUES (%s, %s, %s)'
    self.cursor.execute(sql, (ctx.message.author.id, time, text))
    self.connection.commit()
    await self.bot.say(':white_check_mark: Reminder set.')

  @remind.command(name='list', pass_context=True, invoke_without_command=True)
  async def remind_list(self, ctx):
    sql = 'SELECT * FROM `reminders` WHERE user={0}'
    sql = sql.format(ctx.message.author.id)
    self.cursor.execute(sql)
    result = self.cursor.fetchall()
    if len(result) == 0:
      await self.bot.say(":no_entry: You don't have any reminders set!")
      return
    reminders = []
    count = 0
    for reminder in result:
      count += 1
      timestamp = str(datetime.fromtimestamp(reminder['time']).strftime('%m-%d-%Y %H:%M:%S'))
      if reminder['message'] != None:
        reminders.append('`{0} #{1} ({2})`'.format(reminder['message'], count, timestamp))
      else:
        reminders.append('`{0} #{1}`'.format(timestamp, count))
    await self.bot.say('You have **{0}** reminders: {1}'.format(len(reminders), ', '.join(reminders)))

  @remind.group(name='remove', pass_context=True, invoke_without_command=True, aliases=['delete'])
  async def remind_remove(self, ctx, id:int):
    sql = 'SELECT * FROM `reminders` WHERE user={0}'
    sql = sql.format(ctx.message.author.id)
    self.cursor.execute(sql)
    result = self.cursor.fetchall()
    if len(result) == 0:
      await self.bot.say(":no_entry: You don't have any reminders set!")
      return
    reminders = {}
    count = 0
    for reminder in result:
      count += 1
      reminders[count] = reminder['time']
    sql = 'DELETE FROM `reminders` WHERE user={0} AND time={1}'
    try:
      sql = sql.format(ctx.message.author.id, reminders[id])
    except:
      await self.bot.say(':warning: `Invalid reminder id!`')
      return
    self.cursor.execute(sql)
    self.connection.commit()
    await self.bot.say(':x: Removed reminder **#{0}**'.format(id))

  @remind_remove.command(name='all', pass_context=True, invoke_without_command=True)
  async def remind_remove_all(self, ctx):
    sql = 'SELECT * FROM `reminders` WHERE user={0}'
    sql = sql.format(ctx.message.author.id)
    self.cursor.execute(sql)
    result = self.cursor.fetchall()
    if len(result) == 0:
      await self.bot.say(":no_entry: You don't have any reminders set!")
      return
    sql = 'DELETE FROM `reminders` WHERE user={0}'
    sql = sql.format(ctx.message.author.id)
    self.cursor.execute(sql)
    self.connection.commit()
    await self.bot.say(':x: `Removed all reminders.`'.format(id))

def setup(bot):
  bot.add_cog(Reminders(bot))

import discord
import asyncio
import re
import timestring
import time as ti
from timestring.timestring_re import TIMESTRING_RE
from datetime import datetime
from discord.ext import commands
from mods.cog import Cog

code = "```py\n{0}\n```"

class Reminders(Cog):
  def __init__(self, bot):
    super().__init__(bot)
    self.cursor = bot.mysql.cursor
    self.truncate = bot.truncate
    #https://github.com/Rapptz/RoboDanny/tree/master/cogs/meta.py#L13
    self.time_regex = re.compile(r"(?:(?P<months>\d+)mo)?(?:(?P<weeks>\d+)w)?(?:(?P<days>\d+)d)?(?:(?P<hours>\d+)h)?(?:(?P<minutes>\d+)m)?(?:(?P<seconds>\d+)s)?")
    bot.loop.create_task(self.remind_task())

  async def get_reminders(self):
    sql = 'SELECT * FROM `reminders`'
    result = self.cursor.execute(sql).fetchall()
    result = [dict(s.items()) for s in result]
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

  def remind_due(self, when):
    return int(ti.time()) >= when

  async def remove_reminder(self, user:int, time:int):
    sql = 'DELETE FROM `reminders` WHERE user={0} AND time={1}'
    sql = sql.format(user, time)
    self.cursor.execute(sql)
    self.cursor.commit()

  async def remind_task(self):
    try:
      if self.bot.shard_id != 0:
        return
      await self.bot.wait_until_ready()
      while self.bot.is_closed == False:
        reminders = await self.get_reminders()
        if reminders is False:
          await asyncio.sleep(10)
          continue
        for user in reminders:
          for t in reminders[user][0]:
            is_due = self.remind_due(int(t))
            if is_due is False:
              continue
            index = reminders[user][0].index(t)
            message = reminders[user][1][index]
            discord_user = await self.bot.get_user_info(str(user))
            try:
              if message is None:
                await self.truncate(discord_user, ":alarm_clock: Reminder: `time is up!`")
              else:
                await self.truncate(discord_user, ":alarm_clock: Reminder: `{0}`.".format(message))
            except:
              pass
            await self.remove_reminder(user, t)
        await asyncio.sleep(5)
    except Exception as e:
      print(e)

  async def get_time(self, txt):
    time = 0
    if txt.isdigit():
      time += int(txt)
    elif txt.split()[0].isdigit():
      s = txt.split()[0]
      time += int(s)
      txt = txt[len(s):]
    else:
      match = self.time_regex.match(txt)
      if match is None or not match.group(0):
        return False
      months = match.group('months')
      weeks = match.group('weeks')
      days = match.group('days')
      hours = match.group('hours')
      minutes = match.group('minutes')
      seconds = match.group('seconds')
      if months:
        time += int(months) * 2592000
      if weeks:
        time += int(weeks) * 604800
      if days:
        time += int(days) * 86400
      if hours:
        time += int(hours) * 3600
      if minutes:
        time += int(minutes) * 60
      if seconds:
        time += int(seconds)
    text = re.sub(self.time_regex, '', txt)
    if text and text[0] == ' ':
      text = text[1:]
    return time, text

  @commands.group(pass_context=True, aliases=['reminder'], invoke_without_command=True)
  async def remind(self, ctx, *, text:str=None):
    if text is None:
      await self.bot.say(':warning: `Invalid Time Format`\n**Example:** `1h2m` (1 hour, 2 minutes)')
      return
    curr = ti.time()
    time_result = await self.get_time(text)
    if time_result:
      time = time_result[0]
      text = time_result[1]
    if time_result is False:
      time = 1
      try:
        epoch = int(timestring.Date(text).to_unixtime())
        assert curr >= epoch
        text = re.sub(TIMESTRING_RE, '', text)
      except:
        await self.bot.say(':warning: `Invalid Time Format`\n**Example:** `1h2m` (1 hour, 2 minutes)')
        return
    elif time <= 0:
      await self.bot.say(':warning: AFAIK, time can\'t be negative.')
      return
    else:
      epoch = int(curr) + time
    text = text if text != '' else None
    sql = 'INSERT INTO `reminders` (`user`, `time`, `message`) VALUES (%s, %s, %s)'
    self.cursor.execute(sql, (ctx.message.author.id, epoch, text))
    self.cursor.commit()
    await self.bot.say(':white_check_mark: Reminder set for `{0}` seconds.'.format(time))

  @remind.command(name='list', pass_context=True, invoke_without_command=True)
  async def remind_list(self, ctx):
    sql = 'SELECT * FROM `reminders` WHERE user={0}'
    sql = sql.format(ctx.message.author.id)
    result = self.cursor.execute(sql).fetchall()
    if len(result) == 0:
      await self.bot.say(":no_entry: You don't have any reminders set!")
      return
    reminders = []
    count = 0
    for reminder in result:
      count += 1
      timestamp = str(datetime.fromtimestamp(reminder['time']).strftime('%m-%d-%Y %H:%M:%S'))
      if reminder['message'] != None:
        reminders.append('**{0}.** `{1}` __{2}__'.format(count, reminder['message'], timestamp))
      else:
        reminders.append('**{0}.** __{1}__'.format(count, timestamp))
    await self.truncate(ctx.message.channel, '**Reminders:**\n{0}'.format('\n'.join(reminders)))

  @remind.group(name='remove', pass_context=True, invoke_without_command=True, aliases=['delete'])
  async def remind_remove(self, ctx, id:int):
    sql = 'SELECT * FROM `reminders` WHERE user={0}'
    sql = sql.format(ctx.message.author.id)
    result = self.cursor.execute(sql).fetchall()
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
    self.cursor.commit()
    await self.bot.say(':x: Removed reminder **#{0}**'.format(id))

  @remind_remove.command(name='all', pass_context=True, invoke_without_command=True)
  async def remind_remove_all(self, ctx):
    sql = 'SELECT * FROM `reminders` WHERE user={0}'
    sql = sql.format(ctx.message.author.id)
    result = self.cursor.execute(sql).fetchall()
    if len(result) == 0:
      await self.bot.say(":no_entry: You don't have any reminders set!")
      return
    sql = 'DELETE FROM `reminders` WHERE user={0}'
    sql = sql.format(ctx.message.author.id)
    self.cursor.execute(sql)
    self.cursor.commit()
    await self.bot.say(':x: `Removed all reminders.`'.format(id))

def setup(bot):
  bot.add_cog(Reminders(bot))
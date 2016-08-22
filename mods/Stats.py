import discord
import time
import requests
import io

cool = "```xl\n{0}\n```"
class Stats:
  """carbonitex.net and bots.discord.pw"""
  def __init__(self, bot):
    self.bot = bot
    self.discord_path = bot.path.discord
    self.files_path = bot.path.files

  async def server_count(self, idk=None):
    if idk == None:
      path = self.files_path('server_count/{0}.txt'.format(self.bot.shard_id))
      with io.open(path, 'w', encoding='utf8') as f:
        f.write(str(len(self.bot.servers)))
        f.close()
      path = self.files_path('server_count/{0}_largest_member_server.txt'.format(self.bot.shard_id))
      with io.open(path, 'w', encoding='utf8') as f:
        server_count = [len(i.members) for i in self.bot.servers]
        max_ = max(server_count)
        max_index = server_count.index(max_)
        servers = [i for i in self.bot.servers]
        max_server = servers[max_index]
        thing = '{0}\n{1}'.format(max_server.name, max_)
        f.write(str(thing))
        f.close()
      path = self.files_path('server_count/{0}_users.txt'.format(self.bot.shard_id))
      count = 0
      with io.open(path, 'w', encoding='utf8') as f:
        count = len([x for x in self.bot.get_all_members()])
        f.write(str(count))
        f.close()
      path = self.files_path('server_count/{0}_unique_users.txt'.format(self.bot.shard_id))
      count = 0
      with io.open(path, 'w', encoding='utf8') as f:
        count = len(set([x for x in self.bot.get_all_members()]))
        f.write(str(count))
        f.close()
      path = self.files_path('server_count/{0}_channels.txt'.format(self.bot.shard_id))
      text_channels = 0
      voice_channels = 0
      for server in self.bot.servers:
        for channel in server.channels:
          if channel.type == discord.ChannelType.text:
            text_channels += 1
          if channel.type == discord.ChannelType.voice:
            voice_channels += 1
      with io.open(path, 'w', encoding='utf8') as f:
        f.write('{0}\n{1}'.format(text_channels, voice_channels))
        f.close()
    elif idk == True:
      shards = [0, 1, 2, 3]
      count = 0
      for x in shards:
        path = self.files_path('server_count/{0}.txt'.format(x))
        with io.open(path, 'r') as f:
          try:
            count += int(f.read())
          except:
            pass
          f.close()
      return count

  sent = 0
  key = ''
  API = 'https://www.carbonitex.net/discord/data/botdata.php'
  async def carbon(self):
    server_count = await self.server_count(True)
    data = {
      'key': self.key,
      'servercount': server_count,
      "botname": self.bot.user.name,
      "botid": self.bot.user.id,
      "logoid": self.bot.user.avatar_url[60:].replace(".jpg",""),
      "ownerid": '130070621034905600',
      "ownername": 'NotSoSuper'
    }
    timestamp = time.strftime('%H:%M:%S')
    r = requests.post(self.API, json=data)

  pw_key = ''
  async def discord_pw(self):
    API = 'https://bots.discord.pw/api/bots/{0}/stats'.format(self.bot.user.id)
    data = {
      "shard_id": self.bot.shard_id,
      "shard_count": self.bot.shard_count,
      "server_count": len(self.bot.servers)
    }
    headers = {'Authorization': self.pw_key}
    timestamp = time.strftime('%H:%M:%S')
    r = requests.post(API, json=data, headers=headers)

  async def on_server_join(self, server):
    await self.server_count()
    await self.carbon()
    await self.discord_pw()

  async def on_server_leave(self, server):
    await self.server_count()
    await self.carbon()
    await self.discord_pw()

  async def on_ready(self):
    await self.server_count()
    await self.carbon()
    await self.discord_pw()

def setup(bot):
  bot.add_cog(Stats(bot))
def setup(bot):
  bot.add_cog(Stats(bot))

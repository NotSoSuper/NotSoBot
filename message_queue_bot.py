import discord
import asyncio
import aiohttp
import jsonpickle

async def truncate(channel, msg):
	if len(msg) == 0:
		return
	split = [msg[i:i + 1999] for i in range(0, len(msg), 1999)]
	try:
		for s in split:
			if len(split) > 1:
				if s.startswith('```'):
					s = s[:1995]+'\n```'
			await bot.send_message(channel, s)
	except Exception as e:
		await bot.send_message(channel, e)

async def get_queue():
	payload = {'key': ''}
	try:
		with aiohttp.ClientSession() as session:
			with aiohttp.Timeout(15):
				async with session.post('http://ip:port/queued', data=payload) as resp:
					load = await resp.json()
		queue = {}
		for s in load:
			queue[s] = int(load[s][2])
		q = {}
		for key in sorted(queue, key=lambda k: queue[k], reverse=False):
			q[key] = load[key]
		return q
	except Exception as e:
		print(e)
		return {}

async def delete_queue(id):
	payload = {'key':'', 'id':str(id)}
	try:
		with aiohttp.ClientSession() as session:
			with aiohttp.Timeout(15):
				async with session.post('http://ip:port/queue_delete', data=payload) as resp:
					text = await resp.text()
		return text
	except:
		return []

bot = discord.Client()

async def check_queue():
	await bot.wait_until_ready()
	while not bot.is_closed:
		queue = await get_queue()
		if len(queue) == 0:
			await asyncio.sleep(1)
		else:
			for s in queue:
				message_id = int(s)
				channel_id = str(queue[s][0])
				message = str(queue[s][1])
				embed = True if int(queue[s][3]) else False
				try:
					target = bot.get_channel(channel_id)
					if embed:
						await bot.send_message(target, embed=jsonpickle.decode(message))
					else:
						await truncate(target, message)
				except Exception as e:
					print(e)
					pass
				delete_request = await delete_queue(message_id)
				await asyncio.sleep(0.21)

@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.name + "#" + bot.user.discriminator)
	print(bot.user.id)
	print('------')
	await bot.change_presence(game=discord.Game(name="go away"))

bot.loop.create_task(check_queue())
bot.run('')
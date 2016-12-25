import asyncio
import datetime
import os, sys
from bot import NotSoBot

loop = asyncio.get_event_loop()

dev_mode = str(os.getenv('dev_mode', False))
if dev_mode == '1' or dev_mode.lower() == 'true':
	dev_mode = True
else:
	dev_mode = False

shard_id = [int(s) for s in os.path.realpath(__file__) if s.isdigit()][0]
shard_count = len([s for s in os.listdir() if s.startswith('bot') and s[3].isdigit()])
if dev_mode:
	if len(sys.argv) > 2:
		shard_id = int(sys.argv[1])
	if len(sys.argv) > 1:
		shard_count = int(sys.argv[2])

async def watcher():
	await asyncio.sleep(30)
	while True:
		print('Checking NotSoBot #{0}'.format(bot.shard_id))
		now = datetime.datetime.utcnow()
		ahead = bot.last_message + datetime.timedelta(minutes=1)
		if now > ahead:
			bot.die()
			await asyncio.sleep(120)
		else:
			await asyncio.sleep(5)


bot = NotSoBot(loop=loop, shard_id=shard_id, shard_count=shard_count, dev_mode=dev_mode, max_messages=10000)

if __name__ == "__main__":
	try:
		task = loop.create_task(bot.run())
		task.add_done_callback(functools.partial(main, loop))
		bot.own_task = task
		loop.create_task(watcher())
		loop.run_until_complete(task)
		loop.run_forever()
	except (KeyboardInterrupt, RuntimeError):
		print('\nKeyboardInterrupt - Shutting down...')
		bot.die()
	finally:
		print('--Closing Loop--')
		loop.close()
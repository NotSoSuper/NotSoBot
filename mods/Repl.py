from discord.ext import commands
from utils import checks
import asyncio
import traceback
import discord
import inspect
import aiohttp
from contextlib import redirect_stdout
import io
from mods.cog import Cog

#mainly from https://github.com/Rapptz/RoboDanny/blob/master/cogs/repl.py

class Repl(Cog):
	def __init__(self, bot):
		super().__init__(bot)
		self.sessions = set()
		self.cursor = bot.mysql.cursor
 
	async def cleanup_code(self, content):
		"""Automatically removes code blocks from the code."""
		if content.startswith('```') and content.endswith('```'):
			clean = '\n'.join(content.split('\n')[1:-1])
		else:
			clean = content.strip('` \n')
		if clean.startswith('http'):
			with aiohttp.ClientSession() as session:
				async with session.get(clean) as r:
					code = await r.text()
			clean = code
		return clean

	def get_syntax_error(self, e):
		return '```py\n{0.text}{1:>{0.offset}}\n{2}: {0}```'.format(e, '^', type(e).__name__)

	@commands.command(pass_context=True, hidden=True)
	@checks.is_owner()
	async def repl(self, ctx):
		try:
			msg = ctx.message
			variables = {
				'self': self,
				'ctx': ctx,
				'bot': self.bot,
				'message': msg,
				'server': msg.server,
				'channel': msg.channel,
				'author': msg.author,
				'last': None,
				'commands': commands,
				'discord': discord,
				'asyncio': asyncio,
				'cursor': self.cursor
			}
			if msg.channel.id in self.sessions:
				await ctx.bot.say('Already running a REPL session in this channel. Exit it with `quit`.')
				return
			self.sessions.add(msg.channel.id)
			await ctx.bot.say('Enter code to execute or evaluate. `exit()` or `quit` to exit.')
			while True:
				response = await ctx.bot.wait_for_message(author=msg.author, channel=msg.channel,
																									 check=lambda m: m.content.startswith('`'))
				cleaned = await self.cleanup_code(response.content)
				if cleaned in ('quit', 'exit', 'exit()', 'brexit'):
					await ctx.bot.say('Exiting.')
					self.sessions.remove(msg.channel.id)
					return
				executor = exec
				if cleaned.count('\n') == 0:
					try:
						code = compile(cleaned, '<repl session>', 'eval')
					except SyntaxError:
						pass
					else:
						executor = eval
				if executor is exec:
					try:
						code = compile(cleaned, '<repl session>', 'exec')
					except SyntaxError as e:
						await ctx.bot.say(self.get_syntax_error(e))
						continue
				variables['message'] = response
				fmt = None
				stdout = io.StringIO()
				try:
					with redirect_stdout(stdout):
						result = executor(code, variables)
						if inspect.isawaitable(result):
							result = await result
				except Exception as e:
					value = stdout.getvalue()
					fmt = '```py\n{}{}\n```'.format(value, traceback.format_exc())
				else:
					value = stdout.getvalue()
					if result is not None:
						fmt = '```py\n{}{}\n```'.format(value, result)
						variables['last'] = result
					elif value:
						fmt = '```py\n{}\n```'.format(value)
				try:
					if fmt is not None:
						if len(fmt) >= 1999:
							fmt = fmt[:1976]
							fmt += "```\n:warning: Truncated"
						await self.bot.say(fmt)
				except discord.Forbidden:
					pass
				except discord.HTTPException as e:
					await ctx.bot.say(':warning: Unexpected error: `{0}`'.format(e))
		except Exception as e:
			await ctx.bot.say(e)

def setup(bot):
	bot.add_cog(Repl(bot))
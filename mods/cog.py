#attempt to try https://github.com/SunDwarf's bot threading manager with multiprocessing, failed and too lazy to remove
from collections import OrderedDict
from bot import NotSoBot

class CogMeta(type):
	def __prepare__(*args, **kwargs):
		return OrderedDict()

class Cog(metaclass=CogMeta):
	def __init__(self, bot:NotSoBot):
		self._bot = bot

	@property
	def bot(self):
		return self._bot

	@classmethod
	def setup(cls, bot:NotSoBot):
		bot.add_cog(cls(bot))
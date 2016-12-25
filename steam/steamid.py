import re

from .steamaccountuniverse import SteamAccountUniverse
from .steamaccounttype     import SteamAccountType

class SteamId(object):
	def __init__(self):
		super(SteamId, self).__init__()
		
		self._universe    = None
		self._accountType = None
		self._instance    = None
		self._accountId   = None
	
	@property
	def universe(self):
		return self._universe
	
	@property
	def accountType(self):
		return self._accountType
	
	@property
	def instance(self):
		return self._instance
	
	@property
	def accountId(self):
		return self._accountId
	
	@property
	def steamId(self):
		x = "0"
		if self.universe != SteamAccountUniverse.Public: x = "?"
		y = self.accountId & 1
		z = self.accountId >> 1
		
		return "STEAM_%s:%d:%d" % (x, y, z)
	
	@property
	def steamId3(self):
		character = SteamAccountType.toCharacter(self.accountType)
		if self.accountType == SteamAccountType.Chat:
			if self.instance == SteamAccountType.defaultInstanceId("T"): character = "T"
			elif self.instance == SteamAccountType.defaultInstanceId("c"): character = "c"
			elif self.instance == SteamAccountType.defaultInstanceId("L"): character = "L"
			else: character = "T"
		
		steamId3 = "[" + character + ":" + str(self.universe) + ":" + str(self.accountId)
		
		if self.instance != SteamAccountType.defaultInstanceId(character):
			steamId3 += ":" + str(self.instance)
		
		steamId3 += "]"
		
		return steamId3
	
	@property
	def steamId64(self):
		return (self.universe << 56) + (self.accountType << 52) + (self.instance << 32) + self.accountId
	
	@property
	def profileUrl(self):
		return "http://steamcommunity.com/profiles/" + str(self.steamId64)
	
	@classmethod
	def fromSteamId(cls, steamId):
		match = re.match("STEAM_([0-9]+):([0-9]+):([0-9]+)", steamId.upper())
		if match is None: return None
		
		steamId = cls()
		steamId._accountId   = (int(match.group(3)) << 1) + int(match.group(2))
		steamId._instance    = 1
		steamId._accountType = SteamAccountType.Individual
		steamId._universe    = SteamAccountUniverse.Public
		
		if int(match.group(1)) != 0: steamId.universe = SteamAccountUniverse.Invalid
		
		return steamId
	
	@classmethod
	def fromSteamId3(cls, steamId3):
		match = re.match(r"\[(.):([0-9]+):([0-9]+)\]", steamId3)
		if match is not None:
			steamId = cls()
			steamId._accountId   = int(match.group(3))
			steamId._instance    = SteamAccountType.defaultInstanceId(match.group(1))
			steamId._accountType = SteamAccountType.fromCharacter(match.group(1))
			steamId._universe    = int(match.group(2))
			
			if steamId.instance    is None: steamId._instance    = 1
			if steamId.accountType is None: steamId._accountType = SteamAccountType.Invalid
			
			return steamId
		
		match = re.match(r"\[(.):([0-9]+):([0-9]+):([0-9]+)\]", steamId3)
		if match is not None:
			steamId = cls()
			steamId._accountId   = int(match.group(3))
			steamId._instance    = int(match.group(4))
			steamId._accountType = SteamAccountType.fromCharacter(match.group(1))
			steamId._universe    = int(match.group(2))
			
			if steamId.accountType is None: steamId._accountType = SteamAccountType.Invalid
			
			return steamId
		
		return None
	
	@classmethod
	def fromSteamId64(cls, steamId64):
		try: steamId64 = int(steamId64)
		except: return None
		
		steamId = cls()
		steamId._accountId   = steamId64 & ((1 << 32) - 1)
		steamId64 >>= 32
		steamId._instance    = steamId64 & ((1 << 20) - 1)
		steamId64 >>= 20
		steamId._accountType = steamId64 & ((1 <<  4) - 1)
		steamId64 >>=  4
		steamId._universe    = steamId64 & ((1 <<  8) - 1)
		
		return steamId
	
	@classmethod
	def fromProfileUrl(cls, profileUrl):
		match = re.compile(r"(https?://)?steamcommunity.com/profiles/([0-9]+)", re.IGNORECASE).match(profileUrl)
		if match is None: return None
		
		return cls.fromSteamId64(match.group(2))

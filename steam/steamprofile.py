import html
import re
import urllib.request

from .steamid import SteamId

class SteamProfile(object):
	def __init__(self):
		self._steamId     = None
		
		self._displayName = None
		self._profileId   = None
	
	@property
	def steamId(self):
		return self._steamId
	
	@property
	def displayName(self):
		return self._displayName
	
	@property
	def profileId(self):
		return self._profileId
	
	@property
	def customProfileUrl(self):
		if self.profileId is None: return None
		return "http://steamcommunity.com/id/" + self.profileId
	
	@property
	def profileUrl(self):
		return self.steamId.profileUrl
	
	@classmethod
	def fromSteamId(cls, steamId):
		if steamId is None: return None
		
		steamProfile = cls.fromProfileUrl(steamId.profileUrl)
		if steamProfile is None: return None
		
		steamProfile._steamId = steamId
		
		return steamProfile
	
	@classmethod
	def fromProfileId(cls, profileId):
		if profileId is None: return None
		
		return cls.fromProfileUrl("http://steamcommunity.com/id/" + profileId)
	
	@classmethod
	def fromCustomProfileUrl(cls, customProfileUrl):
		if customProfileUrl is None: return None
		
		profileId = customProfileUrl
		
		match = re.compile(r"(https?://)?steamcommunity.com/id/(.*)", re.IGNORECASE).match(customProfileUrl)
		if match is not None: profileId = match.group(2)
		
		return cls.fromProfileUrl("http://steamcommunity.com/id/" + profileId)
	
	@classmethod
	def fromProfileUrl(cls, profileUrl):
		if profileUrl is None: return None
		
		profileUrl += "?xml=1"
		
		data = urllib.request.urlopen(profileUrl).read()
		data = data.decode("utf-8")
		
		if "<response><error>" in data: return None
		
		steamProfile = cls()
		
		match = re.compile(r".*?<steamID64>([0-9]+)</steamID64>", re.DOTALL).match(data)
		if match is not None: steamProfile._steamId = SteamId.fromSteamId64(match.group(1))
		match = re.compile(r".*?<steamID><!\[CDATA\[(.*?)\]\]></steamID>", re.DOTALL).match(data)
		if match is not None: steamProfile._displayName = html.unescape(match.group(1))
		match = re.compile(r".*?<customURL><!\[CDATA\[(.*?)\]\]></customURL>", re.DOTALL).match(data)
		if match is not None: steamProfile._profileId = html.unescape(match.group(1))
		
		return steamProfile

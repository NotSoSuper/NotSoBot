class SteamAccountType(object):
	Invalid             =  0
	Individual          =  1
	Multiseat           =  2
	GameServer          =  3
	AnonymousGameServer =  4
	Pending             =  5
	ContentServer       =  6
	Clan                =  7
	Chat                =  8
	ClanChat            =  8
	LobbyChat           =  8
	P2PSuperSeeder      =  9
	AnonymousUser       = 10
	
	DefaultInstanceIds  = {}
	DefaultInstanceIds[Invalid]             = 0
	DefaultInstanceIds[Individual]          = 1
	DefaultInstanceIds[Multiseat]           = 0
	DefaultInstanceIds[GameServer]          = 1
	DefaultInstanceIds[AnonymousGameServer] = 0
	DefaultInstanceIds[Pending]             = 0
	DefaultInstanceIds[ContentServer]       = 0
	DefaultInstanceIds[Clan]                = 0
	DefaultInstanceIds[Chat]                = 0
	DefaultInstanceIds[ClanChat]            = 0x00080000
	DefaultInstanceIds[LobbyChat]           = 0x00040000
	DefaultInstanceIds[P2PSuperSeeder]      = 0
	DefaultInstanceIds[AnonymousUser]       = 0
	DefaultInstanceIds["c"]                 = 0x00080000
	DefaultInstanceIds["L"]                 = 0x00040000
	
	Characters  = {}
	Characters[Invalid]             = "I"
	Characters[Individual]          = "U"
	Characters[Multiseat]           = "M"
	Characters[GameServer]          = "G"
	Characters[AnonymousGameServer] = "A"
	Characters[Pending]             = "P"
	Characters[ContentServer]       = "C"
	Characters[Clan]                = "g"
	Characters[Chat]                = "T"
	Characters[ClanChat]            = "c"
	Characters[LobbyChat]           = "L"
	Characters[AnonymousUser]       = "a"
	
	CharacterAccountTypes = {}
	CharacterAccountTypes["I"] = Invalid
	CharacterAccountTypes["U"] = Individual
	CharacterAccountTypes["M"] = Multiseat
	CharacterAccountTypes["G"] = GameServer
	CharacterAccountTypes["A"] = AnonymousGameServer
	CharacterAccountTypes["P"] = Pending
	CharacterAccountTypes["C"] = ContentServer
	CharacterAccountTypes["g"] = Clan
	CharacterAccountTypes["T"] = Chat
	CharacterAccountTypes["c"] = ClanChat
	CharacterAccountTypes["L"] = LobbyChat
	CharacterAccountTypes["a"] = AnonymousUser
	
	@classmethod
	def defaultInstanceId(cls, x):
		if x in cls.DefaultInstanceIds: return cls.DefaultInstanceIds[x]
		return cls.DefaultInstanceIds.get(cls.CharacterAccountTypes.get(x))
	
	@classmethod
	def fromCharacter(cls, c):
		return cls.CharacterAccountTypes.get(c)
	
	@classmethod
	def toCharacter(cls, accountType):
		return cls.Characters.get(accountType)

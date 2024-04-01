
from django.conf import settings

import uuid

#
# CLASS PLAYER
#

class Player:
	name:				str
	uuid:				uuid.UUID
	connected_channel:	str

	def __init__(self, name: str, connected_channel: str) -> None:
		self.name = name
		self.uuid = uuid.uuid4()
		self.connected_channel = connected_channel
	
	def __str__(self) -> str:
		return "name: " + self.name + ", id: " + str(self.uuid) + "\n"
		

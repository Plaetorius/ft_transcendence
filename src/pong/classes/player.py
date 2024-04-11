
#
# CLASS PLAYER
#

class Player:
	def __init__(self, name: str, id: int) -> None:
		self.name = name
		self.id = id
	
	def __repr__(self) -> str:
		return "name: " + self.name + ", id: " + self.id
	
	def to_dict(self):
		return {
			"name": self.name,
			"id": self.id
		}
		

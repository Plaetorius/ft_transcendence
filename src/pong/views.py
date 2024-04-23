
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


from .classes.player import Player
from .consumers import Party

from users.views import CookieJWTAuthentication

from .consumers import g_party_manager

from .game_classes.pong_game import PongParty
from .game_classes.pong_tournament import pongTournament


class CreatePartyAPIView(APIView):
	authentication_classes = [CookieJWTAuthentication]
	permission_classes = [IsAuthenticated]

	def get(self, request, *args, **kwargs):

		# Create a new party
		if ('gamemode' not in kwargs):
			gamemode = 'versus'
		else:
			gamemode = kwargs['gamemode']



		if (gamemode == 'maze'):
			party_mode = PongParty()		# TODO TODO TODO TODO TODO TODO
		elif (gamemode == 'tournament'):
			party_mode = pongTournament()
		elif (gamemode == 'local_1v1'):		# TODO TODO TODO TODO TODO TODO
			party_mode = pongTournament()
		elif (gamemode == 'local_2v2'):
			party_mode = pongTournament()
		else:
			gamemode = 'versus'
			party_mode = PongParty()

		print(f"#################################   INFO: User {request.user.username} is trying to create a party with gamemode {gamemode}")

		party = g_party_manager.create_party(f"{gamemode} {request.user.username}", party_mode)
		# Return the UUID of the created party
		return Response({'party_uuid': party.uuid}, status=status.HTTP_201_CREATED)

class GatherPartyAPIView(APIView):
	authentication_classes = [CookieJWTAuthentication]
	permission_classes = [IsAuthenticated]

	def get(self, request, *args, **kwargs):
		# Get the list of parties
		my_list = g_party_manager.to_dict()['parties']

		# Return the UUID of the created party
		return Response({'parties': my_list}, status=status.HTTP_201_CREATED)
	
class GatherPartyByIdAPIView(APIView):
	authentication_classes = [CookieJWTAuthentication]
	permission_classes = [IsAuthenticated]

	def get(self, request, *args, **kwargs):
		# Get the list of parties
		party_uuid = kwargs['party_uuid']
		my_party = g_party_manager.parties.get(party_uuid, None)

		if (my_party is None):
			return Response({'detail': 'Party not found'}, status=status.HTTP_404_NOT_FOUND)

		return Response({'party': my_party.to_dict()}, status=status.HTTP_201_CREATED)

# class JoinPartyAPIView(LoginRequiredMixin, APIView):
# 	def post(self, request, party_uuid, *args, **kwargs):
# 		# Get the current user
# 		user = request.user
		
# 		print(f"#################################   INFO: User {user.username} is trying to join party {party_uuid}")
		
# 		# Create a player object for the user
# 		player = Player(user.username, user.id)
# 		# Attempt to join the party
# 		success = g_party_manager.join_party(party_uuid, player)
# 		if success:
# 			return Response({'detail': 'Successfully joined the party.'}, status=status.HTTP_200_OK)
# 		else:
# 			return Response({'detail': 'Failed to join the party.'}, status=status.HTTP_400_BAD_REQUEST)

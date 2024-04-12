from django.urls import path
from . import views

urlpatterns = [
	path('create_party/', views.CreatePartyAPIView.as_view(), name='create_party'),
	path('get_parties/', views.GatherPartyAPIView.as_view(), name='get_parties'),
	path('get_party_by_id/<str:party_uuid>/', views.GatherPartyByIdAPIView.as_view(), name='get_party_by_id'),
	# path('join_party/<str:party_uuid>/', views.JoinPartyAPIView.as_view(), name='join_party'),
]

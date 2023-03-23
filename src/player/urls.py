from django.urls import path
from .views import player_details

urlpatterns = [
    path('player_details/<str:player_name>/', player_details, name='player_details'),
]
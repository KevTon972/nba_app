from django.urls import path
from .views import teams_list, team_details

urlpatterns = [
    path('', teams_list, name='teams_list'),
    path('team_details/<str:team_name>/', team_details, name='team_details')
]

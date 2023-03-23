import threading
from django.shortcuts import render
from teams.views import (team_logo,
                        players_img,
                        nba_players,
                        nba_teams_id_name)


def player_details(request, player_name):
    """return player's details and stats."""
    nbaplayers = nba_players()
    nba_team = nba_teams_id_name()
    player_team = nbaplayers[player_name].get('team')
    logo = team_logo(nba_team[player_team].get('id'))
    context = {'player_name': player_name,
               'position': nbaplayers[player_name].get('position'),
               'player_img': players_img(nbaplayers[player_name].get('id')),
               'player_team': player_team,
               'player_jersey_number': nbaplayers[player_name].get('jersey number'),
               'logo': logo}

    return render(request, 'player/player_details.html', context=context)

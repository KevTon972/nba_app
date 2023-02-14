from django.shortcuts import render
from decouple import config

import json
import requests

headers = {
        "X-RapidAPI-Key": config('X-RapidAPI-Key'),
        "X-RapidAPI-Host": config('X-RapidAPI-Host')
    }
nba_teams = {}
players = {}
test = {}

team_managers = {}
team_players = []
positions = []
jersey_numbers = []

def nba_teams_id_name():
    '''collect nba id and name from api'''
    url = "https://basketapi1.p.rapidapi.com/api/basketball/category/15/events/16/1/2023"
    response = json.loads(requests.request("GET", url, headers=headers).text)
    i = 0

    while i < 17:
        if response['events'][i]['tournament']['name'] == 'NBA':
            if response['events'][i]['tournament']['name'] not in nba_teams:
                nba_teams[response['events'][i]['awayTeam']['name']] = {
                    'id': response['events'][i]['awayTeam']['id'],
                }
                nba_teams[response['events'][i]['homeTeam']['name']] = {
                    'id': response['events'][i]['homeTeam']['id'],
                }
        i += 1
    return nba_teams


def nba_players():
    '''collect nba players_name, players_id, players_positions and jersey_number from each teams'''
    nba_teams = nba_teams_id_name()
    team_id = [nba_teams[key]['id'] for key in nba_teams]
    team_names = [key for key in nba_teams]

    for id in team_id:
        url = f"https://basketapi1.p.rapidapi.com/api/basketball/team/{id}/players"
        response = json.loads(requests.request("GET", url, headers=headers).text)

        for name in team_names:
            i = 0
            while i < len(response['players']):
                if id == nba_teams[name]['id']:
                    players[response['players'][i]['player']['name']] = {
                    'position': response['players'][i]['player']['position'],
                    'jersey number': response['players'][i]['player']['shirtNumber'],
                    'id': response['players'][i]['player']['id'],
                    'team': name
                }
                i += 1
    return players


def team_manager():
    '''collect manager's names from each teams'''
    nba_teams = nba_teams_id_name()
    teams_names = [key for key in nba_teams]
    match_id = []
    managers_id = []

    for number in range(4, 6):
        url = f"https://basketapi1.p.rapidapi.com/api/basketball/matches/{number}/4/2022"
        response = json.loads(requests.request("GET", url, headers=headers).text)
        i = 0

        while i < 11:
            if response['events'][i]['tournament']['name'] == 'NBA':
                if response['events'][i]['id'] not in match_id:
                    match_id.append(response['events'][i]['id'])
            i += 1

    for id in match_id:
        url = f"https://basketapi1.p.rapidapi.com/api/basketball/match/{id}/managers"
        response = json.loads(requests.request("GET", url, headers=headers).text)
        managers_id.append(response['awayManager']['id'])
        managers_id.append(response['homeManager']['id'])

    for id in managers_id:
        url = f"https://basketapi1.p.rapidapi.com/api/basketball/manager/{id}"
        response = json.loads(requests.request("GET", url, headers=headers).text)

        try:
            for team_name in teams_names:
                if response['manager']['team']['name'] == team_name:
                    nba_teams[team_name]['manager'] = response['manager']['name']
        except TypeError:
            continue
    return nba_teams


def teams_list(request):
    '''afficher teams and their logos in teams-list template'''
    nba_teams = nba_teams_id_name()
    team_names = [key for key in nba_teams]

    return render(request, 'teams/teams-list.html', context={'teams': team_names})


def team_details(request, team_name):

    nbaplayers = nba_players()
    manager = team_manager()
    players_names = [key for key in nbaplayers]
    coach = ''

    if manager[team_name]['manager']:
        coach = manager[team_name]['manager']



    for player_name in players_names:
        if nbaplayers[player_name]['team'] == team_name:
            team_players.append(player_name)
            positions.append(nbaplayers[player_name]['position'])
            jersey_numbers.append(nbaplayers[player_name]['jersey number'])

    context = {'team_name': team_name,
                'team_starter_players': team_players[:5],
                'starter_positions': positions[:5],
                'team_bench': team_players[5:],
                'bench_positions': positions[5:],
                'jersey_numbers': jersey_numbers,
                'coach': coach}

    return render(request, 'teams/team_details.html', context=context)
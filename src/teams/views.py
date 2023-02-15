from django.shortcuts import render
from decouple import config

import json
import requests

headers = {
        "X-RapidAPI-Key": config('X-RapidAPI-Key'),
        "X-RapidAPI-Host": config('X-RapidAPI-Host')
    }

def nba_teams_id_name():
    '''collect nba id and name from api'''
    nba_teams = {}
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
    team_players = []
    players = {}

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


def team_manager(team):
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

    return nba_teams[team]['manager']


def team_next_match(team):
    """collect team's next match."""
    nba_teams = nba_teams_id_name()
    team_id = nba_teams[team]['id']
    url = f"https://basketapi1.p.rapidapi.com/api/basketball/team/{team_id}/matches/next/0"
    response = json.loads(requests.request("GET", url, headers=headers).text)

    if response['events'][0]['awayTeam']['name'] == team:
        return response['events'][0]['homeTeam']['name']
    return response['events'][0]['awayTeam']['name']


def team_last_match(team):
    """collect team's last match."""
    last_macth = {}
    nba_teams = nba_teams_id_name()
    team_id = nba_teams[team]['id']
    url = f"https://basketapi1.p.rapidapi.com/api/basketball/team/{team_id}/matches/previous/0"
    response = json.loads(requests.request("GET", url, headers=headers).text)
    last_match_indx = len(response['events']) - 1

    if response['events'][last_match_indx]['awayTeam']['name'] == team:
        last_macth = {
            f'{team}': team,
            f'{team}_score': response['events'][last_match_indx]['awayScore']['display'],
            'other_team': response['events'][last_match_indx]['homeTeam']['name'],
            'other_team_score': response['events'][last_match_indx]['homeScore']['display']
        }
        return last_macth
    else:
        last_macth = {
            f'{team}': team,
            f'{team}_score': response['events'][last_match_indx]['homeScore']['display'],
            'other_team': response['events'][last_match_indx]['awayTeam']['name'],
            'other_team_score': response['events'][last_match_indx]['awayScore']['display']
        }
        return last_macth


def teams_list(request):
    '''display teams and their logos in teams-list template'''
    nba_teams = nba_teams_id_name()
    team_names = [key for key in nba_teams]

    return render(request, 'teams/teams-list.html', context={'teams': team_names})


def team_details(request, team_name):
    """display team's players, coach, last match and next match"""
    nbaplayers = nba_players()
    manager = team_manager(team_name)
    next_opponent =team_next_match(team_name)
    last_match = team_last_match(team_name)
    players_names = [key for key in nbaplayers]
    team_players = []
    positions = []
    jersey_numbers = []
    coach = ''

    if manager:
        coach = manager

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
                'coach': coach,
                'next_opponent': next_opponent,
                'team_score': last_match[f'{team_name}_score'],
                'last_opponent': last_match['other_team'],
                'opponent_score': last_match['other_team_score'],
                }

    return render(request, 'teams/team_details.html', context=context)

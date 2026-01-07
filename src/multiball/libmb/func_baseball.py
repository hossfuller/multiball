#!/usr/bin/env python3

import pprint
import requests

from typing import Optional

from . import constants as const


## -------------------------------------------------------------------------- ##
## STATCAST FUNCTIONS
## -------------------------------------------------------------------------- ##

def convert_int_to_ordinal_str(n):
    n_str = str(n)
    if n_str[-1] == '1':
        n_str = n_str + 'st'
    elif n_str[-1] == '2':
        n_str = n_str + 'nd'
    elif n_str[-1] == '3':
        n_str = n_str + 'rd'
    else:
        n_str = n_str + 'th'
    return n_str


def build_mlb_player_display_string(player: list, verbose_bool: Optional[bool] = False) -> str:
    player_string = f"{player['name']} ({player['hand']}) - {player['team']}"
    if verbose_bool:
        player_string = player_string + f" [id = {player['id']}]"
    return player_string


def get_mlb_game_deets(game: list, verbose_bool: Optional[bool] = False) -> list:
    game_deets = {
        'home': {
            'team'       : game['teams']['home']['team']['name'] if 'name' in game['teams']['home']['team'] else 'N/A',
            'final_score': game['teams']['home']['score'] if 'score' in game['teams']['home'] else None,
            'wins'       : game['teams']['home']['leagueRecord']['wins'],
            'losses'     : game['teams']['home']['leagueRecord']['losses'],
            'pct'        : game['teams']['home']['leagueRecord']['pct'],
        },
        'away': {
            'team'       : game['teams']['away']['team']['name'] if 'name' in game['teams']['away']['team'] else 'N/A',
            'final_score': game['teams']['away']['score'] if 'score' in game['teams']['away'] else None,
            'wins'       : game['teams']['away']['leagueRecord']['wins'],
            'losses'     : game['teams']['away']['leagueRecord']['losses'],
            'pct'        : game['teams']['away']['leagueRecord']['pct'],
        },
        'description': game['seriesDescription'],
        'date'       : game['officialDate'],
        'innings'    : get_mlb_game_total_innings(game['gamePk'], verbose_bool),
        'game_pk'    : game['gamePk'],
    }
    if verbose_bool:
        pprint.pprint(game)
        print("---------->")
        pprint.pprint(game_deets)

    return game_deets


def get_mlb_games_for_date(date_str: str, verbose_bool: Optional[bool] = False) -> list:
    url = const.MLB_STATS_BASE_URL + const.MLB_STATS_SCHEDULE_STUB
    params = {
        "sportId": 1,
        "date": date_str
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    games = []
    for date_block in data.get("dates", []):
        games.extend(date_block.get("games", []))
    return games


def get_mlb_game_total_innings(game_pk: str, verbose_bool: Optional[bool] = False) -> int:
    live_feed_url = const.MLB_STATS_BASE_URL + const.MLB_STATS_LIVE_FEED_STUB.replace('<<GAME_PK>>', str(game_pk))
    response = requests.get(live_feed_url, timeout=10)
    response.raise_for_status()
    data = response.json()

    if verbose_bool:
        pprint.pprint(data)

    all_plays = data.get("liveData", {}).get("plays", {}).get("allPlays", [])
    return all_plays[-1]['about']['inning']


def get_mlb_player_details(player_id: int, verbose_bool: Optional[bool] = False) -> list:
    player_details_url = const.MLB_STATS_BASE_URL + const.MLB_STATS_PLAYER_STUB.replace('<<PLAYER_ID>>', str(player_id))
    response = requests.get(player_details_url, timeout=10)
    response.raise_for_status()
    data = response.json()

    if verbose_bool:
        pprint.pprint(data)

    player_details = {
        'id'              : data['people'][0]['id'],
        'link'            : data['people'][0]['link'],
        'name'            : data['people'][0]['fullName'],
        'birthdate'       : data['people'][0]['birthDate'],
        'height'          : data['people'][0]['height'],
        'jersey_number'   : data['people'][0]['primaryNumber'] if 'primaryNumber' in data['people'][0] else None,
        'primary_position': data['people'][0]['primaryPosition']['abbreviation'],
        'pitches'         : data['people'][0]['pitchHand']['code'],
        'hits'            : data['people'][0]['batSide']['code'],
        'strike_zone_top' : data['people'][0]['strikeZoneTop'],
        'strike_zone_bot' : data['people'][0]['strikeZoneBottom']
    }

    return player_details


## -------------------------------------------------------------------------- ##
## MODE FUNCTIONS
## -------------------------------------------------------------------------- ##

def get_mlb_events_from_single_game(mode: str, game: list, verbose_bool: Optional[bool] = False) -> list:
    events    = []
    all_plays = []

    try:
        live_feed_url = const.MLB_STATS_BASE_URL + game['link']
        if verbose_bool:
            print(f"Live feed URL: {live_feed_url}")
        # print(f"Live feed URL: {live_feed_url}")

        response = requests.get(live_feed_url, timeout=10)
        response.raise_for_status()
        data      = response.json()
        all_plays = data.get("liveData", {}).get("plays", {}).get("allPlays", [])
    except Exception as e:
        print(f"[ERROR] '{live_feed_url}' failed: {e}")

    # Identify events at the play-result level (most reliable)
    for play in all_plays:
        derp_event = None
        
        if mode == 'derp':
            ## Enumerate all the derp plays
            derp_plays = []
            ## derp_event = ??
            continue 
        elif mode == "hbp":
            if play.get("result", {}).get("event") != "Hit By Pitch":
                continue
        elif mode == "triples":
            if (
                play.get("result", {}).get("event") != "Triple Play" and 
                play.get("result", {}).get("event") != "Triple"
            ):
                continue

        # Find the final pitch event to extract play_id
        play_id = None
        pitch_events = [
            e for e in play.get("playEvents", [])
            if e.get("isPitch")
        ]

        if pitch_events:
            play_id = pitch_events[-1].get("playId")
        
        if verbose_bool:
            print("@@-- Start --@@")
            pprint.pprint(play['playEvents'][-1])
            print("@@--  End  --@@")

        events.append({
            "game_pk"    : game['gamePk'],
            "play_id"    : play_id,
            "batter": {
                "id"  : play["matchup"]["batter"]["id"],
                "name": play["matchup"]["batter"]["fullName"],
                "hand": play["matchup"]["batSide"]["code"],
                "team": game['teams']['away']['team']['name'] if play["about"]["halfInning"] == "top" else game['teams']['home']['team']['name']
            },
            "pitcher": {
                "id"  : play["matchup"]["pitcher"]["id"],
                "name": play["matchup"]["pitcher"]["fullName"],
                "hand": play["matchup"]["pitchHand"]["code"],
                "team": game['teams']['away']['team']['name'] if play["about"]["halfInning"] == "bottom" else game['teams']['home']['team']['name']
            },
            "at_bat": {
                'home_score'  : play['result']['homeScore'],
                'away_score'  : play['result']['awayScore'],
                'balls'       : play['playEvents'][-1]["count"]["balls"],
                'strikes'     : play['playEvents'][-1]["count"]["strikes"],
                'outs_when_up': play['playEvents'][-1]["count"]["outs"],
                'inning'      : play["about"]["inning"],
                'half_inning' : play["about"]["halfInning"],
                'start_speed' : play['playEvents'][-1]['pitchData']['startSpeed'] if 'pitchData' in play['playEvents'][-1] and 'startSpeed' in play['playEvents'][-1]['pitchData'] else None,
                'end_speed'   : play['playEvents'][-1]['pitchData']['endSpeed'] if 'pitchData' in play['playEvents'][-1] and 'endSpeed' in play['playEvents'][-1]['pitchData'] else None,
                'plate_x'     : play['playEvents'][-1]['pitchData']['coordinates']['pX'] if 'pitchData' in play['playEvents'][-1] and 'pX' in play['playEvents'][-1]['pitchData']['coordinates'] else None,   ## in feet!
                'plate_z'     : play['playEvents'][-1]['pitchData']['coordinates']['pZ'] if 'pitchData' in play['playEvents'][-1] and 'pZ' in play['playEvents'][-1]['pitchData']['coordinates'] else None,   ## in feet!
                'pitch_name'  : play['playEvents'][-1]['details']['type']['description'] if 'type' in play['playEvents'][-1]['details'] and play['playEvents'][-1]['details']['type'] != 'no_pitch' else None,
            },
            "description": play['result']['description'],
            "derp_event": derp_event,
        })

    return events

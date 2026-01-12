#!/usr/bin/env python3

import os
import pprint

from datetime import datetime
from typing import List, Optional, Tuple

from . import constants as const
from . import func_baseball as bb


## -------------------------------------------------------------------------- ##
## SKEET FUNCTIONS
## -------------------------------------------------------------------------- ##

def cleanup_after_skeet(
    mode: str,
    game_pk: int,
    play_id: str,
    verbose_bool: Optional[bool] = False,
) -> list:
    files_removed = list()

    plot_dir  = const.HBP_PATHS['plot_dir_fullpath']
    skeet_dir = const.HBP_PATHS['skeet_dir_fullpath']
    video_dir = const.HBP_PATHS['video_dir_fullpath']
    if mode == "derp":
         plot_dir  = const.DERP_PATHS['plot_dir_fullpath']
         skeet_dir = const.DERP_PATHS['skeet_dir_fullpath']
         video_dir = const.DERP_PATHS['video_dir_fullpath']
    elif mode == "triples":
        plot_dir  = const.TRIPLES_PATHS['plot_dir_fullpath']
        skeet_dir = const.TRIPLES_PATHS['skeet_dir_fullpath']
        video_dir = const.TRIPLES_PATHS['video_dir_fullpath']

    for plot_file in os.listdir(plot_dir):
        if plot_file.startswith(f"{game_pk}_{play_id}"):
            plot_filepath = os.path.join(plot_dir, plot_file)
            os.remove(plot_filepath)
            files_removed.append(plot_filepath)

    for skeet_file in os.listdir(skeet_dir):
        if skeet_file.startswith(f"{game_pk}_{play_id}"):
            skeet_filepath = os.path.join(skeet_dir, skeet_file)
            os.remove(skeet_filepath)
            files_removed.append(skeet_filepath)

    ## Remove video file.
    video_filepath = os.path.join(video_dir, f"{game_pk}_{play_id}.mp4")
    if os.path.isfile(video_filepath):
        os.remove(video_filepath)
        files_removed.append(video_filepath)

    return files_removed


def read_skeet_text(filename: str, verbose_bool: Optional[bool] = False) -> str:
    file_contents = ''
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            file_contents = f.read()
    except FileNotFoundError:
        print(f"Error: '{filename}' was not found.")
    except Exception as e:
        print(f"Something bad happened: {e}")
    return file_contents


def trim_skeet_text(skeet_list: List[str], verbose_bool: Optional[bool] = False) -> List[str]:
    idx                    = -2  ## event description location in skeet.
    most_characters_length = 0

    if not skeet_list or len(skeet_list) == 0:
        pass
    elif len(skeet_list) == 1:
        ## How did a skeet_list with only one element get in?
        allowed = max(const.SKEETS_CHAR_LIMIT - most_characters_length, 0)
        if len(skeet_list[0]) > allowed:
            skeet_list[idx] = skeet_list[idx][:allowed-3] + '...'
    else:
        for i, s in enumerate(skeet_list):
            if i != (len(skeet_list) + idx):
                most_characters_length = most_characters_length + len(s)
        allowed = max(const.SKEETS_CHAR_LIMIT - most_characters_length, 0)
        if len(skeet_list[idx]) > allowed:
            skeet_list[idx] = skeet_list[idx][:allowed-3] + '...'

    return skeet_list


def write_desc_skeet_text(mode: str, game: list, event: list, verbose_bool: Optional[bool] = False) -> str:
    '''Returns the filename of the skeet, not the actual skeet!'''
    if verbose_bool:
        print("# --------- >")
        pprint.pprint(game)
        print("# ---")
        pprint.pprint(event)

    ## Defaults to HBP emoji.
    mode_emoji = "⚾💥"
    if mode == "derp":
        mode_emoji = "⚾🤡"
    elif mode == 'triples':
        mode_emoji = "⚾⚾⚾"

    game_datetime_obj = datetime.strptime(game['date'], "%Y-%m-%d")
    date_str          = f"{mode_emoji} {game_datetime_obj.strftime("%d %B %Y")} {mode_emoji[::-1]}"
    series_desc_str   = f"Game: {game['description']}"

    ## If the game is finished, there'll be a final score.
    winning_team  = None
    winning_score = None
    losing_score  = None
    if ('final_score' in game['home'] and
        game['home']['final_score'] is not None and
        game['away']['final_score'] is not None
    ):
        winning_team       = game['away']['team']
        winning_score      = game['away']['final_score']
        losing_score       = game['home']['final_score']
        if game['home']['final_score'] > game['away']['final_score']:
            winning_team  = game['home']['team']
            winning_score = game['home']['final_score']
            losing_score  = game['away']['final_score']

    ## If nothing happened, add that to the skeet_strs list.
    if len(event) == 0:
        team_str           = f"⚾🧤 {game['away']['team']} at {game['home']['team']} 🧤⚾"
        nobody_got_hit_str = f"👍 Nothing happened! What a boring game...."

        winning_line_str = ''
        if winning_team is not None:
            winning_line_str = f"{winning_team} won {winning_score}-{losing_score} in {game['innings']} innings"

        skeet_strs = [team_str, date_str, series_desc_str, nobody_got_hit_str, winning_line_str]

    ## Something cool happened!
    else:
        game_is_tied   = False
        leading_team   = game['away']['team']
        leading_score  = event['at_bat']['away_score']
        trailing_score = event['at_bat']['home_score']
        if event['at_bat']['home_score'] > event['at_bat']['away_score']:
            leading_team   = game['home']['team']
            leading_score  = event['at_bat']['home_score']
            trailing_score = event['at_bat']['away_score']
        elif event['at_bat']['home_score'] == event['at_bat']['away_score']:
            game_is_tied = True

        # teamname_str = bb.get_mlb_team_attribute(leading_team, 'teamname')
        teamname_str = None
        if teamname_str is None:
            teamname_str = leading_team
        score_str   = f"{teamname_str} up {leading_score}-{trailing_score}"
        if game_is_tied:
            score_str = f"tied at {leading_score}-{trailing_score}"

        batter_str      = f"Batter: {bb.build_mlb_player_display_string(event['batter'])}"
        pitcher_str     = f"Pitcher: {bb.build_mlb_player_display_string(event['pitcher'])}"
        count_str       = f"The Play: {bb.build_event_count(event['at_bat'])}, {score_str}"
        pitch_str       = f"The Pitch: {bb.build_event_pitch(event['at_bat'])}"

        final_score_str = ''
        if 'final_score' in game['home']:
            final_score_str = f"Final: {winning_team} won {winning_score}-{losing_score} in {game['innings']} innings."

        ## Defaults to HBP skeet.
        skeet_strs = [date_str, series_desc_str, pitcher_str, batter_str, count_str, pitch_str, final_score_str]
        if mode == "derp" and event['event'] == 'Balk':
            skeet_strs = trim_skeet_text([date_str, series_desc_str, pitcher_str, count_str, f"Balk: {event['description']}", final_score_str])
        elif mode == "derp" and event['event'] == 'Batter Interference':
            skeet_strs = trim_skeet_text([date_str, series_desc_str, pitcher_str, batter_str, count_str, f"Interference: {event['description']}", final_score_str])
        elif mode == "derp" and event['event'] == 'Catcher Interference':
            skeet_strs = trim_skeet_text([date_str, series_desc_str, count_str, f"Interference: {event['description']}", final_score_str])
        elif mode == "derp" and event['event'] == 'Field Error':
            skeet_strs = trim_skeet_text([date_str, series_desc_str, count_str, f"Error: {event['description']}", final_score_str])
        elif mode == "triples" and event['event'] in const.TRIPLES_EVENTS:
            skeet_strs = trim_skeet_text([date_str, series_desc_str, count_str, f"💥{event['description']}💥", final_score_str])

    total_skeet_str = "\n".join(skeet_strs)
    total_skeet_length = len(total_skeet_str)
    # if total_skeet_length > const.SKEETS_CHAR_LIMIT:
    #     raise Exception("Basic skeet text is already too long!")

    ## Build filename
    skeet_dir = const.HBP_PATHS['skeet_dir_fullpath']
    if mode == "derp":
        skeet_dir = const.DERP_PATHS['skeet_dir_fullpath']
    elif mode == "triples":
        skeet_dir = const.TRIPLES_PATHS['skeet_dir_fullpath']

    skeet_file_path = os.path.join(skeet_dir, f"{game['game_pk']}_clean.txt")
    if len(event) > 0:
        skeet_file_path = os.path.join(skeet_dir, f"{game['game_pk']}_{event['play_id']}_desc.txt")

    with open(skeet_file_path, 'w', encoding='utf-8') as f:
        f.write(total_skeet_str)

    return skeet_file_path

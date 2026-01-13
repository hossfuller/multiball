#!/usr/bin/env python3

## -------------------------------------------------------------------------- ##
## Multiball Downloader
## Using statcast data, builds a skeet and downloads the video. Also updates
## the appropriate database for the plotter/skeet scripts.
## -------------------------------------------------------------------------- ##

import os
import pprint
import sys
import time

from datetime import datetime, timedelta
from typing import Optional

# Import application modules
from .libmb import basic as bsc
from .libmb import constants as const
from .libmb import func_baseball as bb
from .libmb import func_database as dbmgr
from .libmb import func_skeet as sk

from .libmb.cmdparser import CmdParser
from .libmb.configurator import ConfigReader
from .libmb.logger import PrintLogger


## -------------------------------------------------------------------------- ##
## SETUP
## -------------------------------------------------------------------------- ##

## Read and update configuration
config = ConfigReader(bsc.verify_file_path(bsc.sanitize_path(const.DEFAULT_CONFIG_INI_FILE)))

backward       = False
get_latest     = False
mode           = "hbp"
num_days       = 1
skip_video_dl  = False
sleep_time     = float(config.get("client_parameters", "sleep_time"))
start_date     = datetime.strftime(datetime.now() - timedelta(days=1), '%Y-%m-%d')
test_mode      = bool(int(config.get("operations", "test_mode")))
verbose        = bool(int(config.get("operations", "verbose_output")))
double_verbose = bool(int(config.get("operations", "double_verbose")))


## Create parser and add arguments
parser = CmdParser(description="Reads database for events, then prepares skeets and downloads videos.")
parser.add_arguments_from_dict({
    ("-b", "--backward"): {
        "action" : "store_true",
        "default": backward,
        "help"   : "Go backward in time instead of the default forward",
    },
    ("-d", "--num-days"): {
        "type"   : int,
        "default": num_days,
        "help"   : "Number of days to check for events. Defaults to '%(default)s'.",
    },
    ("-g", "--get-latest"): {
        "action" : "store_true",
        "default": get_latest,
        "help"   : "Get the latest event that hasn't been downloaded yet",
    },
    ("-m", "--mode"): {
        "type"    : str,
        "required": True,
        "choices" : ["derp", "hbp", "triples"],
        "default" : mode,
        "help"    : "Specify which baseball mode to populate",
    },
    ("-s", "--start-date"): {
        "type"   : bsc.parse_date_string,
        "default": start_date,
        "help"   : "Start date to check for events. Must be in '2025-11-01' format. Defaults to '%(default)s'.",
    },
    ("--skip-video-dl"): {
        "action" : "store_true",
        "default": skip_video_dl,
        "help"   : "Skips video download for each event",
    },
})
args = parser.parse_args()

## Now pull config and command line action together.
if args.get("backward"):
    backward = True
if args.get("get_latest"):
    get_latest = args.get("get_latest")
if args.get("mode"):
    mode = args.get("mode")
if args.get("num_days") and num_days > 0:
    num_days = args.get("num_days")
if args.get("skip_video_dl"):
    skip_video_dl = True
if args.get("start_date"):
    start_date = args.get("start_date")
if args.get("test_mode"):
    config.set("operations", "test_mode", "1")
    test_mode = True
if args.get("verbose"):
    config.set("operations", "verbose_output", "1")
    verbose = True
if args.get("double_verbose"):
    config.set("operations", "verbose_output", "1")
    config.set("operations", "double_verbose", "1")
    verbose        = True
    double_verbose = True

## Set up logging
if not args.get("nolog"):
    prefix_val = config.get("logging_prefixes", "downloader_prefix")
    sys.stdout = PrintLogger(
        config.get("paths", "log_dir"),
        f"{mode}_{prefix_val}",
    )


# -------------------------------------------------------------------------- ##
# MAIN ACTION
# -------------------------------------------------------------------------- ##

def main(start_date: Optional[str] = None) -> int:
    try:
        print()

        if verbose:
            print(config.get_all())
            print()

        print("="*80)
        print(f" ⚾ {config.get('app', 'name')} ⚾ ~~> ⏬ {mode.capitalize()} Downloader")
        print("="*80)
        start_time = time.time()

        if get_latest:
            start_date = dbmgr.get_latest_date_that_hasnt_been_downloaded(mode, double_verbose)

        total_mode_events = 0
        for xday in range(num_days):
            print("--->")
            print(f'⚾ Checking {start_date} for games...', end='')
            mlb_games = bb.get_mlb_games_for_date(start_date)
            print(f'found {len(mlb_games)} game(s) that day. ⚾')
            print()

            ## "GAME" FOR LOOP
            ## Loops through all the games for the day.
            mode_event_count = 0
            for i, game in enumerate(mlb_games):
                game_deets = bb.get_mlb_game_deets(game, double_verbose)
                mode_events = bb.get_mlb_events_from_single_game(mode, game, double_verbose)

                if double_verbose:
                    print("@ --------- GAME DEETS --------- ")
                    pprint.pprint(game_deets)
                    print("@ --------- MODE EVENTS --------- ")
                    pprint.pprint(mode_events)
                    print("@ ------------ END ------------- ")
                    print()

                ## No events during this game....
                if mode_events is None or len(mode_events) == 0:
                    skeet_filename = sk.write_desc_skeet_text(mode, game_deets, [], double_verbose)
                    if verbose:
                        print(f"{i + 1}. Skeet File: {skeet_filename}")
                    skeet_text = sk.read_skeet_text(skeet_filename)
                    print(f"{skeet_text}")
                    print()
                    continue

                ## MODE EVENT FOR LOOP
                ## Loops through all the mode events.
                for j, event in enumerate(mode_events):
                    mode_event_count = mode_event_count + 1

                    ## Check if event is already in database. If not, add it.
                    dbdata = dbmgr.get_event_play_data(mode, event['play_id'], double_verbose)
                    if len(dbdata) == 0:
                        dbinsert_result = dbmgr.insert_row(mode, game_deets, event, double_verbose)
                        if dbinsert_result:
                            print(f"👍 HBP {event['play_id']} added to database.")
                        else:
                            raise Exception("Something is definitely wrong with the database file.")

                    ## Generate skeet
                    skeet_filename = sk.write_desc_skeet_text(mode, game_deets, event, double_verbose)
                    if verbose:
                        print(f"{i + 1}. Skeet File: {skeet_filename}")
                    ## Print skeet to screen
                    skeet_text = sk.read_skeet_text(skeet_filename)
                    print(f"{skeet_text}")

                    ## Finally, download the video.
                    if event['play_id'] is None or event['play_id'] == '':
                        print(f"😢 Video unavailable.")
                    else:
                        ## download video
                        if test_mode:
                            print("Pretending to download video....")
                        elif skip_video_dl:
                            pass
                        else:
                            video_filename = bb.download_baseball_savant_play(mode, game['gamePk'], event['play_id'], verbose)
                            print(f"VIDEO: {video_filename}")

                            if os.path.exists(video_filename):
                                dbmgr.set_download_flag(mode, event['play_id'])

                    print()
            print(f"💥 There were {mode_event_count} total {mode.capitalize()} events for this day. 💥")
            print("<---\n")
            total_mode_events = total_mode_events + mode_event_count

            if backward:
                start_date = bsc.subtract_one_day_from_date(start_date)
            else:
                start_date = bsc.add_one_day_to_date(start_date)

        print(f"⚾💥 Captured {total_mode_events} during this run.")

        print()
        end_time = time.time()
        elapsed = end_time - start_time
        print("="*80)
        print(f'Completed in {elapsed:.2f} seconds')
        print("="*80)
        print()
        return 0

    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main(start_date))

#!/usr/bin/env python3

## -------------------------------------------------------------------------- ##
## Multiball Plotter
## For certain events, we want to plot the action.
## -------------------------------------------------------------------------- ##

import os
import pprint
import sys
import time

# Import application modules
from .libmb import basic as bsc
from .libmb import constants as const
from .libmb import func_baseball as bb
from .libmb import func_database as dbmgr
from .libmb import func_plot as plotter
from .libmb import func_skeet as sk

from .libmb.cmdparser import CmdParser
from .libmb.configurator import ConfigReader
from .libmb.logger import PrintLogger


## -------------------------------------------------------------------------- ##
## SETUP
## -------------------------------------------------------------------------- ##

## Read and update configuration
config = ConfigReader(
    bsc.verify_file_path(bsc.sanitize_path(const.DEFAULT_CONFIG_INI_FILE))
)

#fmt: off
mode           = "hbp"
test_mode      = bool(int(config.get("operations", "test_mode")))
verbose        = bool(int(config.get("operations", "verbose_output")))
double_verbose = bool(int(config.get("operations", "double_verbose")))
#fmt: on

## Create parser and add arguments
parser = CmdParser(description="Analyzes event data and generates plots.")
parser.add_arguments_from_dict(
    {
        ("-m", "--mode"): {
            "type": str,
            "required": True,
            "choices": ["derp", "hbp", "triples"],
            "default": mode,
            "help": "Specify which baseball mode to populate",
        },
    }
)
args = parser.parse_args()

## Now pull config and command line action together.
if args.get("mode"):
    mode = args.get("mode")
if args.get("test_mode"):
    config.set("operations", "test_mode", "1")
    test_mode = True
if args.get("verbose"):
    config.set("operations", "verbose_output", "1")
    verbose = True
if args.get("double_verbose"):
    config.set("operations", "verbose_output", "1")
    config.set("operations", "double_verbose", "1")
    verbose = True
    double_verbose = True

## Set up logging
if not args.get("nolog"):
    prefix_val = config.get("logging_prefixes", "plotter_prefix")
    sys.stdout = PrintLogger(
        config.get("paths", "log_dir"),
        f"{mode}_{prefix_val}",
    )


## -------------------------------------------------------------------------- ##
## MAIN ACTION
## -------------------------------------------------------------------------- ##


def main() -> int:
    try:
        print()

        if verbose:
            print(config.get_all())
            print()

        print("=" * 80)
        print(f" ⚾ {config.get('app', 'name')} ⚾ ~~> ⏬ {mode.capitalize()} Plotter")
        print("=" * 80)
        start_time = time.time()

        ## Comment this part out if/when we figure out what sort of plots to do
        ## for everything besides HBP events.
        if mode == "derp" or mode == "triples":
            raise ValueError(f"🙀 Unsupported event. Finishing...\n")

        ## The plan:
        ##  1. Get a list of all current skeets in skeet_dir waiting to go.
        ##  2. Skip any files that don't end in '_desc.txt'
        ##  3. Check if it's already been skeeted. If so, remove all files.
        ##  4. Query the play_id. This is 'current_play'.
        ##  5. Extract the season, batter_id, and pitcher_id.
        ##  6a. Query the season. This is 'all_season_data'.
        ##  6b. Query the batter_id. This is 'batter_career_data'.
        ##  6c. Query the pitcher_id. This is 'pitcher_career_data'.
        ##  7a. Plot all_season_data as gray, current_play color coded to end_speed.
        ##  7b. Plot batter_career_data as gray, current_play color coded to end_speed.
        ##  7c. Plot pitcher_career_data as gray, current_play color coded to end_speed.

        ## 1. Get a list of all current skeets in skeet_dir waiting to go.
        plot_dir = const.HBP_PATHS["plot_dir_fullpath"]
        skeet_dir = const.HBP_PATHS["skeet_dir_fullpath"]
        if mode == "derp":
            plot_dir = const.DERP_PATHS["plot_dir_fullpath"]
            skeet_dir = const.DERP_PATHS["skeet_dir_fullpath"]
        elif mode == "triples":
            plot_dir = const.TRIPLES_PATHS["plot_dir_fullpath"]
            skeet_dir = const.TRIPLES_PATHS["skeet_dir_fullpath"]

        skeet_dir_files = sorted(os.listdir(skeet_dir))
        if verbose:
            pprint.pprint(skeet_dir_files)

        for skeet_file in skeet_dir_files:
            full_skeet_filename = os.path.join(skeet_dir, skeet_file)
            skeet_root, ext = os.path.splitext(skeet_file)
            skeet_parts = skeet_root.split("_")

            ## Not a file we want to work with
            if not skeet_parts[0].isdigit():
                print()
                continue

            game_pk = skeet_parts[0]
            play_id = skeet_parts[1]
            print(f"⚾ Game = {game_pk}, Play ID = {play_id}")

            ## 2. Skip any files that don't end in '_desc.txt'
            if skeet_parts[1] == "clean":
                ## We don't skeet out games where there are no HBP events.
                print(f"  😞 Nobody got hit during this game. Skipping.\n")
                os.remove(full_skeet_filename)
                continue
            elif skeet_parts[1] == "analyze":
                print(f"  😒 Current file is analysis information. Skipping.\n")
                continue

            ## 3. Check if it's already been skeeted. If so, remove all files.
            if dbmgr.has_been_skeeted(mode, play_id, verbose):
                print(f"  🤨 This event has already been skeeted!\n")
                sk.cleanup_after_skeet(mode, int(game_pk), play_id, verbose)
                continue

            ## 4. Query the play_id. This is 'current_play'.
            current_play = dbmgr.get_event_play_data(mode, play_id, verbose)
            if verbose:
                pprint.pprint(current_play)

            ##  5. Extract the season, batter_id, and pitcher_id.
            #fmt: off
            game_date          = current_play[0][2]
            season, month, day = game_date.split("-")
            pitcher_info       = bb.get_mlb_player_details(current_play[0][3], verbose)
            batter_info        = bb.get_mlb_player_details(current_play[0][4], verbose)
            #fmt: on
            if verbose:
                pprint.pprint(pitcher_info)
                pprint.pprint(batter_info)

            ##  6. Query the season, pitcher_id, batter_id.
            all_season_data = dbmgr.get_season_data(mode, int(season), verbose)
            pitcher_career_data = dbmgr.get_all_pitcher_data(
                mode, pitcher_info["id"], verbose
            )
            batter_career_data = dbmgr.get_all_batter_data(
                mode, batter_info["id"], verbose
            )
            print(f"   In {season} there have been {len(all_season_data)} HBP events.")
            print(
                f"   {pitcher_info['name']} ({pitcher_info['primary_position']}) has hit {len(pitcher_career_data)} batters in his career."
            )
            print(
                f"   {batter_info['name']} ({batter_info['primary_position']}) has been hit {len(batter_career_data)} times in his career."
            )

            if all_season_data and len(all_season_data) > 0:
                ##  7a. Plot all_season_data as gray, current_play color coded to end_speed.
                print(
                    f"   📊 Creating scatter plot for this {mode} against all {mode} events for {season}..."
                )
                plot_result = plotter.plot_hbp_current_play_against_season(
                    current_play, all_season_data, pitcher_info, batter_info, verbose
                )
                if not plot_result:
                    continue

                ##  7b. Plot batter_career_data as gray, current_play color coded to end_speed.
                print(
                    f"   📊 Creating scatter plot for this batter's career {mode} events..."
                )
                plot_result = plotter.plot_hbp_batter_play_against_career(
                    current_play, batter_career_data, batter_info, verbose
                )
                if not plot_result:
                    continue

                ##  7c. Plot pitcher_career_data as gray, current_play color coded to end_speed.
                print(
                    f"   📊 Creating scatter plot for this pitcher's career {mode} events..."
                )
                plot_result = plotter.plot_hbp_pitcher_play_against_career(
                    current_play, pitcher_career_data, pitcher_info, verbose
                )
                if not plot_result:
                    continue

                ## If we get to this point, all three plots have been created.
                dbmgr.set_analyzed_flag(mode, play_id, verbose)

            else:
                print(f"   ⚠️  No season data available for plotting.")

            print()

        end_time = time.time()
        elapsed = end_time - start_time
        print("=" * 80)
        print(f"Completed in {elapsed:.2f} seconds")
        print("=" * 80)
        print()
        return 0

    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

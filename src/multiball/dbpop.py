#!/usr/bin/env python3

## -------------------------------------------------------------------------- ##
## Multiball DB Populator
## Using statcast data, fills in a database of targetted plays we want to
## download/analyze/skeet in the future.
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

from .libmb.cmdparser import CmdParser
from .libmb.configurator import ConfigReader
from .libmb.logger import PrintLogger


## -------------------------------------------------------------------------- ##
## SETUP
## -------------------------------------------------------------------------- ##

## Read and update configuration
config = ConfigReader(bsc.verify_file_path(bsc.sanitize_path(const.DEFAULT_CONFIG_INI_FILE)))

backward       = False
mode           = "hbp"
num_days       = 1
sleep_time     = float(config.get("client_parameters", "sleep_time"))
start_date     = datetime.strftime(datetime.now() - timedelta(days=1), '%Y-%m-%d')
test_mode      = bool(int(config.get("operations", "test_mode")))
verbose        = bool(int(config.get("operations", "verbose_output")))
double_verbose = bool(int(config.get("operations", "double_verbose")))


## Create parser and add arguments
parser = CmdParser(description="Populates sqlite3 database with various baseball events.")
parser.add_arguments_from_dict({
    ("-b", "--backward"): {
        "action" : "store_true",
        "default": backward,
        "help"   : "Go backward in time instead of the default forward",
    },
    ("-d", "--num-days"): {
        "type"   : int,
        "default": num_days,
        "help"   : "Number of days to check for HBP events. Defaults to '%(default)s'.",
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
        "help"   : "Start date to check for HBP events. Must be in '2025-11-01' format. Defaults to '%(default)s'.",
    },
})
args = parser.parse_args()

## Now pull config and command line action together.
if args.get("backward"):
    backward = True
if args.get("mode"):
    mode = args.get("mode")
if args.get("num_days") and num_days > 0:
    num_days = args.get("num_days")
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
    prefix_val = config.get("logging_prefixes", "dbpopulator_prefix")
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
        print(f" ⚾ {config.get('app', 'name')} ⚾ ~~> 📈 {mode.capitalize()} DB Populator")
        print("="*80)
        start_time = time.time()

        ## First check if the database file already exists. If it doesn't,
        ## create it, then create the table.
        db_create_result = False
        db_definition = dbmgr.get_table_definition(mode, verbose)
        if os.path.exists(bsc.sanitize_path(db_definition["filename"])):
            print(f"💾 '{mode}' database file:  {db_definition["filename"]}")
        else:
            print(f"‼️ No database file exists for '{mode}'. Creating '{db_definition["filename"]}'...")
            db_create_result = dbmgr.create_database(mode, verbose)
            if db_create_result:
                print(f"💾 '{db_definition["filename"]}' has been created.")

        if os.path.getsize(db_definition["filename"]) == 0:
            db_create_result = dbmgr.create_database(mode, verbose)
        else:
            db_create_result = True

        if db_create_result:
            print(f"💾 '{mode}' database table: {db_definition["tablename"]}")
        else:
            raise Exception(f"❌ Database file/table is not in a condition for writing!")
        print()

        ## Now start in on parsing out baseball events based on mode.
        total_events = 0
        for xday in range(num_days):
            print(f'⚾ [{xday+1}/{num_days}] Checking {start_date} for games...', end='')
            mlb_games = bb.get_mlb_games_for_date(start_date)
            print(f'found {len(mlb_games)} game(s) that day. ⚾')

            ## "GAME" FOR LOOP
            ## Loops through all the games for the day.
            event_count = 0
            for i, game in enumerate(mlb_games):
                game_deets = bb.get_mlb_game_deets(game, double_verbose)
                events = bb.get_mlb_events_from_single_game(mode, game, double_verbose)
                ## The type of event is handled by the function itself when we
                ## pass it the mode. So we don't need to seperate out the mode
                ## events ourselves here.

                if double_verbose:
                    print("@ --------- GAME DEETS --------- ")
                    pprint.pprint(game_deets)
                    print("@ ----------- EVENTS ----------- ")
                    pprint.pprint(events)
                    print("@ ------------ END ------------- ")
                    print()

                ## "EVENT" FOR LOOP
                ## Loops through all the HBP events.
                for j, event in enumerate(events):
                    try:
                        dbinsert_result = dbmgr.insert_row(mode, game_deets, event)
                        event_count = event_count + 1

                        if dbinsert_result:
                            print(f"  {event_count:02}. 👍 {mode.upper()} {event['play_id']} added to database.")
                        else:
                            print(f"  {event_count:02}. 🦋 {mode.upper()} {event['play_id']} is already in the database.", end='')
                            if dbmgr.has_been_downloaded(mode, event['play_id'], verbose):
                                print(f" (dl)", end='')
                            if dbmgr.has_been_analyzed(mode, event['play_id'], verbose):
                                print(f" (nz)", end='')
                            if dbmgr.has_been_skeeted(mode, event['play_id'], verbose):
                                print(f" (sk)", end='')
                            print()
                    except KeyboardInterrupt:
                        dbmgr.delete_row(mode, event['play_id'])

                time.sleep(sleep_time)
            print(f"💥 There were {event_count} total {mode} events for this day. 💥")
            print()
            total_events = total_events + event_count

            if backward:
                start_date = bsc.subtract_one_day_from_date(start_date)
            else:
                start_date = bsc.add_one_day_to_date(start_date)

        print(f"⚾💥 Captured {total_events} during this run.")

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

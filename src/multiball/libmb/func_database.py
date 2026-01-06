#!/usr/bin/env python3

import os
import pprint

from . import basic as bsc
from . import constants as const
from .configurator import ConfigReader
from .sqlitemgr import SQLiteManager

from typing import Optional


## -------------------------------------------------------------------------- ##
## DATABASE CONFIG
## -------------------------------------------------------------------------- ##

config = ConfigReader(bsc.verify_file_path(bsc.sanitize_path(const.DEFAULT_CONFIG_INI_FILE)))


## -------------------------------------------------------------------------- ##
## DATABASE WRAPPER FUNCTIONS
## -------------------------------------------------------------------------- ##

def get_all_batter_data(mode: str, player_id: int, verbose_bool: Optional[bool] = False) -> list:
    return get_all_player_data(mode, player_id, "batter", verbose_bool)


def get_all_pitcher_data(mode: str, player_id: int, verbose_bool: Optional[bool] = False) -> list:
    return get_all_player_data(mode, player_id, "pitcher", verbose_bool)


def get_all_player_data(
    mode: str, 
    player_id: int, 
    player_type: str, 
    verbose_bool: Optional[bool] = False
) -> list:
    player_data = []
    table_definition = get_table_definition(mode, verbose_bool)

    player_types = ["batter", "pitcher"]
    if player_type not in player_types:
        return player_data

    with SQLiteManager(table_definition['filename']) as db:
        player_data = db.query_data(
            f"SELECT * FROM {table_definition['tablename']} WHERE {player_type}_id = ?",
            [player_id]
        )
    return player_data


def get_earliest_date(mode: str, verbose_bool: Optional[bool] = False) -> str:
    select_data = None
    table_definition = get_table_definition(mode, verbose_bool)
    with SQLiteManager(table_definition['filename']) as db:
        select_data = db.query_data(
            f"SELECT MIN(game_date) FROM {table_definition['tablename']}",
            []
        )
    return select_data[0][0]


def get_event_play_data(mode: str, play_id: str, verbose_bool: Optional[bool] = False) -> list:
    select_data = []
    table_definition = get_table_definition(mode, verbose_bool)
    with SQLiteManager(table_definition['filename']) as db:
        select_data = db.query_data(
            f"SELECT * FROM {table_definition['tablename']} WHERE play_id = ?",
            [play_id]
        )
    return select_data


def get_latest_date(mode: str, verbose_bool: Optional[bool] = False) -> str:
    select_data = None

    table_definition = get_table_definition(mode, verbose_bool)
    with SQLiteManager(table_definition['filename']) as db:
        select_data = db.query_data(
            f"SELECT MAX(game_date) FROM {table_definition['tablename']}",
            []
        )

    return select_data[0][0]


def get_latest_date_that_hasnt_been_downloaded(mode: str, verbose_bool: Optional[bool] = False) -> str:
    select_data = None
    table_definition = get_table_definition(mode, verbose_bool)
    with SQLiteManager(table_definition['filename']) as db:
        select_data = db.query_data(
            f"SELECT MAX(game_date) FROM {table_definition['tablename']} WHERE downloaded = 0",
            []
        )
    return select_data[0][0]


def get_season_data(mode: str, season: int, verbose_bool: Optional[bool] = False) -> list:
    season_data  = []
    season_start = f"{season}-01-01"
    season_end   = f"{season}-12-31"

    table_definition = get_table_definition(mode, verbose_bool)
    with SQLiteManager(table_definition['filename']) as db: 
        season_data = db.query_data(
            f"SELECT * FROM {table_definition['tablename']} WHERE game_date BETWEEN ? AND ?",
            [season_start, season_end]
        )
    return season_data


def get_season_year(mode: str, play_id: str, verbose_bool: Optional[bool] = False) -> str:
    current_play = get_event_play_data(mode, play_id, verbose_bool)
    
    # Search through each column in current_play to find a YYYY-MM-DD date value
    season = None
    for column_value in current_play[0]:
        if column_value and isinstance(column_value, str):
            # Check if the value looks like a date in YYYY-MM-DD format
            parts = column_value.split('-')
            if len(parts) == 3 and len(parts[0]) == 4 and parts[0].isdigit():
                # Found a valid date, extract the year
                season = parts[0]
                break
    
    if season is None:
        raise ValueError(f"No valid date found in play data for play_id: {play_id}")
    
    return season


def has_been_downloaded(mode: str, play_id: str, verbose_bool: Optional[bool] = False) -> bool:
    return has_been_done(mode, play_id, "downloaded")


def has_been_analyzed(mode: str, play_id: str, verbose_bool: Optional[bool] = False) -> bool:
    return has_been_done(mode, play_id, "analyzed")


def has_been_skeeted(mode: str, play_id: str, verbose_bool: Optional[bool] = False) -> bool:
    return has_been_done(mode, play_id, "skeeted")


def has_been_done(mode: str, play_id: str, flag: str, verbose_bool: Optional[bool] = False) -> bool:
    flag_status = False

    ## Validate the flag
    valid_flags = ['downloaded', 'analyzed', 'skeeted']
    if flag not in valid_flags:
        raise ValueError(f"Invalid flag '{flag}'. Must be one of: {valid_flags}")

    table_definition = get_table_definition(mode, verbose_bool)
    with SQLiteManager(table_definition['filename']) as db:
        select_data = db.query_data(
            f"SELECT {flag} FROM {table_definition['tablename']} WHERE play_id = ?",
            [play_id]
        )
        if len(select_data) == 1 and select_data[0][0] == 1:
            flag_status = True

    return flag_status


def set_download_flag(mode: str, play_id: str, verbose_bool: Optional[bool] = False) -> bool:
    return set_hbp_flag(mode, play_id, 'downloaded', verbose_bool)


def set_analyzed_flag(mode: str, play_id: str, verbose_bool: Optional[bool] = False) -> bool:
    return set_hbp_flag(mode, play_id, 'analyzed', verbose_bool)


def set_skeeted_flag(mode: str, play_id: str, verbose_bool: Optional[bool] = False) -> bool:
    return set_hbp_flag(mode, play_id, 'skeeted', verbose_bool)


def set_hbp_flag(mode: str, play_id: str, flag: str, verbose_bool: Optional[bool] = False) -> bool:
    flags       = ['downloaded', 'analyzed', 'skeeted']
    flag_status = False

    if flag not in flags:
        return flag_status

    table_definition = get_table_definition(mode, verbose_bool)
    with SQLiteManager(table_definition['filename']) as db:
        update_data = db.update_data(
            f"UPDATE {table_definition['tablename']} SET {flag} = 1 WHERE play_id = ?",
            [play_id]
        )
        if update_data == 0:
            raise Exception(f"Play ID {play_id} doesn't exist in the {table_definition['filename']} database!")
        elif update_data == 1:
            flag_status = True
        else:
            raise Exception(f"More than one entry in {table_definition['tablename']} was updated! THIS SHOULDN'T HAPPEN.")
    return flag_status


## -------------------------------------------------------------------------- ##
## DATABASE MAINTENANCE FUNCTIONS
## -------------------------------------------------------------------------- ##


def get_table_definition(mode: str, verbose_bool: Optional[bool] = False) -> dict:
    # Validate the mode parameter
    valid_modes = ["cursed", "hbp", "triples"]
    if mode not in valid_modes:
        raise ValueError(f"Invalid mode '{mode}'. Must be one of: {valid_modes}")

    # Select the appropriate table definition based on mode
    if mode == "cursed":
        table_definition = const.CURSED_TABLE
    elif mode == "hbp":
        table_definition = const.HBP_TABLE
    elif mode == "triples":
        table_definition = const.TRIPLES_TABLE
    else:
        # This should never be reached due to the validation above
        table_definition = None

    if table_definition is None:
        raise ValueError(f"No table definition found for mode: {mode}")

    return table_definition


def create_database(mode: str, verbose_bool: Optional[bool] = False) -> bool:
    """
    Create a database table based on the specified mode.

    This function ensures that:
    1. The database directory exists (creates it if necessary)
    2. The database file exists (creates an empty file if necessary)
    3. The appropriate table is created in the database

    Args:
        mode (str): The type of database to create. Must be one of: "cursed", "hbp", or "triples".
        verbose_bool (Optional[bool]): Whether to print verbose output. Defaults to False.

    Returns:
        bool: True if database creation was successful, False otherwise.

    Raises:
        ValueError: If an invalid mode is provided.

    Example:
        >>> create_database("cursed", verbose_bool=True)
        Creating database table for mode: cursed
        Database file: bsky_data/cursed/cursed.db
        Creating new database file: bsky_data/cursed/cursed.db
        ✅ Successfully created cursed database table
        True
    """
    db_was_created = False

    # Generate SQL CREATE TABLE statement from the dictionary
    table_definition = get_table_definition(mode, verbose_bool)
    filename         = table_definition["filename"]
    tablename        = table_definition["tablename"]
    columns          = table_definition["columns"]

    # Build the column definitions
    column_definitions = []
    for column_name, column_def in columns.items():
        column_definitions.append(f"{column_name} {column_def}")

    # Create the full SQL statement
    create_statement = f"CREATE TABLE IF NOT EXISTS {tablename} (\n    " + ",\n    ".join(column_definitions) + "\n)"

    if verbose_bool:
        print(f"Creating database table for mode: {mode}")
        print(f"Database file: {filename}")
        print(f"Table name: {tablename}")
        print(f"Using SQL statement: {create_statement[:100]}...")  # Show first 100 chars

    # Create SQLiteManager instance and create the table
    try:
        with SQLiteManager(filename) as db_manager:
            db_manager.create_table(create_statement)
            db_was_created = True

        if verbose_bool:
            print(f"✅ Successfully created {mode} database table")

    except Exception as e:
        print(f"❌ Error creating database: {e}")
        db_was_created = False

    return db_was_created


def insert_row(mode: str, game: list, event: list, verbose_bool: Optional[bool] = False) -> bool:
    row_inserted = False
    table_definition = get_table_definition(mode, verbose_bool)

    select_data = get_event_play_data(mode, event['play_id'], verbose_bool)
    if len(select_data) == 0:
        if mode == "cursed":
            insert_data = {
                "play_id"   : event['play_id'],
                "game_pk"   : game['game_pk'],
                "game_date" : game['date'],
                "pitcher_id": event['pitcher']['id'],
                "batter_id" : event['batter']['id'],
                "event"     : "cursed",
            }
        elif mode == "hbp":
            insert_data = {
                "play_id"   : event['play_id'],
                "game_pk"   : game['game_pk'],
                "game_date" : game['date'],
                "pitcher_id": event['pitcher']['id'],
                "batter_id" : event['batter']['id'],
                "end_speed" : event['at_bat']['end_speed'],
                "x_pos"     : event['at_bat']['plate_x'],
                "z_pos"     : event['at_bat']['plate_z'],
            }
        elif mode == "triples":
            insert_data = {
                "play_id"   : event['play_id'],
                "game_pk"   : game['game_pk'],
                "game_date" : game['date'],
                "pitcher_id": event['pitcher']['id'],
                "batter_id" : event['batter']['id'],
            }

        with SQLiteManager(table_definition['filename']) as db:
            row_inserted = db.insert_data(table_definition['tablename'], insert_data)

    return row_inserted

def delete_row(mode: str, play_id: str, verbose_bool: Optional[bool] = False) -> bool:
    deleted = False
    table_definition = get_table_definition(mode, verbose_bool)
    with SQLiteManager(table_definition['filename']) as db:
        delete_data = db.update_data(
            f"DELETE FROM {table_definition['tablename']} WHERE play_id = ?",
            [play_id]
        )
        if delete_data == 0 or delete_data == 1:
            deleted = True
        else:
            raise Exception("More than one entry was deleted! THIS SHOULDN'T HAPPEN.")
    return deleted

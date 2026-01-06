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

# def get_all_batter_data(player_id: int, dbfile: str = db_file_path, dbtable: str = db_table) -> list:
#     return get_all_player_data(player_id, "batter", dbfile, dbtable)


# def get_all_pitcher_data(player_id: int, dbfile: str = db_file_path, dbtable: str = db_table) -> list:
#     return get_all_player_data(player_id, "pitcher", dbfile, dbtable)


# def get_all_player_data(
#     player_id: int,
#     player_type: str,
#     dbfile: str = db_file_path,
#     dbtable: str = db_table
# ) -> list:
#     player_data = []

#     player_types = ["batter", "pitcher"]
#     if player_type not in player_types:
#         return player_data

#     with SQLiteManager(dbfile) as db:
#         player_data = db.query_hbpdata(
#             f"SELECT * FROM {dbtable} WHERE {player_type}_id = ?",
#             [player_id]
#         )
#     return player_data


# def get_earliest_date(dbfile: str = db_file_path, dbtable: str = db_table) -> str:
#     select_data = None
#     with SQLiteManager(dbfile) as db:
#         select_data = db.query_hbpdata(
#             f"SELECT MIN(game_date) FROM {dbtable}",
#             []
#         )
#     return select_data[0][0]


def get_event_play_data(mode: str, play_id: str, verbose_bool: Optional[bool] = False) -> list:
    select_data = []
    table_definition = get_table_definition(mode, verbose_bool)

    with SQLiteManager(table_definition['filename']) as db:
        select_data = db.query_hbpdata(
            f"SELECT * FROM {table_definition['tablename']} WHERE play_id = ?",
            [play_id]
        )
    return select_data


# def get_latest_date_that_hasnt_been_downloaded() -> str:
#     select_data = None
#     with SQLiteManager(db_file_path) as db:
#         select_data = db.query_hbpdata(
#             f"SELECT MAX(game_date) FROM {db_table} WHERE downloaded = 0",
#             []
#         )
#     return select_data[0][0]

# def get_season_data(season: int, dbfile: str = db_file_path, dbtable: str = db_table) -> list:
#     season_data = []
#     season_start = f"{season}-01-01"
#     season_end = f"{season}-12-31"
#     with SQLiteManager(dbfile) as db:
#         season_data = db.query_hbpdata(
#             f"SELECT * FROM {dbtable} WHERE game_date BETWEEN ? AND ?",
#             [season_start, season_end]
#         )
#     return season_data


# def get_season_year(play_id: str, dbfile: str = db_file_path, dbtable: str = db_table) -> bool:
#     current_play = get_event_play_data(play_id, db_file_path, db_table)
#     game_date        = current_play[0][2]
#     season,month,day = game_date.split('-')
#     return season


# def has_been_downloaded(play_id: str, dbfile: str = db_file_path, dbtable: str = db_table) -> bool:
#     return has_been_done(play_id, "downloaded", dbfile, dbtable)


# def has_been_analyzed(play_id: str, dbfile: str = db_file_path, dbtable: str = db_table) -> bool:
#     return has_been_done(play_id, "analyzed", dbfile, dbtable)


# def has_been_skeeted(play_id: str, dbfile: str = db_file_path, dbtable: str = db_table) -> bool:
#     return has_been_done(play_id, "skeeted", dbfile, dbtable)


# def has_been_done(play_id: str, flag: str, dbfile: str = db_file_path, dbtable: str = db_table) -> bool:
#     flags       = {'downloaded': 8, 'analyzed': 9, 'skeeted': 10}
#     flag_index  = flags.get(flag)
#     flag_status = False

#     if flag_status is not None:
#         with SQLiteManager(dbfile) as db:
#             select_data = db.query_hbpdata(
#                 f"SELECT * FROM {dbtable} WHERE play_id = ?",
#                 [play_id]
#             )
#         if len(select_data) == 1 and select_data[0][flag_index] == 1:
#             flag_status = True
#     return flag_status


# def set_download_flag(play_id: str, dbfile: str = db_file_path, dbtable: str = db_table) -> bool:
#     return set_hbp_flag(play_id, 'downloaded', dbfile, dbtable)


# def set_analyzed_flag(play_id: str, dbfile: str = db_file_path, dbtable: str = db_table) -> bool:
#     return set_hbp_flag(play_id, 'analyzed', dbfile, dbtable)


# def set_skeeted_flag(play_id: str, dbfile: str = db_file_path, dbtable: str = db_table) -> bool:
#     return set_hbp_flag(play_id, 'skeeted', dbfile, dbtable)


# def set_hbp_flag(play_id: str, flag: str, dbfile: str = db_file_path, dbtable: str = db_table) -> bool:
#     flags       = ['downloaded', 'analyzed', 'skeeted']
#     flag_status = False

#     if flag not in flags:
#         return flag_status

#     with SQLiteManager(dbfile) as db:
#         update_data = db.update_hbpdata_data(
#             f"UPDATE {dbtable} SET {flag} = 1 WHERE play_id = ?",
#             [play_id]
#         )
#         if update_data == 0:
#             raise Exception(f"Play ID {play_id} doesn't exist in the database!")
#         elif update_data == 1:
#             flag_status = True
#         else:
#             raise Exception("More than one entry was updated! THIS SHOULDN'T HAPPEN.")
#     return flag_status


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

    # # Validate the mode parameter
    # valid_modes = ["cursed", "hbp", "triples"]
    # if mode not in valid_modes:
    #     raise ValueError(f"Invalid mode '{mode}'. Must be one of: {valid_modes}")

    # # Select the appropriate table definition based on mode
    # if mode == "cursed":
    #     table_definition = const.CURSED_TABLE
    # elif mode == "hbp":
    #     table_definition = const.HBP_TABLE
    # elif mode == "triples":
    #     table_definition = const.TRIPLES_TABLE
    # else:
    #     # This should never be reached due to the validation above
    #     table_definition = None

    # if table_definition is None:
    #     raise ValueError(f"No table definition found for mode: {mode}")

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
        print(f"Table name: {tablename}")
        print(f"Using SQL statement: {create_statement[:100]}...")  # Show first 100 chars

    try:
        # Get the database configuration from config based on mode
        bsky_root   = config.get("paths", "bsky_data_dir")
        db_filename = config.get(mode, "db_filename")
        data_root   = config.get(mode, "data_root")

        # Construct the full database file path
        db_file = os.path.join(bsky_root, data_root, db_filename)

        if verbose_bool:
            print(f"Database file: {db_file}")

        # Create SQLiteManager instance and create the table
        with SQLiteManager(db_file) as db_manager:
            db_manager.create_table(create_statement)
            db_was_created = True

        if verbose_bool:
            print(f"✅ Successfully created {mode} database table")

    except Exception as e:
        print(f"❌ Error creating database: {e}")
        db_was_created = False

    return db_was_created


def insert_row(mode: str, game: list, event: list, verbose_bool: Optional[bool] = False) -> bool:
    inserted = False
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
            row_inserted = True

    return inserted

def delete_row(mode: str, play_id: str, verbose_bool: Optional[bool] = False) -> bool:
    deleted = False
    table_definition = get_table_definition(mode, verbose_bool)
    with SQLiteManager(table_definition['filename']) as db:
        delete_data = db.update_hbpdata_data(
            f"DELETE FROM {table_definition['tablename']} WHERE play_id = ?",
            [play_id]
        )
        if delete_data == 0 or delete_data == 1:
            deleted = True
        else:
            raise Exception("More than one entry was deleted! THIS SHOULDN'T HAPPEN.")
    return deleted

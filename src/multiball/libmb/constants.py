#!/usr/bin/env python3

import os
from . import basic
from .configurator import ConfigReader

DEFAULT_CONFIG_DIRECTORY = "config"
DEFAULT_CONFIG_INI_FILE  = os.path.join(DEFAULT_CONFIG_DIRECTORY, "settings.ini")

config = ConfigReader(basic.verify_file_path(basic.sanitize_path(DEFAULT_CONFIG_INI_FILE)))


## ---------------------------------------------------------------------------->
## Skeet constants
## ---------------------------------------------------------------------------->
SKEETS_CHAR_LIMIT = 300
SKEETS_VIDEO_LIMIT = 50000000  ## bytes


## ---------------------------------------------------------------------------->
## MLB Stats URL values
## ---------------------------------------------------------------------------->
BASEBALL_SAVANT_PLAY_VIDEO_URL = 'https://baseballsavant.mlb.com/sporty-videos'
MLB_STATS_BASE_URL             = 'https://statsapi.mlb.com'
MLB_STATS_SCHEDULE_STUB        = '/api/v1/schedule'
MLB_STATS_GAME_STUB            = '/api/v1/game/<<GAME_PK>>/content'
MLB_STATS_LIVE_FEED_STUB       = '/api/v1.1/game/<<GAME_PK>>/feed/live'
MLB_STATS_PLAYER_STUB          = '/api/v1/people/<<PLAYER_ID>>'
MLB_STATS_TEAM_STUB            = '/api/v1/teams/<<TEAM_ID>>'


## ---------------------------------------------------------------------------->
## Events to catch
## ---------------------------------------------------------------------------->
DERP_EVENTS = [
    "Balk",
    "Batter Interference",
    "Catcher Interference",
    # "Caught Stealing 2B",
    # "Caught Stealing 3B",
    # "Caught Stealing Home",
    "Field Error",
]
HBP_EVENTS = ["Hit By Pitch"]
TRIPLES_EVENTS = ["Triple", "Triple Play"]

## ---------------------------------------------------------------------------->
## Database Creation Statements
## ---------------------------------------------------------------------------->

DERP_TABLE = {
    "filename": os.path.join(
        config.get("paths", "bsky_data_dir"),
        config.get("derp", "data_root"),
        config.get("derp", "db_filename")
    ),
    "tablename": config.get("derp", "db_tablename"),
    "columns": {
        "play_id"    : "TEXT PRIMARY KEY",
        "game_pk"    : "INTEGER NOT NULL",
        "game_date"  : "DATE NOT NULL",
        "pitcher_id" : "INTEGER NOT NULL",
        "batter_id"  : "INTEGER NOT NULL",
        "event"      : "TEXT",
        "description": "TEXT",
        "downloaded" : "INTEGER NOT NULL DEFAULT 0",
        "analyzed"   : "INTEGER NOT NULL DEFAULT 0",
        "skeeted"    : "INTEGER NOT NULL DEFAULT 0",
    }
}

HBP_TABLE = {
    "filename": os.path.join(
        config.get("paths", "bsky_data_dir"),
        config.get("hbp", "data_root"),
        config.get("hbp", "db_filename")
    ),
    "tablename": config.get("hbp", "db_tablename"),
    "columns": {
        "play_id"   : "TEXT PRIMARY KEY",
        "game_pk"   : "INTEGER NOT NULL",
        "game_date" : "DATE NOT NULL",
        "pitcher_id": "INTEGER NOT NULL",
        "batter_id" : "INTEGER NOT NULL",
        "end_speed" : "REAL",
        "x_pos"     : "REAL",
        "z_pos"     : "REAL",
        "downloaded": "INTEGER NOT NULL DEFAULT 0",
        "analyzed"  : "INTEGER NOT NULL DEFAULT 0",
        "skeeted"   : "INTEGER NOT NULL DEFAULT 0",
    }
}

TRIPLES_TABLE = {
    "filename": os.path.join(
        config.get("paths", "bsky_data_dir"),
        config.get("triples", "data_root"),
        config.get("triples", "db_filename")
    ),
    "tablename": config.get("triples", "db_tablename"),
    "columns": {
        "play_id"   : "TEXT PRIMARY KEY",
        "game_pk"   : "INTEGER NOT NULL",
        "game_date" : "DATE NOT NULL",
        "pitcher_id": "INTEGER NOT NULL",
        "batter_id" : "INTEGER NOT NULL",
        "downloaded": "INTEGER NOT NULL DEFAULT 0",
        "analyzed"  : "INTEGER NOT NULL DEFAULT 0",
        "skeeted"   : "INTEGER NOT NULL DEFAULT 0",
    }
}


## ---------------------------------------------------------------------------->
## Filesystem Paths
## ---------------------------------------------------------------------------->

DERP_PATHS = {
    'root': os.path.join(
        config.get("paths", "bsky_data_dir"),
        config.get("derp", "data_root"),
    ),
    'database_fullpath': os.path.join(
        config.get("paths", "bsky_data_dir"),
        config.get("derp", "data_root"),
        config.get("derp", "db_filename")
    ),
    'plot_dir_fullpath': os.path.join(
        config.get("paths", "bsky_data_dir"),
        config.get("derp", "data_root"),
        config.get("paths", "plot_dir")
    ),
    'skeet_dir_fullpath': os.path.join(
        config.get("paths", "bsky_data_dir"),
        config.get("derp", "data_root"),
        config.get("paths", "skeet_dir")
    ),
    'video_dir_fullpath': os.path.join(
        config.get("paths", "bsky_data_dir"),
        config.get("derp", "data_root"),
        config.get("paths", "video_dir")
    ),
    'username_fullpath': os.path.join(
        config.get("paths", "bsky_data_dir"),
        config.get("derp", "data_root"),
        config.get("derp", "bsky_user_file")
    ),
    'password_fullpath': os.path.join(
        config.get("paths", "bsky_data_dir"),
        config.get("derp", "data_root"),
        config.get("derp", "bsky_pwd_file")
    ),
}

HBP_PATHS = {
    'root': os.path.join(
        config.get("paths", "bsky_data_dir"),
        config.get("hbp", "data_root"),
    ),
    'database_fullpath': os.path.join(
        config.get("paths", "bsky_data_dir"),
        config.get("hbp", "data_root"),
        config.get("hbp", "db_filename")
    ),
    'plot_dir_fullpath': os.path.join(
        config.get("paths", "bsky_data_dir"),
        config.get("hbp", "data_root"),
        config.get("paths", "plot_dir")
    ),
    'skeet_dir_fullpath': os.path.join(
        config.get("paths", "bsky_data_dir"),
        config.get("hbp", "data_root"),
        config.get("paths", "skeet_dir")
    ),
    'video_dir_fullpath': os.path.join(
        config.get("paths", "bsky_data_dir"),
        config.get("hbp", "data_root"),
        config.get("paths", "video_dir")
    ),
    'username_fullpath': os.path.join(
        config.get("paths", "bsky_data_dir"),
        config.get("hbp", "data_root"),
        config.get("hbp", "bsky_user_file")
    ),
    'password_fullpath': os.path.join(
        config.get("paths", "bsky_data_dir"),
        config.get("hbp", "data_root"),
        config.get("hbp", "bsky_pwd_file")
    ),
}

TRIPLES_PATHS = {
    'root': os.path.join(
        config.get("paths", "bsky_data_dir"),
        config.get("triples", "data_root"),
    ),
    'database_fullpath': os.path.join(
        config.get("paths", "bsky_data_dir"),
        config.get("triples", "data_root"),
        config.get("triples", "db_filename")
    ),
    'plot_dir_fullpath': os.path.join(
        config.get("paths", "bsky_data_dir"),
        config.get("triples", "data_root"),
        config.get("paths", "plot_dir")
    ),
    'skeet_dir_fullpath': os.path.join(
        config.get("paths", "bsky_data_dir"),
        config.get("triples", "data_root"),
        config.get("paths", "skeet_dir")
    ),
    'video_dir_fullpath': os.path.join(
        config.get("paths", "bsky_data_dir"),
        config.get("triples", "data_root"),
        config.get("paths", "video_dir")
    ),
    'username_fullpath': os.path.join(
        config.get("paths", "bsky_data_dir"),
        config.get("triples", "data_root"),
        config.get("triples", "bsky_user_file")
    ),
    'password_fullpath': os.path.join(
        config.get("paths", "bsky_data_dir"),
        config.get("triples", "data_root"),
        config.get("triples", "bsky_pwd_file")
    ),
}


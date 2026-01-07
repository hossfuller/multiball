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

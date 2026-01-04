#!/usr/bin/env python3

import os

DEFAULT_CONFIG_DIRECTORY = "config"
DEFAULT_CONFIG_INI_FILE  = os.path.join(DEFAULT_CONFIG_DIRECTORY, "settings.ini")

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
hbp_table = """
    CREATE TABLE IF NOT EXISTS hbpdata (
        play_id TEXT PRIMARY KEY,
        game_pk INTEGER NOT NULL,
        game_date DATE NOT NULL,
        pitcher_id INTEGER NOT NULL,
        batter_id INTEGER NOT NULL,
        end_speed REAL,
        x_pos REAL,
        z_pos REAL,
        downloaded INTEGER NOT NULL DEFAULT 0,
        analyzed INTEGER NOT NULL DEFAULT 0,
        skeeted INTEGER NOT NULL DEFAULT 0
    )
"""
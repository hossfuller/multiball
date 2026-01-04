#!/usr/bin/env python3

# Package metadata
__version__ = "1.0.0"
__author__ = "Hossein Fuller <hossfuller@protonmail.com>"
__description__ = "Multiball Bsky Client - Bluesky bot that posts cursed baseball plays, hit by pitches, and triples to different bsky accounts."

# Import key components to make them available at package level
from .libmb import basic
from .libmb import configurator
from .libmb import constants
from .libmb import dbconnector
from .libmb import logger
from .libmb import sqlitemgr
# from .libmb import func_general
# from .libmb import func_baseball
# from .libmb import func_skeet

# Package-level variables
__all__ = [
    'basic',
    'configurator',
    'constants',
    'dbconnector',
    'logger',
    'sqlitemgr',
    # 'func_general',
    # 'func_baseball',
    # 'func_skeet',
]

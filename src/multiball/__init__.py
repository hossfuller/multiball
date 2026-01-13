#!/usr/bin/env python3

# Package metadata
__version__ = "1.0.0"
__author__ = "Hossein Fuller <hossfuller@protonmail.com>"
__description__ = "Multiball Bsky Client - Bluesky bot that posts derpy baseball plays, hit by pitches, and triples to one or multiple bluesky accounts."

# Import key components to make them available at package level
from .libmb import basic
from .libmb import cmdparser
from .libmb import configurator
from .libmb import constants
from .libmb import dbconnector
from .libmb import func_baseball
from .libmb import func_database
from .libmb import func_plot
from .libmb import func_skeet
from .libmb import logger
from .libmb import sqlitemgr

# Package-level variables
__all__ = [
    "basic",
    "cmdparser",
    "configurator",
    "constants",
    "dbconnector",
    "func_baseball",
    "func_database",
    "func_plot",
    "func_skeet",
    "logger",
    "sqlitemgr",
]

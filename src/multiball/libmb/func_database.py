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
## DATABASE FUNCTIONS
## -------------------------------------------------------------------------- ##

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

    # Validate the mode parameter
    valid_modes = ["cursed", "hbp", "triples"]
    if mode not in valid_modes:
        raise ValueError(f"Invalid mode '{mode}'. Must be one of: {valid_modes}")

    # Select the appropriate table creation SQL based on mode
    if mode == "cursed":
        create_statement = const.CURSED_TABLE
    elif mode == "hbp":
        create_statement = const.HBP_TABLE
    elif mode == "triples":
        create_statement = const.TRIPLES_TABLE
    else:
        # This should never be reached due to the validation above
        create_statement = ""

    if verbose_bool:
        print(f"Creating database table for mode: {mode}")
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

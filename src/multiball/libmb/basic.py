import argparse
import os
import pathlib
import platform

from datetime import datetime, date, timedelta
from typing import Optional


## -------------------------------------------------------------------------- ##
## CONSTANTS
## -------------------------------------------------------------------------- ##

SYSTEM_NAME = platform.system()

## -------------------------------------------------------------------------- ##
## DATE FUNCTIONS
## -------------------------------------------------------------------------- ##

def parse_date_string(date_string):
    try:
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    except ValueError:
        msg = f"Not a valid date format: '{date_string}'. Expected format: YYYY-MM-DD."
        raise argparse.ArgumentTypeError(msg)


def add_one_day_to_date(date_str: Optional[str] = None):
    return transcend_time_and_space("forward", date_str)


def subtract_one_day_from_date(date_str: Optional[str] = None):
    return transcend_time_and_space("backward", date_str)


def transcend_time_and_space(direction: str, date_str: Optional[str] = None):
    return_date = None
    if date_str is None:
        if direction == "forward":
            return_date = date.today() + timedelta(days=1)
        else:
            return_date = date.today() - timedelta(days=1)
    else:
        if direction == "forward":
            new_date = datetime.strptime(str(date_str), "%Y-%m-%d").date() + timedelta(days=1)
        else:
            new_date = datetime.strptime(str(date_str), "%Y-%m-%d").date() - timedelta(days=1)
        return_date =  new_date.strftime("%Y-%m-%d")
    return return_date


## -------------------------------------------------------------------------- ##
## FILE PATHS AND SUCH
## -------------------------------------------------------------------------- ##

def sanitize_path(path_string, return_path_obj=False):
    """
    Takes a directory path string and converts it into an OS-appropriate path.

    Args:
        path_string (str): The directory path we want to sanitize.
        return_path_obj (bool): Whether or not we should return the path obj.

    Returns:
        str: The OS-sanitized directory path.
        obj: The OS-dependent Path object.
    """
    if SYSTEM_NAME == "Windows":
        # path_obj = pathlib.PureWindowsPath(path_string)
        path_obj = pathlib.WindowsPath(path_string)
        path_str = str(path_obj)
    else:
        path_obj = pathlib.Path(path_string)
        path_str = str(path_obj)

    if return_path_obj:
        return path_obj
    else:
        return path_str


def verify_directory_path(path_string):
    """
    Determine whether or not a directory exists. Attempts to smoothly handle the
    difference between Windows and Linux paths.

    Args:
        path_string (str): The directory path we want to check.

    Returns:
        str: The OS-sanitized directory path.
    """
    path_str = sanitize_path(path_string)
    if not os.path.isdir(path_str):
        raise TypeError(f"'{path_str}' is not an existing directory.")
    return path_str


def verify_file_path(filepath):
    """
    Checks if a file exists and is a regular file.
    """
    if not os.path.exists(filepath):
        raise TypeError(f"Error: File '{filepath}' not found.")
    elif not os.path.isfile(filepath):
        raise TypeError(f"Error: '{filepath}' is not a regular file.")
    return filepath

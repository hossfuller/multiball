#!/usr/bin/env python3
"""
Command Line Argument Parser Wrapper

This module provides a CmdParser class that wraps the argparse library,
allowing for easy configuration through a dictionary of argument options.
"""

import argparse
import sys
from typing import Dict, Any, List, Optional, Union


class CmdParser:
    """
    A wrapper class for argparse that simplifies command line argument parsing.

    This class takes a dictionary of argument configurations and automatically
    adds them to an argparse.ArgumentParser instance. It also provides two
    default arguments: --test-mode and --verbose.

    Attributes:
        parser (argparse.ArgumentParser): The underlying argparse parser instance
        args (argparse.Namespace): The parsed arguments as a Namespace object
        parsed_dict (Dict[str, Any]): The parsed arguments as a dictionary
    """

    def __init__(self, description: str = "Command Line Argument Parser"):
        """
        Initialize the CmdParser with a description.

        Args:
            description (str): Description for the argument parser
        """
        self.parser = argparse.ArgumentParser(description=description)
        self.args = None
        self.parsed_dict = {}

        # Add default arguments
        self._add_default_arguments()

    def _add_default_arguments(self) -> None:
        """
        Add the default command line arguments:
            --nolog (-n)
            --test-mode (-t)
            --verbose (-v)
            --double-verbose (-vv)
        """
        # Add --nolog argument with short form -n
        self.parser.add_argument(
            "-n", "--nolog",
            action="store_true",
            help="Disable logging"
        )

        # Add --test-mode argument with short form -t
        self.parser.add_argument(
            "-t", "--test-mode",
            action="store_true",
            help="Enable test mode for debugging and testing purposes"
        )

        # Add --verbose argument with short form -v
        self.parser.add_argument(
            "-v", "--verbose",
            action="store_true",
            help="Enable verbose output for detailed logging"
        )

        # Add --double-verbose argument with short form -vv
        self.parser.add_argument(
            "-vv", "--double-verbose",
            action="store_true",
            help="Enable *really* verbose output for *really* detailed logging"
        )

    def add_arguments_from_dict(self, arg_configs: Dict[Union[str, tuple], Dict[str, Any]]) -> None:
        """
        Add arguments to the parser from a dictionary configuration.

        Args:
            arg_configs (Dict[Union[str, tuple], Dict[str, Any]]): Dictionary where keys are
                argument names/flags and values are dictionaries of kwargs to pass
                to add_argument(). Keys can be:
                - Single argument string: "--input-file"
                - Tuple with short and long forms: ("-i", "--input-file")

                Supported kwargs include all argparse.add_argument() parameters:
                - type: str, int, float, bool, etc.
                - default: default value
                - required: True/False
                - help: help text
                - choices: list of acceptable values (for input restriction)
                - action: "store", "store_true", "store_false", etc.
                - And any other argparse parameter

        Example:
            {
                "--input-file": {
                    "type": str,
                    "required": True,
                    "help": "Path to input file"
                },
                ("-o", "--output-dir"): {
                    "type": str,
                    "default": "./output",
                    "help": "Output directory path"
                },
                "--max-items": {
                    "type": int,
                    "default": 100,
                    "help": "Maximum number of items to process"
                },
                "--log-level": {
                    "type": str,
                    "choices": ["debug", "info", "warning", "error"],
                    "default": "info",
                    "help": "Logging level (debug, info, warning, error)"
                }
            }
        """
        for arg_name, kwargs in arg_configs.items():
            if isinstance(arg_name, tuple):
                # Handle tuple format: ("-s", "--long-arg")
                self.parser.add_argument(*arg_name, **kwargs)
            else:
                # Handle single string format: "--long-arg"
                self.parser.add_argument(arg_name, **kwargs)

    def parse_args(self, args_list: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Parse command line arguments and return them as a dictionary.

        Args:
            args_list (Optional[List[str]]): List of arguments to parse.
                If None, uses sys.argv[1:]

        Returns:
            Dict[str, Any]: Dictionary of parsed argument values
        """
        try:
            if args_list is None:
                self.args = self.parser.parse_args()
            else:
                self.args = self.parser.parse_args(args_list)

            # Convert Namespace to dictionary
            self.parsed_dict = vars(self.args)
            return self.parsed_dict

        except argparse.ArgumentError as e:
            print(f"Argument error: {e}", file=sys.stderr)
            self.parser.print_help()
            sys.exit(1)
        except Exception as e:
            print(f"Error parsing arguments: {e}", file=sys.stderr)
            self.parser.print_help()
            sys.exit(1)

    def get_parsed_dict(self) -> Dict[str, Any]:
        """
        Get the parsed arguments as a dictionary.

        Returns:
            Dict[str, Any]: Dictionary of parsed argument values
        """
        return self.parsed_dict

    def get_argument(self, arg_name: str) -> Any:
        """
        Get the value of a specific argument.

        Args:
            arg_name (str): Name of the argument (with hyphens, e.g., "--input-file")

        Returns:
            Any: Value of the argument, or None if not found
        """
        # Convert argument name from hyphen format to underscore format
        # argparse converts --arg-name to arg_name internally
        if arg_name.startswith("--"):
            underscore_name = arg_name[2:].replace("-", "_")
        elif arg_name.startswith("-"):
            underscore_name = arg_name[1:].replace("-", "_")
        else:
            underscore_name = arg_name.replace("-", "_")

        return self.parsed_dict.get(underscore_name)

    def print_help(self) -> None:
        """
        Print the help message for the argument parser.
        """
        self.parser.print_help()

    def __str__(self) -> str:
        """
        String representation of the parsed arguments.
        """
        return str(self.parsed_dict)

    def __repr__(self) -> str:
        """
        Detailed representation of the CmdParser instance.
        """
        return f"CmdParser(parsed_args={self.parsed_dict})"


# Example usage and testing
if __name__ == "__main__":
    # Example configuration dictionary demonstrating all supported formats
    example_config = {
        # Single long argument format (original)
        "--input-file": {
            "type": str,
            "required": True,
            "help": "Path to input file"
        },

        # Tuple format with short and long arguments (new feature)
        ("-o", "--output-dir"): {
            "type": str,
            "default": "./output",
            "help": "Output directory path"
        },

        ("-m", "--max-items"): {
            "type": int,
            "default": 100,
            "help": "Maximum number of items to process"
        },

        # Boolean flag with tuple format
        ("-d", "--debug"): {
            "action": "store_true",
            "help": "Enable debug mode"
        },

        # Argument with restricted choices (input validation)
        ("-l", "--log-level"): {
            "type": str,
            "choices": ["debug", "info", "warning", "error"],
            "default": "info",
            "help": "Logging level: debug, info, warning, or error"
        }
    }

    # Create parser and add arguments
    parser = CmdParser(description="Example Command Line Parser with Short Arguments")
    parser.add_arguments_from_dict(example_config)

    # Parse arguments - demonstrates various ways to call the script:
    # python script.py --input-file data.txt --output-dir ./results --max-items 50 --debug --test-mode --verbose
    # python script.py --input-file data.txt -o ./results -m 50 -d -t -v
    # python script.py --input-file data.txt -o ./results --max-items 75 -d -t -v
    # python script.py --input-file data.txt -l warning  # Using choices argument
    parsed_args = parser.parse_args()

    print("Parsed Arguments:")
    for key, value in parsed_args.items():
        print(f"  {key}: {value}")

    # Demonstrate accessing specific arguments using both long and short forms
    print(f"\nDefault arguments:")
    print(f"  Test mode enabled (-t/--test-mode): {parser.get_argument('--test-mode')}")
    print(f"  Verbose mode enabled (-v/--verbose): {parser.get_argument('--verbose')}")

    print(f"\nCustom arguments:")
    print(f"  Input file (--input-file): {parser.get_argument('--input-file')}")
    print(f"  Output dir (-o/--output-dir): {parser.get_argument('--output-dir')}")
    print(f"  Max items (-m/--max-items): {parser.get_argument('--max-items')}")
    print(f"  Debug mode (-d/--debug): {parser.get_argument('--debug')}")
    print(f"  Log level (-l/--log-level): {parser.get_argument('--log-level')}")

    # Demonstrate accessing the full parsed dictionary
    print(f"\nFull parsed dictionary:")
    print(f"  {parser.get_parsed_dict()}")

    # Show how to use the arguments in a real script
    print(f"\nExample usage in script:")
    if parsed_args.get('test_mode'):
        print("  🧪 Running in test mode")
    if parsed_args.get('verbose'):
        print("  📢 Verbose logging enabled")
    if parsed_args.get('debug'):
        print("  🐛 Debug mode active")

    print(f"  📁 Processing {parsed_args.get('input_file', 'no file')}")
    print(f"  📂 Output to {parsed_args.get('output_dir', 'default directory')}")
    print(f"  📊 Max items: {parsed_args.get('max_items', 0)}")

# multiball

Bluesky bot that posts derpie baseball plays, hit by pitches, and triples to different bsky accounts.


<!-- --------------------------------------------------------------------------- -->


<div id='setting_up_the_virtual_environment' />

## Setting up the virtual environment

From start to finish, here's what to do for the different platforms after cloning this repository.


<div id='setup_summary_linux' />

#### Linux

If Debian/Ubuntu:

```sh
sudo apt-get install python3.13 python3.13-venv python3-pip
```

If RHELx:

```sh
sudo apt-get install python3 python3-venv python3-pip
```

Then, for both:

```sh
python3.13 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install pipreqs black mypy
python -m  pipreqs.pipreqs . --force --ignore ".venv"
pip install -r requirements.txt
```


<div id='setup_summary_windows' />

#### Windows 11

How do you install python on Windows 11?

```sh
python -m venv env
.\env\bin\Activate.ps1  ## or .\env\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install pipreqs black mypy
python -m  pipreqs.pipreqs . --force --ignore "env"
pip install -r requirements.txt
```

**NOTE:** See that `"env"` on the `--ignore` flag? That may not be necessary for Windows, but if there's a `UnicodeDecodeError` error when running `pipreqs`, you'll need to add that flag to avoid the error.


<!-- --------------------------------------------------------------------------- -->


<div id='set_up_bluesky_credentials' />

## Set up Bluesky credentials

The `config/settings.ini` file has a section where you specify the Bluesky account credentials. For the password, create a file called `config/credentials.txt` or some such name with just the bsky account password, set the proper info in the `settings.ini` file, and let 'er rip.


<!-- --------------------------------------------------------------------------- -->


## TO-DO

- [x] Figure out how to do derp plays for db population (`get_mlb_events_from_single_game()`)
- [x] Figure out how to do triples plays for db population (`get_mlb_events_from_single_game()`)


<!-- --------------------------------------------------------------------------- -->


<div id='inspirations' />

## Inspirations

- [coperyan/mlb-videos](https://github.com/coperyan/mlb-videos)
- [dylandru/BSav_Scraper_Vid](https://github.com/dylandru/BSav_Scraper_Vid)
- [Smerity/all_examples_from_bluesky_atproto_python_api.py.txt](https://gist.github.com/Smerity/f896e0a9d27c725b2bc03cd85e105b31)



<!-- --------------------------------------------------------------------------- -->


<div id='run_multiball_script_usage_examples' />

## `run_multiball` Script Usage Examples

The `run_multiball.sh` and `run_multiball.bat` scripts have been updated to use specific flags for each module.

### Basic Usage

#### Shell Script (Linux/macOS)

```bash
# Default behavior (dbpop)
./run_multiball.sh --help
./run_multiball.sh --test-mode --verbose

# Explicit module selection
./run_multiball.sh --db --help
./run_multiball.sh --dl --input-file data.csv
./run_multiball.sh --pl --output-dir ./plots
./run_multiball.sh --sk --message "Hello World"
```

#### Batch Script (Windows)

```batch
:: Default behavior (dbpop)
run_multiball.bat --help
run_multiball.bat --test-mode --verbose

:: Explicit module selection
run_multiball.bat --db --help
run_multiball.bat --dl --input-file data.csv
run_multiball.bat --pl --output-dir ./plots
run_multiball.bat --sk --message "Hello World"
```

### Available Flags

- `--db` - Database population module (default if no flag specified)
- `--dl` - Data downloader module
- `--pl` - Plotting/visualization module
- `--sk` - Social media posting module

### Argument Passing

All arguments after the module flag are passed directly to the selected module. For example:

```bash
# These are equivalent:
./run_multiball.sh --dl --input-file data.csv --output-dir ./output --verbose
python3 -m src.multiball.downloader --input-file data.csv --output-dir ./output --verbose
```

### Help System

```bash
# Show script help
./run_multiball.sh --help

# Show help for a specific module
./run_multiball.sh --dl --help
./run_multiball.sh --pl --help
```

### Examples with Common Arguments

```bash
# Database operations (default, so --db is optional)
./run_multiball.sh --test-mode --verbose --dry-run
./run_multiball.sh --db --test-mode --verbose --dry-run

# Downloader with file specifications
./run_multiball.sh --dl --input-file input.csv --output-file output.json --max-items 100

# Plotter with custom settings
./run_multiball.sh --pl --input-data data.json --output-dir ./plots --plot-style fancy

# Skeeter with message
./run_multiball.sh --sk --message "Check out this new plot!" --image-file plot.png
```

### Notes

- The scripts automatically set the `PYTHONPATH` to include the current directory
- Both scripts support the same functionality and argument parsing
- The default module is `dbpop` if no flag is provided
- All module-specific arguments are passed through unchanged
- Use `--help` to see script usage information
- Use `--<module> --help` to see module-specific help

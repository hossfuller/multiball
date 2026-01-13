# Multiball

Bluesky bot written in python that posts derpie baseball plays, hit by pitches, and triples to different bsky accounts.


<!-- --------------------------------------------------------------------------- -->


<div id='creating_a_virtual_environment' />

## Creating a Virtual Environment

It's recommended to use a virtual environment to isolate the project dependencies.

#### Linux/MacOS

```bash
# Clone the repository
git clone https://github.com/yourusername/multiball.git
cd multiball

# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Windows

```powershell
# Clone the repository
git clone https://github.com/yourusername/multiball.git
cd multiball

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
.\[path]\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```


<!-- --------------------------------------------------------------------------- -->


<div id='configuration' />

## Configuration

This application has three "modes": `derp` (balks, interferences, and errors), `hbp` (hit by pitches), and `triples` (triples and triple plays). The data for all three are stored in their own unique directories inside a root bluesky data directory. This includes each mode's Bluesky username/password, database, skeet text, plot diagrams, and video files. The directories are arranged like this:

```
bsky_data/              # Bluesky data root
├── derp/
│   ├── derpdata.db
│   ├── derp_password.txt
│   ├── derp_username.txt
│   ├── plots/
│   ├── skeets/
│   └── videos/
├── hbp/
│   ├── hbpdata.db
│   ├── hbp_password.txt
│   ├── hbp_username.txt
│   ├── plots/
│   ├── skeets/
│   └── videos/
└── triples
    ├── triplesdata.db
    ├── triples_password.txt
    ├── triples_username.txt
    ├── plots/
    ├── skeets/
    └── videos/
```

Thus, to access the `hbp` mode's database, go to `bsky_data/hbp/hbpdata.db`; to access the derp skeets, go to `bsky_data/derp/skeets`; etc.

The locations of the modes' root directories, database files, and username and password files, update the respective mode's configuration in `config/settings.ini`.

```ini
[hbp]
data_root      = hbp
bsky_user_file = hbp_username.txt
bsky_pwd_file  = hbp_password.txt
db_filename    = hbpdata.db
db_tablename   = hbpdata
```

Note that there's even a setting for the name of the database table. This is an sqlite database. It's configuration is contained in `src/multiball/libmb/constants.py`. For example:

```python
DERP_TABLE = {
    "filename": os.path.join(
        config.get("paths", "bsky_data_dir"),
        config.get("derp", "data_root"),
        config.get("derp", "db_filename"),
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
    },
}
```

You can see straight away that the `constants.py` file has a dependency on the `settings.ini` file. Keep it that way or you'll end up in circular hell.


<!-- --------------------------------------------------------------------------- -->


<div id='project_structure' />

## Project Structure

```
multiball/
├── bsky_data/              # Data downloaded from Bluesky
├── config/                 # Configuration files
├── src/                    # Source code
│   └── multiball/          # Main application package
│       ├── libmb/          # Library modules
│       ├── dbpop.py        # Database population script
│       ├── downloader.py   # Data downloader
│       ├── plotter.py      # Plotting functionality
│       └── skeeter.py      # Bluesky posting functionality
├── requirements.txt        # Python dependencies
├── run_multiball.sh        # Linux/MacOS runner script
└── run_multiball.bat       # Windows runner script
```


<!-- --------------------------------------------------------------------------- -->


<div id='modules' />

## Modules

### dbpop.py

Uses statcast data to fill in a mode's database with targetted plays we want to download/analyze/skeet in the future.

### downloader.py

Uses mode database data and statcast data to build a skeet and download the corresponding video from Baseball Savant. Also updates the appropriate database for the plotter/skeet scripts.

### plotter.py

For certain events, we want to plot certain data action. This script generates plots and visualizations from the database and statcast data. Currently only setup to work on HBP data.

### skeeter.py

Reads the skeet file, finds the video and (if any) plot files, and then throws it all into the Bluesky void.


<!-- --------------------------------------------------------------------------- -->


<div id='run_multiball_script_usage_examples' />

## `run_multiball` Script Usage Examples

On Linux and Macos, use `run_multiball.sh`. On Windows, pray `run_multiball.bat` works.

Update the `hbp` database with events from 10 days in the middle of summer with no logging enabled:

```bash
./run_multiball.sh --db -n --start-date 2025-07-01 --num-days 10 --mode hbp
```

Update the `derp` database with events from the last 20 days of the playoffs:

```bash
./run_multiball.sh --db --start-date 2025-11-01 --num-days 20 --backward --mode derp
```

Build skeets and download videos of triples and triple plays from the last 30 days of the season:

```bash
./run_multiball.sh --dl --start-date 2025-11-01 --num-days 30 --backward --mode triples
```

Assemble HBP plots for all queued-up skeets:

```bash
./run_multiball.sh --pl -n --mode hbp
```

Post 3 derp skeets:

```bash
./run_multiball.sh --sk -n --num-posts 3 --mode hbp
```


<!-- --------------------------------------------------------------------------- -->


<div id='license' />

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


<!-- --------------------------------------------------------------------------- -->


<div id='contributing' />

## Contributing



<!-- --------------------------------------------------------------------------- -->


<div id='inspirations' />

## Inspirations

- [coperyan/mlb-videos](https://github.com/coperyan/mlb-videos)
- [dylandru/BSav_Scraper_Vid](https://github.com/dylandru/BSav_Scraper_Vid)
- [Smerity/all_examples_from_bluesky_atproto_python_api.py.txt](https://gist.github.com/Smerity/f896e0a9d27c725b2bc03cd85e105b31)


<!-- --------------------------------------------------------------------------- -->


<div id='support' />

## Support

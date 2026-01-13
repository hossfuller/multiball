#!/usr/bin/env python3

## -------------------------------------------------------------------------- ##
## Multiball Skeeter
## Reads the skeet file, finds the video and (if any) plot files, and then
## throws it all into the void.
## -------------------------------------------------------------------------- ##


import os
import pprint
import sys
import time

# Import application modules
from .libmb import basic as bsc
from .libmb import constants as const
from .libmb import func_baseball as bb
from .libmb import func_database as dbmgr
from .libmb import func_skeet as sk

from .libmb.cmdparser import CmdParser
from .libmb.configurator import ConfigReader
from .libmb.logger import PrintLogger

from atproto import Client, exceptions, models
from datetime import datetime
from typing import Optional


## -------------------------------------------------------------------------- ##
## SETUP
## -------------------------------------------------------------------------- ##

## Read and update configuration
config = ConfigReader(
    bsc.verify_file_path(bsc.sanitize_path(const.DEFAULT_CONFIG_INI_FILE))
)

#fmt: off
mode           = "hbp"
num_posts      = int(config.get("client_parameters", "num_posts_per_run"))
test_mode      = bool(int(config.get("operations", "test_mode")))
verbose        = bool(int(config.get("operations", "verbose_output")))
double_verbose = bool(int(config.get("operations", "double_verbose")))
#fmt: on

## Create parser and add arguments
parser = CmdParser(description="Posts skeets, plots, and videos to Bluesky.")
parser.add_arguments_from_dict(
    {
        ("-m", "--mode"): {
            "type": str,
            "required": True,
            "choices": ["derp", "hbp", "triples"],
            "default": mode,
            "help": "Specify which baseball mode to populate",
        },
        ("-p", "--num-posts"): {
            "type": int,
            "default": num_posts,
            "help": "Number of events to post. Defaults to '%(default)s'",
        },
    }
)
args = parser.parse_args()

## Now pull config and command line action together.
if args.get("mode"):
    mode = args.get("mode")
if args.get("num_posts"):
    config.set("client_parameters", "num_posts_per_run", str(args.get("num_posts")))
    num_posts = args.get("num_posts")

if args.get("test_mode"):
    config.set("operations", "test_mode", "1")
    test_mode = True
if args.get("verbose"):
    config.set("operations", "verbose_output", "1")
    verbose = True
if args.get("double_verbose"):
    config.set("operations", "verbose_output", "1")
    config.set("operations", "double_verbose", "1")
    verbose = True
    double_verbose = True

## Set up logging
if not args.get("nolog"):
    prefix_val = config.get("logging_prefixes", "skeeter_prefix")
    sys.stdout = PrintLogger(
        config.get("paths", "log_dir"),
        f"{mode}_{prefix_val}",
    )


## -------------------------------------------------------------------------- ##
## MAIN ACTION
## -------------------------------------------------------------------------- ##


def main(num_posts: Optional[int] = 1) -> int:
    try:
        print()

        if verbose:
            print(config.get_all())
            print()

        print("=" * 80)
        print(
            f" ⚾ {config.get('app', 'name')} ⚾ ~~> 🦋 {mode.capitalize()} Bluesky Skeeter"
        )
        print("=" * 80)
        start_time = time.time()

        ## -----------------------
        ## Directory Setup
        ## -----------------------
        #fmt: off
        plot_dir  = const.HBP_PATHS["plot_dir_fullpath"]
        skeet_dir = const.HBP_PATHS["skeet_dir_fullpath"]
        video_dir = const.HBP_PATHS["video_dir_fullpath"]
        user_file = const.HBP_PATHS["username_fullpath"]
        pwd_file  = const.HBP_PATHS["password_fullpath"]
        if mode == "derp":
            plot_dir  = const.DERP_PATHS["plot_dir_fullpath"]
            skeet_dir = const.DERP_PATHS["skeet_dir_fullpath"]
            video_dir = const.DERP_PATHS["video_dir_fullpath"]
            user_file = const.DERP_PATHS["username_fullpath"]
            pwd_file  = const.DERP_PATHS["password_fullpath"]
        elif mode == "triples":
            plot_dir = const.TRIPLES_PATHS["plot_dir_fullpath"]
            skeet_dir = const.TRIPLES_PATHS["skeet_dir_fullpath"]
            video_dir = const.TRIPLES_PATHS["video_dir_fullpath"]
            user_file = const.TRIPLES_PATHS["username_fullpath"]
            pwd_file = const.TRIPLES_PATHS["password_fullpath"]
        #fmt: on

        ## -----------------------
        ## Bluesky Setup
        ## -----------------------
        bsky_user = None
        bsky_pass = None
        with open(user_file, "r", encoding="utf-8") as f:
            bsky_user = f.read()
        with open(pwd_file, "r", encoding="utf-8") as f:
            bsky_pass = f.read()
        if verbose:
            print(f" {mode.capitalize()} username: >{bsky_user.rstrip()}<")
            print(f" {mode.capitalize()} password: >{bsky_pass.rstrip()}<")
        print(f"🔌 Connecting to bluesky account for {bsky_user.rstrip()}...")
        client = Client()
        try:
            profile = client.login(bsky_user.rstrip(), bsky_pass.rstrip())
        except:
            raise Exception("❌ Unable to connect to Bluesky!!")

        print(f"👍 Connected as '{profile.handle}'.")
        if double_verbose:
            print()
            pprint.pprint(profile)
        print()

        ## -----------------------
        ## Skeet loop
        ## -----------------------
        skeet_dir_files = sorted(os.listdir(skeet_dir))
        if verbose:
            pprint.pprint(skeet_dir_files)
        if len(skeet_dir_files) < num_posts:
            print(
                f"‼️ Number of desired posts ({num_posts}) exceeds number of available skeets. Fixing."
            )
            num_posts = len(skeet_dir_files)
            print(
                f"‼️ Adjusted to {num_posts} posts. This may change during operation...."
            )

        skeet_counter = 0
        for skeet_file in skeet_dir_files:
            full_skeet_filename = os.path.join(skeet_dir, skeet_file)
            skeet_root, ext = os.path.splitext(skeet_file)
            skeet_parts = skeet_root.split("_")

            ## Not a file we want to work with
            if not skeet_parts[0].isdigit():
                print()
                continue

            game_pk = skeet_parts[0]
            play_id = skeet_parts[1]
            print(f"⚾ Game = {game_pk}, Play ID = {play_id}")

            if skeet_parts[1] == "clean":
                ## We don't skeet out games where there are no HBP events.
                print(f"  😞 Nobody got hit during this game. Skipping.\n")
                os.remove(full_skeet_filename)
                continue
            elif skeet_parts[1] == "analyze":
                print(f"  😒 Current file is analysis information. Skipping.\n")
                continue

            ## Now check if it's already been skeeted. If so, remove all files.
            if dbmgr.has_been_skeeted(mode, play_id, verbose):
                print(f"  🤨 This event has already been skeeted!\n")
                sk.cleanup_after_skeet(mode, int(game_pk), play_id, verbose)
                continue

            ## At this point, let's start building the skeet(s).
            ## 1. Get skeet text.
            if verbose:
                print(f"{i + 1}. Skeet File: {full_skeet_filename}")
            skeet_text = sk.read_skeet_text(full_skeet_filename)
            print(f"{skeet_text}")

            ## 2. Get video.
            video_filepath = os.path.join(video_dir, f"{game_pk}_{play_id}.mp4")
            if not dbmgr.has_been_downloaded(
                mode, play_id, verbose
            ) and not os.path.exists(video_filepath):
                ## Don't add a video!
                video_filepath = None
                print(f"  ⛔ No event video associated with this HBP!")
            elif not dbmgr.has_been_downloaded(
                mode, play_id, verbose
            ) and os.path.exists(video_filepath):
                ## File exists but hasn't been marked as downloaded!
                dbmgr.set_download_flag(play_id)
                print(
                    f"  🤨 Event video has been downloaded but not marked so in the database."
                )
            elif dbmgr.has_been_downloaded(
                mode, play_id, verbose
            ) and not os.path.exists(video_filepath):
                ## This is an error condition! File is missing.
                video_filepath = None
                print(f"❌ Video {video_filepath} is missing!")
            elif dbmgr.has_been_downloaded(mode, play_id, verbose) and os.path.exists(
                video_filepath
            ):
                ## File has been marked as downloaded and does exist.
                pass

            if video_filepath:
                print(f"🎥 Video file:     {video_filepath}")

            ## 3. Get analysis plots and build plots data structures.
            plots = []
            plot_alts = []
            if mode == "hbp" and dbmgr.has_been_analyzed(mode, play_id, verbose):
                season = dbmgr.get_season_year(mode, play_id, verbose)
                current_play = dbmgr.get_event_play_data(mode, play_id, verbose)
                pitcher_info = bb.get_mlb_player_details(current_play[0][3], verbose)
                batter_info = bb.get_mlb_player_details(current_play[0][4], verbose)

                season_plot_filename = os.path.join(
                    plot_dir, f"{game_pk}_{play_id}_{season}.png"
                )
                batter_plot_filename = os.path.join(
                    plot_dir, f"{game_pk}_{play_id}_batter.png"
                )
                pitcher_plot_filename = os.path.join(
                    plot_dir, f"{game_pk}_{play_id}_pitcher.png"
                )
                if os.path.exists(season_plot_filename):
                    plots.append(season_plot_filename)
                    plot_alts.append(
                        f"Plot showing this event in the context of the entire {season} season."
                    )
                    print(f"📊 Season's plot:  {season_plot_filename}")
                if os.path.exists(batter_plot_filename):
                    plots.append(batter_plot_filename)
                    plot_alts.append(
                        f"Plot showing this event in the context of {batter_info['name']}'s entire career."
                    )
                    print(f"📊 Batter's plot:  {batter_plot_filename}")
                if os.path.exists(pitcher_plot_filename):
                    plots.append(pitcher_plot_filename)
                    plot_alts.append(
                        f"Plot showing this event in the context of {pitcher_info['name']}'s entire career."
                    )
                    print(f"📊 Pitcher's plot: {pitcher_plot_filename}")

            ## 4. Use atproto client to construct and send skeet(s).
            if video_filepath:
                vid_data = None
                with open(video_filepath, "rb") as f:
                    vid_data = f.read()
                if vid_data:
                    try:
                        root_post_ref = models.create_strong_ref(
                            client.send_video(
                                text=skeet_text,
                                video=vid_data,
                                video_alt=f"A video showing the hit-by-pitch at-bat.",
                            )
                        )
                    except exceptions.NetworkError as e:
                        print(f"[p:{play_id}] Network error occurred: {e}")
                    except exceptions.AtProtocolError as e:
                        print(f"[p:{play_id}] An AT Protocol error occurred: {e}")
                    except Exception as e:
                        print(f"[p:{play_id}] A general error occurred: {e}")
                else:
                    raise Exception(f"❌ Unable to read video file {video_filepath}!")
            else:
                root_post_ref = models.create_strong_ref(client.send_post(skeet_text))

            if plots:
                images = []
                for plot_path in plots:
                    with open(plot_path, "rb") as f:
                        images.append(f.read())

                first_datetime_obj = datetime.strptime(
                    dbmgr.get_earliest_date(mode), "%Y-%m-%d"
                )
                try:
                    reply_to_root = models.create_strong_ref(
                        client.send_images(
                            text=f"Based on data collected through {first_datetime_obj.strftime("%d %b %Y")}.",
                            images=images,
                            image_alts=plot_alts,
                            reply_to=models.AppBskyFeedPost.ReplyRef(
                                parent=root_post_ref, root=root_post_ref
                            ),
                        )
                    )
                except exceptions.NetworkError as e:
                    print(f"[c:{play_id}] Network error occurred: {e}")
                except exceptions.AtProtocolError as e:
                    print(f"[c:{play_id}] An AT Protocol error occurred: {e}")
                except Exception as e:
                    print(f"[c:{play_id}] A general error occurred: {e}")

            # 5. Clean up!
            if not test_mode:
                dbmgr.set_skeeted_flag(mode, play_id, verbose)
                sk.cleanup_after_skeet(mode, int(game_pk), play_id, verbose)

            print()
            skeet_counter = skeet_counter + 1
            if skeet_counter >= num_posts:
                break

        print()
        end_time = time.time()
        elapsed = end_time - start_time
        print("=" * 80)
        print(f"Completed in {elapsed:.2f} seconds")
        print("=" * 80)
        print()
        return 0

    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main(num_posts))

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from os import path

import config
import utility
from utility import log, exit_on_error


def _download_info():
    dir = config.get_config(config.key_load_dir)

    if path.exists(dir):

        # Find the last activites*.json file
        with os.scandir(dir) as it:
            timestamp = 0.0
            for entry in it:
                if entry.is_file() and re.match("activities-\d+-\d+\.json", entry.name):
                    if path.getctime(path.join(dir, entry.name)) > timestamp:
                        timestamp = path.getctime(path.join(dir, entry.name))
                        name = entry.name

        if name is not None:
            with open(path.join(dir, name), "rt") as file:
                j = json.load(file)

                download_date = datetime.fromtimestamp(timestamp).strftime("%A, %B %d, %Y %I:%M:%S")
                print(f"Last downloaded activity '{j[0]['activityId']}' was at {download_date}:")
                print(f"  ID   : {j[0]['activityId']}")
                print(f"  Name : {j[0]['activityName']}")
                print(f"  Start: {j[0]['startTimeLocal']}")
        else:
            print("No activities.csv file found. Seems to be the very first download. You should download a fixed number of activites.")

    else:
        print("Download directory not found. Seems to be the very first download. You should download a fixed number of activites.")



def process_download(args):
    log("process_download", "start")

    if args.info:
        _download_info()

    elif args.count:
        _download_count(args.count)

    else:
        _download_count("new")



    log("process_download", "end")


def _download_count(count):

    username = config.get_config(config.key_garmin_username)
    password = config.get_config(config.key_garmin_password)
    # log("sys.executable", sys.executable)

    load_dir = config.get_config(config.key_load_dir)

    # with subprocess.Popen(["ping", "www.google.de", "-w", "5"],
    #                            stdout=subprocess.PIPE,
    #                            stderr=subprocess.PIPE,
    #                            bufsize=1,
    #                            text=True) as p:


    with subprocess.Popen(["/home/chris/PycharmProjects/garmin-connect-export/venv/bin/python",
                           '/home/chris/PycharmProjects/garmin-connect-export/gcexport.py',
                           "--username", f"{username}" , "--password", f"{password}",
                           "-d", load_dir, "-f", "tcx", "-s", config.load_subdir, "-fp", "-c", f"{count}"],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          bufsize=1,
                          universal_newlines=True,
                          text=True
                          ) as p:

        # Doesn't flush for garmin but flushs for pings. Why?
        for line in p.stdout:
            print(line, end='', flush=True)

        # Print the rest
        for line in p.stdout.readlines():
            print(line, end='', flush=True)

        for line in p.stderr.readlines():
            print(line, end='', flush=True)

        # Doesn't work
        # if p.returncode != 0:
        #     exit_on_error(f"Download failed")


    log("donwload", "end")

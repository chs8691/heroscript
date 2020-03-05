import glob
from os import path

from load import create_load
from strava import load_strava_activity
from utility import log, exit_on_error


def process_load(args):
    log("process_load", "start")

    if args.file:
        create_load(args.file)

    elif args.directory:
        create_load(get_next_track_file(args.directory))
    else:
        exit_on_error("Invalid arguments: Use either '--file' or '--directory'.")

    if args.strava:
        load_strava_activity()

    log("process_load", "end")


def get_next_track_file(directory):
    """
    Get apth of the name track file
    :param directory: String with directorz=y
    :return: String with path or None
    """
    if not path.exists(directory):
        exit_on_error("Not a valid directory: '{}'".format(directory))

    types = ('*.TCX', '*.tcx')
    files_grabbed = []

    for files in types:
        files_grabbed.extend(glob.glob(path.join(directory, files)))

    files_grabbed.sort()
    log("files_grabbed", files_grabbed)

    if len(files_grabbed) == 0:
        exit_on_error("No track file found in {}".format(directory))
    else:
        return files_grabbed[0]

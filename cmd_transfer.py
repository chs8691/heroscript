from os import path, replace
from pathlib import Path

from load import save_load, read_load
from strava import strava_do_update
from utility import log, exit_on_error, resolve_path, warn
from velohero import velohero_check_sso_login
from velohero import velohero_do_update
from velohero import velohero_do_upload


def process_transfer(args):
    # log("process_transfer", "start")

    if not args.velohero and not args.archive and not args.strava:
        exit_on_error("Missing transfer destination(s). Use --help to see possible arguments")

    load = read_load()

    if args.strava and load.strava_activity_id is None:
        exit_on_error("STRAVA activity not loaded, so STRAVA can't be updated. If you want to update your STRAVA activity, " 
                      "first 'load --strava' to get the activity ID from STRAVA.")

    if not path.exists(load.file_name):
        exit_on_error("File not found: '{}'".format(load.file_name))

    dest_dir = None
    dest_file = None
    if args.archive:
        dest_dir = resolve_path(args.archive, load.started_at)
        if not path.exists(dest_dir):
            warn("Path doesn't exists and will be created: '{}".format(dest_dir))

        dest_file = path.join(dest_dir, path.basename(load.file_name))

        if path.exists(dest_file):
            warn("File exists and will be overwritten: '{}'".format(dest_file) )

    if args.velohero:

        # Velohero step 2: Upload, if not already done
        if load.velohero_workout_id is None:
            print("Upload to velohero.", end='', flush=True)

            velohero_check_sso_login()
            print(".", end='', flush=True)

            velohero_workout_id = velohero_do_upload(load.file_name)

            load.set_velohero_workout_id(velohero_workout_id)
            print(".", end='', flush=True)

            save_load(load)

            velohero_do_update(velohero_workout_id, None, load)

            print("Done (new Workout ID %s created)" % velohero_workout_id)

        # Velohero step update
        else:
            print("Update velohero.", end='', flush=True)

            velohero_check_sso_login()
            print(".", end='', flush=True)

            velohero_workout_id = load.velohero_workout_id

            # Velohero step update
            velohero_do_update(velohero_workout_id, None, load)

            print("Done (Workout ID %s updated)" % velohero_workout_id)

    if args.strava:
        strava_do_update()

    if args.archive and dest_dir is not None:
        if not path.exists(dest_dir):
            Path(dest_dir).mkdir(parents=True, exist_ok=True)

        log("os.replace from {} to".format(load.file_name), dest_dir)
        replace(load.file_name, dest_file)
        load.set_archived_to(dest_file)
        save_load(load)
        print("Archived: '{}'".format(dest_file))

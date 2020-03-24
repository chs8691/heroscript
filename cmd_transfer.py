from os import path, replace
from pathlib import Path

from load import save_load, read_load
from strava import strava_do_update
from velohero import velohero_check_sso_login
from velohero import velohero_do_update
from velohero import velohero_do_upload
import utility


def process_transfer(args):
    # utility.log("process_transfer", "start")

    if not args.velohero and not args.archive and not args.strava:
        utility.exit_on_error("Missing transfer destination(s). Use --help to see possible arguments")

    load = read_load()

    if args.strava and load.strava_activity_id is None:
        utility.exit_on_error("STRAVA activity not loaded, so STRAVA can't be updated. If you want to update your STRAVA activity, " 
                      "first 'load --strava' to get the activity ID from STRAVA.")

    if not path.exists(load.file_name):
        utility.exit_on_error("File not found: '{}'".format(load.file_name))
        
    if load.new_activity_type is None:
        utility.exit_on_error(f"Activity type not set! Use heroscript set --activity_type '{utility.activity_type_list}'")
        

    dest_dir = None
    dest_file = None
    if args.archive:
        dest_dir = utility.resolve_path(args.archive, load.started_at)
        if not path.exists(dest_dir):
            utility.warn("Path doesn't exists and will be created: '{}".format(dest_dir))

        dest_file = path.join(dest_dir, path.basename(load.file_name))

        if path.exists(dest_file):
            utility.warn("File exists and will be overwritten: '{}'".format(dest_file) )

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

        utility.log("os.replace from {} to".format(load.file_name), dest_dir)
        replace(load.file_name, dest_file)
        load.set_archived_to(dest_file)
        save_load(load)
        print("Archived: '{}'".format(dest_file))

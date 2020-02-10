import glob
import time
from os import path, replace
from pathlib import Path

import heroscript_gps
from persistance import read_load, save_load, create_load
from utility import log, exit_on_error, get_human_date, resolve_path, warn
from velohero import velohero_check_sso_login
from velohero import velohero_do_update
from velohero import velohero_do_upload


def process_show(args):
    log("process_show", "start")

    load = read_load()

    if args.map:
        heroscript_gps.show_map()
        # print("Opening map in default Browser...", end='', flush=True)
        # tracksfer_gps.map("track.gps")
        # print("Done.")
        return

    print('File Name              : %s' % load.file_name)
    print('--- ATTRIBUTES ---')

    if load.new_activity_type is None:
        print('Activity Type          : %s' % load.original_activity_type)
    else:
        print('Activity Type          : %s (original: %s)' %
              (load.new_activity_type, load.original_activity_type))

    print('Training Type          : %s' % load.training_type)

    print('Route Name             : %s' % load.route_name)

    print('Equipment Names        : %s' % load.equipment_names)

    print("Comment                : '%s'" % load.comment)
    print("")

    print("Started at (GMT)       : {}".format(get_human_date(load.started_at, "%a %y-%m-%d %H:%M")))

    print("Distance               : {0:.1f} k{1}".format(load.distance/1000, load.distance_unit_abbreviation()))

    print("Duration               : {} h".format(time.strftime('%H:%M:%S', time.gmtime(load.duration))))

    print("Velocity - Pace (total): {0:.1f} k{1}/h - {2}/k{3}".format(
        load.velocity_average, load.distance_unit_abbreviation(), load.pace, load.distance_unit_abbreviation()))

    print("Altitude               : \u25B2 {0:.0f} \u25bc {1:.0f}  [{2:.0f}..{3:.0f}] {4}".format(
        load.ascent, load.descent, load.altitude_min, load.altitude_max, load.distance_units))

    print('--- STATUS ---')
    print('Velohero Workout ID    : %s' % load.velohero_workout_id)

    print("Archived to            : {}".format(load.archived_to))

    log("process_show", "end")


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


def process_load(args):
    log("process_load", "start")

    if args.file:
        create_load(args.file)

    elif args.directory:
        create_load(get_next_track_file(args.directory))
    else:
        exit_on_error("Invalid arguments: Use either '--file' or '--directory'.")

    log("process_load", "end")


def process_set(args):
    log("process_set", "start")

    load = read_load()

    if args.activity_type:
        log("args.activity_type", args.training_type)
        load.set_activity_type(args.activity_type.strip().lower())

    if args.velohero_workout_id:
        log("args.velohero_workout_id", args.velohero_workout_id)
        if args.velohero_workout_id.strip() == '0':
            load.set_velohero_workout_id(None)
        else:
            load.set_velohero_workout_id(args.velohero_workout_id.strip())

    if args.training_type is not None:
        log("args.training_type", args.training_type)
        load.set_training_type(args.training_type.strip().lower())

    if args.route_name is not None:
        log("args.route_name", args.route_name)
        load.set_route_name(args.route_name.strip().lower())

    if args.equipment_names is not None:
        log("args.equipment_names", args.equipment_names)

        if len(args.equipment_names.strip()) == 0:
            equipment_names = []
        elif args.equipment_names.find(",") > 0:
            equipment_names = [e.strip().lower() for e in args.equipment_names.split(',')]
        else:
            equipment_names = [args.equipment_names.strip().lower()]

        log("equipment_names", equipment_names)
        load.set_equipment_names(equipment_names)

    if args.comment is not None:
        log("args.comment", args.comment)
        load.set_comment(args.comment.strip())

    save_load(load)

    log("process_set", "end")


def process_transfer(args):
    log("process_transfer", "start")

    if not args.velohero and not args.archive:
        exit_on_error("Don't know what to do. Use --help to see possible arguments")

    load = read_load()

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


    if args.archive and dest_dir is not None:
        if not path.exists(dest_dir):
            Path(dest_dir).mkdir(parents=True, exist_ok=True)

        log("os.replace from {} to".format(load.file_name), dest_dir)
        replace(load.file_name, dest_file)
        load.set_archived_to(dest_file)
        save_load(load)
        print("Archived: '{}'".format(dest_file))


    log("process_transfer", "end")

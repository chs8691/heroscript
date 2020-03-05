import re

import utility
from cmd_masterdata import find_training_type_by_name, read_masterdata
from load import read_load, save_load
from utility import log, exit_on_error


def _set_training_type(load, training_type):
    """
    Procondition: The type must exists as masterdata.
    Also updates the strava activity name prefix
    :param load:
    :param type: Valid training type from masterdata
    """

    load.set_training_type(training_type)

    data = read_masterdata()

    # STRAVA activity has a commute flag
    if training_type.lower() == 'commute' or training_type.lower() == 'pendel':
        prefix = ""

    # STRAVA activity has a trainer flag
    elif training_type.lower() == 'rolle' or training_type.lower() == 'indoor' or training_type.lower() == 'trainer':
        prefix = ""

    # Default training_type.lower()
    elif training_type.lower() == 'training':
        prefix = ""

    # STRAVA has a Competition flag, but I don't know how to update :o(
    elif training_type.lower() == 'competition' or training_type.lower() == 'wettkampf':
        prefix = training_type

    # All other types
    else:
        prefix = training_type

    if re.compile(".*: .*").match(load.strava_activity_name):
        name = load.strava_activity_name.split(": ", 1)[1]
    else:
        name = load.strava_activity_name

    if len(prefix) > 1:
        load.set_strava_activity_name(f"{prefix}: {name}")
    else:
        load.set_strava_activity_name(f"{name}")


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
        _set_training_type(load, find_training_type_by_name(args.training_type.strip().lower()))


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

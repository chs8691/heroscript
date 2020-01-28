import tracksfer_gps
from persistance import read_load, save_load, create_load
from utility import log, exit_on_error
from velohero import velohero_do_upload
from velohero import velohero_do_update
from velohero import velohero_check_sso_login


def process_show(args):
    log("process_show", "start")

    # load = Load()
    load = read_load()

    if args.map:
        print("Opening map...", end='', flush=True)
        tracksfer_gps.map("track.gps")
        print("Done.")
        return

    print('File Name           : %s' % load.file_name)
    print('--- ATTRIBUTES ---')

    if load.new_activity_type is None:
        print('Activity Type       : %s' % load.original_activity_type)
    else:
        print('Activity Type       : %s (original: %s)' %
              (load.new_activity_type, load.original_activity_type))

    print('Training Type       : %s' % load.training_type)

    print('Route Name          : %s' % load.route_name)

    print('Equipment Names     : %s' % load.equipment_names)

    print("Comment             : '%s'" % load.comment)

    print('--- STATUS ---')
    print('Velohero Workout ID : %s' % load.velohero_workout_id)

    log("process_show", "end")


def process_load(args):
    log("process_load", "start")

    if args.file:
        create_load(args.file)

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

    if args.velohero:

        # Velohero step 2: Upload, if not already done
        if load.velohero_workout_id is None:
            print("Upload to velohero.", end='', flush=True)

            velohero_check_sso_login()
            print(".", end='', flush=True)

            velohero_workout_id = velohero_do_upload(load.file_name)

            load = read_load()
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

        log("process_transfer", "end")

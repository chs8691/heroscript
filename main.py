import sys

from cmd_config import process_config, init_config, default_port
from cmd_masterdata import init_masterdata_storage
from cmd_masterdata import process_masterdata
from cmd_transfer import process_transfer
from cmd_set import process_set
from cmd_load import process_load
from cmd_show import process_show
from velohero import velohero_process_show, velohero_process_update, velohero_process_upload
from utility import set_log_switch, exit_on_error

import argparse


def execute_velohero_upload():
    velohero_process_upload(args)


def execute_velohero_update():
    velohero_process_update(args)


def execute_velohero_show():
    velohero_process_show(args)


def execute_transfer():
    process_transfer(args)


def execute_set():
    process_set(args)


def execute_config():
    process_config(args)


def execute_masterdata():
    process_masterdata(args)


def execute_show():
    process_show(args)


def execute_load():
    process_load(args)


args = None


# def parse_args(execute_load, execute_set, execute_show, execute_upload, execute_vh_show, execute_vh_upload, execute_vh_update):
def parse_args():
    """
    Examples:
        Show info of an workout file:
            main.py info --file=20191221-150315-activity_4355570485.tcx
            main.py info --directory=/home/chris/newActivities

        Upload an workout file and set an attribute:
            main.py upload --file=20191221-150315-activity_4355570485.tcx --sport_id='Mountainbike'

        Pick next file from a directory, upload and set value:
            main.py upload --directory=/home/chris/newActivities --sport_id='Mountainbike'

        Show workout's attributes:
            main.py show --id=4075724

        Update attribute of an an existing workout:
            main.py set --id=4075724 --sport_id=Mountainbike

    """
    global args

    parser = argparse.ArgumentParser(description="Upload activities to velohero an set proper attributes.")

    parser.add_argument("-l", "--log",
                        action='store_true',
                        help="Print log to the console")

    sub_parsers = parser.add_subparsers()

    # ######### masterdata #########
    data_parser = sub_parsers.add_parser('masterdata', help="Set and show master data like equipment and training type.")

    data_parser.add_argument("-l", "--list",
                             required=False,
                             action='store_true',
                             help="Print all master data as a list. This is the default argument.")

    data_parser.add_argument("-r", "--refresh",
                             required=False,
                             action='store_true',
                             help="Update all master data from Velohero (equipments and training types). "
                                  "A EQUIPMENT is compared by name: A equipment will only added to the master data, if"
                                  "it is found in Velohero and STRAVA, all other equipments will be ignored. "
                                  "The name in Velohero must be a substring in STRAVA's name, but spaces and case will be ignored."
                                  "A TYPE is configured by the user in Velohero (Training Type). There is a type specific"
                                  "behavior: A type named 'Competition/Wettkampf' will be used to set the Competition flag in STRAVA,"
                                  "same for 'Commute/Pendel' and 'Indoor/Rolle'. 'Training' is the standard type and has not specific behavior."
                                  "All other types will be used to tag STRAVA's activity name.")

    data_parser.add_argument("-v", "--validate",
                             required=False,
                             action='store_true',
                             help="Check, if master data are actual.")

    data_parser.set_defaults(func=execute_masterdata)

    # ######### config #########
    config_parser = sub_parsers.add_parser('config', help="Set and show script settings.")

    config_parser.add_argument("-l", "--list",
                               action='store_true',
                               help="Print all settings as a list")

    # For every new argument added here, cmd_config.py must be enhanced:
    #    - Define a constant key_....
    #    - Enhance _set_argument()
    #    - If argument has a default value, update _init_config

    config_parser.add_argument("-sc", "--strava_client_id",
                               required=False,
                               help="Set the STRAVA client ID for the used API. This can be found in STAVA / Settings / My API. "
                                    "If you havn't got alreay a created an API, you have to to this first."
                                    "Example: --velohero_sso_id kdRfmIHT6IVH1GI9SD32BIhaUpwTaQguuzE7XYt4 ")

    config_parser.add_argument("-sr", "--strava_reset",
                               required=False,
                               action='store_true',
                               help="Unset STRAVA access ids. "
                                    "Useful, if there is trouble with the authentication process.")

    config_parser.add_argument("-vs", "--velohero_sso_id",
                               required=False,
                               help="Set the velohero SSO key. "
                                    "Example: --velohero_sso_id kdRfmIHT6IVH1GI9SD32BIhaUpwTaQguuzE7XYt4 ")

    config_parser.add_argument("-p", "--port",
                               required=False,
                               help="Port for internal webserver, default is {}. Example: --port 1234"
                               .format(default_port))

    config_parser.set_defaults(func=execute_config)

    # ######### load #########
    load_parser = sub_parsers.add_parser('load', help="Load a track file")

    load_parser.add_argument("-f", "--file",
                             required=False,
                             help="Name (path) to the track file to load. This parameters excludes --directory.")

    load_parser.add_argument("-s", "--strava",
                             required=False,
                             action='store_true',
                             help="If set, activity values will be loaded from Strava. This is only useful, "
                                  "if the activity already exists in STRAVA")

    load_parser.add_argument("-d", "--directory",
                             required=False,
                             help="Path to the directory which contains one or more track files. In alphanumerical order,"
                                  "the first track file will be loaded. This parameters excludes --file.")

    load_parser.set_defaults(func=execute_load)

    # ######### set #########
    set_parser = sub_parsers.add_parser('set', help="Set attributes for a loaded track file")

    set_parser.add_argument("-a", "--activity_type",
                            required=False,
                            choices=['run', 'mtb', 'roadbike', 'fitness', 'hiking'],
                            help="Set the activity type to Running, Mountain Biking, Road Cycling, Fitness or Hiking")

    set_parser.add_argument("-t", "--training_type",
                            required=False,
                            help="Set the training type by its name (unset with ''). "
                                 "The name must exactly match the defined one in Velohero. "
                                 "Examples: 'Pendel', 'Training' or  ''")

    set_parser.add_argument("-r", "--route_name",
                            required=False,
                            help="Set value for the route by its name. Unset with ''. "
                                 "The name must match (case insensitive) the route name exactly or a unique substring of it. "
                                 "Examples: 'Goldbach Wintercross 10 KM', 'goldbach', '")

    set_parser.add_argument("-e", "--equipment_names",
                            required=False,
                            help="Set values for Equipments by its names, delimeted by a comma (','). Unset with ''. "
                                 "The name must match (case insensitive) the material name exactly or a unique substring of it. "
                                 "Examples: 'Laufschuhe Saucony Ride ISO, MTB Focus', ''")

    set_parser.add_argument("-c", "--comment",
                            required=False,
                            help="Set the comment (unset with ''). "
                                 "Examples: 'Wonderful weather', or  ''")

    set_parser.add_argument("-v", "--velohero_workout_id",
                            required=False,
                            help="Velohero workout ID. If set, the upload command only udpates the existing workout "
                                 "in Velohero. Set ID to '0' to force an upload. Examples: '4124109' or '0'")

    set_parser.set_defaults(func=execute_set)

    # ######### show #########
    show_parser = sub_parsers.add_parser('show', help="Show actual attributes for a loaded track file")

    show_parser.add_argument("-m", "--map",
                             required=False,
                             action='store_true',
                             help="Show Track in a map.")

    show_parser.set_defaults(func=execute_show)

    # ######### transfer #########
    transfer_parser = sub_parsers.add_parser('transfer', help="Upload/Update the track file with the actual setting")

    transfer_parser.add_argument("-v", "--velohero",
                                 required=False,
                                 action='store_true',
                                 help="Upload file to Velohero and set values or, ff the Velohero Workout ID is set, "
                                      "just update the values of the existing Workout.")

    transfer_parser.add_argument("-s", "--strava",
                                 required=False,
                                 action='store_true',
                                 help="Update STRAVA activity. The activity must exist in STRAVA and loaded with 'load --strava'")

    transfer_parser.add_argument("-a", "--archive",
                                 required=False,
                                 help="Move the track file to this archive directory. Supported placeholder is '{YYYY}'."
                                      "Examples: '../archive' or '/home/chris/tracks/{YYYY}'")

    transfer_parser.set_defaults(func=execute_transfer)

    # ######### velohero show #########
    vh_show_parser = sub_parsers.add_parser('vh-show', help="Show existing workout in Velohero")

    vh_show_parser.add_argument("-i", "--workout_id",
                                required=True,
                                help="Velohero workout ID.")

    vh_show_parser.set_defaults(func=execute_velohero_show)

    # shared arguments for set and upload
    vh_field_parser = argparse.ArgumentParser(add_help=False)

    vh_field_parser.add_argument("-date", "--workout_date",
                                 required=False,
                                 help="Set Date (field 'workout_date'). Example: '31.12.2020' or '2020-12-31")

    vh_field_parser.add_argument("-time", "--workout_start_time",
                                 required=False,
                                 help="Set Start Time (Field 'workout_start_time'). Example: '17:59:00'")

    vh_field_parser.add_argument("-dur", "--workout_dur_time",
                                 required=False,
                                 help="Set Duration (field 'workout_dur_time'). Example: '2:23:00'")

    vh_field_parser.add_argument("-sport", "--sport_id",
                                 required=False,
                                 help="Set Sport (field 'sport_id'). Value can be id or description (case sensitive). "
                                      "Examples: '1', 'Mountainbike'")

    vh_field_parser.add_argument("-type", "--type_id",
                                 required=False,
                                 help="Set value Training type (field 'type_id'). Value can be id or description "
                                      "(case sensitive). Examples: '7431', 'Training")

    vh_field_parser.add_argument("-route", "--route_id",
                                 required=False,
                                 help="Set value Route (field 'route_id'). Value can be id or description "
                                      "(case sensitive). Examples: '12345', 'Berlin Marathon")

    vh_field_parser.add_argument("-dist", "--workout_dist_km",
                                 required=False,
                                 help="Set Distance (field 'workout_dist_km') in your unit (configured in Velohero). "
                                      "Example: '12345'")

    vh_field_parser.add_argument("-asc", "--workout_asc_m",
                                 required=False,
                                 help="Set Ascent (Field 'workout_asc_m') in your unit (configured in Velohero)."
                                      " Example: '1234'")

    vh_field_parser.add_argument("-dsc_m", "--workout_dsc_m",
                                 required=False,
                                 help="Set Descent (field 'workout_dsc_m') in your unit (configured in Velohero)."
                                      " Example: '1234'")

    vh_field_parser.add_argument("-alt_min", "--workout_alt_min_m",
                                 required=False,
                                 help="Set Minimum Altitude (field 'aworkout_alt_min_m')"
                                      " in your unit (configured in Velohero). Example: '100'")

    vh_field_parser.add_argument("-alt_max", "--workout_alt_max_m",
                                 required=False,
                                 help="Set Maximum Altitude )field 'workout_alt_max_m') "
                                      "in your unit (configured in Velohero). Example: '1000'")

    vh_field_parser.add_argument("-spd_avg", "--workout_spd_avg_kph",
                                 required=False,
                                 help="Set Average Speed (field 'workout_spd_avg_kph') "
                                      "in your unit (configured in Velohero). Example: '23.4'")

    vh_field_parser.add_argument("-spd_max_kph", "--workout_spd_max_kph",
                                 required=False,
                                 help="Set Maximum Speed (field 'workout_spd_max_kph') "
                                      "in your unit (configured in Velohero). Example: '45.6'")

    vh_field_parser.add_argument("-hr_avg_bpm", "--workout_hr_avg_bpm",
                                 required=False,
                                 help="Set Average Heart Rate (field 'workout_hr_avg_bpm'). Example: '123'")

    vh_field_parser.add_argument("-hr_max_bpm", "--workout_hr_max_bpm",
                                 required=False,
                                 help="Set Maximum Heart Rate (field 'workout_hr_max_bpm'). Example: '171'")

    vh_field_parser.add_argument("-equipment", "--equipment_ids",
                                 required=False,
                                 help="Set values for Equipments (field 'equipments_ids'). "
                                      "Examples: '29613, 12345', ''")

    vh_field_parser.add_argument("-comment", "--workout_comment",
                                 required=False,
                                 help="Field 'workout_comment'. Example: 'Got a bonk.'")

    # # ######### velohero update #########
    vh_update_parser = sub_parsers.add_parser('vh-update',
                                              parents=[vh_field_parser],
                                              help="Set attributes for an existing workout in Velohero directly"
                                                   " (independent of a load)")

    vh_update_parser.add_argument("-i", "--workout_id",
                                  required=True,
                                  help="Velohero workout ID. Example: '4075724'")
    vh_update_parser.set_defaults(func=execute_velohero_update)

    # ######### velohero upload #########
    vh_upload_parser = sub_parsers.add_parser('vh-upload',
                                              parents=[vh_field_parser],
                                              help="Upload workout file to Velohero directly"
                                                   " (independent of a load)")

    vh_upload_parser.add_argument("-f", "--file",
                                  required=True,
                                  help="Name (path) to the track file to upload")

    vh_upload_parser.set_defaults(func=execute_velohero_upload)

    args = parser.parse_args()

    # There must be choosen an argument
    if len(sys.argv) == 1:
        exit_on_error("Missing argument, see --help.")

    if args.log:
        set_log_switch(True)

    args.func()


if __name__ == '__main__':
    init_config()
    init_masterdata_storage()
    parse_args()

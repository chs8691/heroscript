import argparse
import sys

import utility
from cmd_config import process_config, init_config
from cmd_load import process_load
from cmd_masterdata import init_masterdata_storage
from cmd_masterdata import process_masterdata
from cmd_set import process_set
from cmd_show import process_show
from cmd_transfer import process_transfer
from cmd_download import process_download
from config import default_port
from utility import set_log_switch, exit_on_error
from velohero import velohero_process_show, velohero_process_update, velohero_process_upload


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


def execute_download():
    process_download(args)

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
    data_parser = sub_parsers.add_parser('masterdata',
                                         help="Set or show master data (equipment and training type).",
                                         description="Set or show master data (equipment and training type)."
                                                     "Equipments will be downloaded from Velohero and from Strava "
                                                     "and then merged together by its name. In consequence, to use an "
                                                     "equipment in heroscript you have to create it twice, once in "
                                                     "velohero and once in Strava. "
                                                     "The second master data is Training Type (Trainingsarten), "
                                                     "imported from Velohero. To set the training type manually, use "
                                                     "the set command. But more comfortable could be to customize it "
                                                     "directly in your Strava activity before the load (see load "
                                                     "command)."
                                         )

    data_parser.add_argument("-l", "--list",
                             required=False,
                             action='store_true',
                             help="Print all master data as a list. This is the default argument.")

    data_parser.add_argument("-r", "--refresh",
                             required=False,
                             action='store_true',
                             help="Update all master data from Velohero (equipments and training types). "
                                  "A EQUIPMENT is compared by name: A equipment will only added to the master data, if"
                                  "it is found in Velohero and Strava, all other equipments will be ignored. "
                                  "In Strava, the equipment can be used to specify activity type and training type:"
                                  "For bikes, the frame type will be mapped to the activity type (Mountainbike to mtb, etc.). "
                                  "Shoes, will be mapped to run. In addition, this can be overridden by a value heroscript.activity_type='YOUR_CHOOSEN_TYPE' "
                                  "in the description, for instance heroscript.activity_type='fitness'. "
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

    # ######### download #########
    download_parser = sub_parsers.add_parser('download',
                                             help="Download track files from Garmin Connect",
                                             description="Download new or a specified number of activity files in TCX format. "
                                                         "The working directory is .download. The downloaded activitiy "
                                                         "files will be moved to the load_dir (set with 'config --load_dir'). "
                                             )

    download_parser.add_argument("-c", "--count",
                                 required=False,
                                 help="Specify a fixed number of latest activities to download. If not given, all "
                                      "new activity files will be loaded. Must be used for the very first downloadb "
                                      "to avoid downloading all existing activities from Garmin Connect. "
                                      "Example: 'download --count 3' will load the last three activities from Garmin "
                                      "Connect.")

    download_parser.add_argument("-i", "--info",
                             required=False,
                             action='store_true',
                             help="Prints info about the last download.")


    download_parser.set_defaults(func=execute_download)


    # ######### config #########
    config_parser = sub_parsers.add_parser('config',
                                           help="Set and show script settings.",
                                           description="Set the configuration for Heroscript. This will be stored in the "
                                                       ".heroscript directory of the user's home directory. Some configurations"
                                                       "will be handled by the script but there are also values the user can "
                                                       "maintain. Calling config without paramater, all values will be listed.",
                                           )

    config_parser.add_argument("-l", "--list",
                               action='store_true',
                               help="Print all settings as a list. This is the default argument.",
                               )

    config_parser.add_argument("-d", "--delete",
                               help="Delete item. Mandatory items will not be deleted but replaced by the default value."
                                    " Examples 'config --delete strava_description__BY__strava_name' will delete the "
                                    "item, but 'config --delete strava_client_id' will reset to default." ,
                               )

    # For every new argument added here, cmd_config.py must be enhanced:
    #    - Define a constant key_....
    #    - Enhance _set_argument()
    #    - If argument has a default value, update _init_config

    config_parser.add_argument("-sc", "--strava_client_id",
                               required=False,
                               help="Set the STRAVA client ID for the used API. This can be found in STAVA / Settings / My API. "
                                    "If you havn't got alreay a created an API, you have to to this first."
                                    "Example: --strava_client_id 43527 ")

    config_parser.add_argument("-sr", "--strava_reset",
                               required=False,
                               action='store_true',
                               help="Unset STRAVA access ids. "
                                    "Useful, if there is trouble with the authentication process.")

    config_parser.add_argument("-vs", "--velohero_sso_id",
                               required=False,
                               help="Set the velohero SSO key. "
                                    "Example: --velohero_sso_id kdRfmIHT6IVH1GI9SD32BIhaUpwTaQguuzE7XYt4 ")

    config_parser.add_argument("-gu", "--garmin_connect_username",
                               required=False,
                               help="Garmin connect user name "
                                    "Example: --garmin_connect_username='chris.schulzi@topbox.com' ")

    config_parser.add_argument("-gp", "--garmin_connect_password",
                               required=False,
                               help="Garmin connect password "
                                    "Example: --garmin_connect_password='top-secret-pASSw0rd' ")

    config_parser.add_argument("-p", "--port",
                               required=False,
                               help="Port for internal webserver, default is {}. Example: --port 1234"
                               .format(default_port))

    config_parser.add_argument("-ld", "--load_dir",
                               required=False,
                               help="Root directory for the activity files to load. This will be used to download "
                                    "activities from Garmin. The track files will be stored in the subdirectory "
                                    f"'{utility.load_subdir}'. Example: --load_dir '/garmin_import'"
                               )

    config_parser.add_argument("-ad", "--archive_dir",
                               required=False,
                               help="Default directory to transfer the track file to this archive directory. "
                                    "Supported placeholder is '{YYYY}'."
                                    "Examples: '../archive' or '/home/chris/tracks/{YYYY}'"
                               )

    config_parser.add_argument("-sd", "--strava_description",
                               required=False,
                               help="Add a description line automatically to the Strava activity, if the value condition maps. "
                                    "Supported values for the condition are 'strava_name(TEXT TO SEARCH FOR)' "
                                    "and training_type((TRAINING_TYPE)) followed by a questionmark '?' and the text. "
                                    "The original description will be purged, if exists."
                                    "Example 1: --strava_description=strava_name(die runden stunde)?https://www.instagram.com/explore/tags/dierundestunde/ "
                                    "will add the link to the description, if the Activity name is 'Die Runden Stunde'. "
                                    "Example 2: --strava_description=training_type(pendel)?https://flic.kr/s/aHsm3QRWjT "
                                    "will create the link, if the training type is set to 'Pendel'.")

    config_parser.set_defaults(func=execute_config)

    # ######### load #########
    load_parser = sub_parsers.add_parser('load',
                                         description="First step of the workflow: Load an activity file from a local "
                                                     "directory into the stage."
                                                     "With no arguments, the next file from the default directory "
                                                     "will be loaded. For this the default directory must be set once "
                                                     "by velohero config --load_dir 'your_path'. Or the directory "
                                                     "or a file can be set by an optional argument.",
                                         # help="",
                                         )

    load_parser.add_argument("-f", "--file",
                             required=False,
                             help="Name (path) to the track file to load. This parameters excludes --directory.")

    load_parser.add_argument("-s", "--strava",
                             required=False,
                             action='store_true',
                             help="If set, values will be loaded from the existing Strava activity (matching by start "
                                  "tinme): ID and name. The training type will be defined by the flags for commute and "
                                  "trainer (indoor), the setting of the workout type to 'Competition' or the prefix in "
                                  " name (separated by a colon ':'). ")

    load_parser.add_argument("-d", "--directory",
                             required=False,
                             help="Path to the directory which contains one or more track files. In alphanumerical order,"
                                  "the first track file will be loaded. This parameters excludes --file.")

    load_parser.add_argument("-i", "--info",
                             required=False,
                             action='store_true',
                             help="Prints info about the track files in the configured directory.")

    load_parser.set_defaults(func=execute_load)

    # ######### set #########
    set_parser = sub_parsers.add_parser('set',
                                        help="Set attributes for a loaded track file",
                                        description="After loading an activity file into the stash, values can be"
                                                    "changed with the set command. This can be useful, if the activity "
                                                    "is not proper configured in Strava. Use the show command to list"
                                                    "the actual settings.",
                                        )

    set_parser.add_argument("-at", "--activity_type",
                            required=False,
                            choices=utility.activity_type_list,
                            help="Set the activity type to Running, Mountain Biking, Road Cycling, Fitness or Hiking. "
                                 "Will be used to set the workout type in Velohero.")

    set_parser.add_argument("-tt", "--training_type",
                            required=False,
                            help="Set the training type by its name (unset with ''). "
                                 "The input must match exactly one master data item "
                                 "(which must be created with 'masterdata --refresh'). Heroscript is expecting, that"
                                 "there are training types for competition ('Competition' or 'Wettkampf'), Commute "
                                 "('Commute' or 'Pendel'), Indoor Cycling ('Indoor', 'Trainer' or 'Rolle') and "
                                 "'Training' as the default type. And there can be additional types, too. This types"
                                 "must be defined in Velohero and downloaded with 'masterdata --refresh'. If you need"
                                 "other training types, you have to fork the scripting for you."
                                 "Examples: 'Pendel', 'Training' or  '', but also 'pendel' or 'p'")

    set_parser.add_argument("-r", "--route_name",
                            required=False,
                            help="Set value for the route by its name. Unset with ''. "
                                 "The name must match (case insensitive) the route name exactly or a unique substring of it. "
                                 "Will be used to update Velohero, not used for STRAVA. "
                                 "Examples: 'Goldbach Wintercross 10 KM', 'goldbach', ' ")

    set_parser.add_argument("-e", "--equipment_names",
                            required=False,
                            help="Set values for Equipments by its names, delimeted by a comma (','). Unset with ''. "
                                 "The name must match (case insensitive) the material name exactly or a unique substring of it. "
                                 "Examples: 'Laufschuhe Saucony Ride ISO, MTB Focus', ''")

    set_parser.add_argument("-t", "--title",
                            required=False,
                            help="Set the activity title (unset with '').  In Velhero this will be saved as "
                                 "comment, in Strava this will be part of the name (without the optional training type). "
                                 "Examples: 'Wonderful weather tour', or  'Day 1 of 5'")

    set_parser.add_argument("-c", "--comment",
                            required=False,
                            help="Set the comment (unset with '') in Velhero and overwrites the name in STRAVA"
                                 "Examples: 'Wonderful weather', or  ''")

    set_parser.add_argument("-v", "--velohero_workout_id",
                            required=False,
                            help="Velohero workout ID. If set, the upload command only udpates the existing workout "
                                 "in Velohero. Set ID to '0' to force an upload. Examples: '4124109' or '0'")

    set_parser.set_defaults(func=execute_set)

    # ######### show #########
    show_parser = sub_parsers.add_parser('show',
                                         help="Show actual attributes for a loaded track file",
                                         description="Shows the values of a loaded activity."
                                         )

    show_parser.add_argument("-m", "--map",
                             required=False,
                             action='store_true',
                             help="Show Track in a map.")

    show_parser.set_defaults(func=execute_show)

    # ######### transfer #########
    transfer_parser = sub_parsers.add_parser('transfer',
                                             help="Upload/Update the track file with the actual setting",
                                             description="Finalized the workflow for a loaded activity by exporting it"
                                                         "the specified destinations: Upload to Velohero, update "
                                                         "Strava and moving the track file to a local archive"
                                                         "directory.",
                                             )

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
                                 action='store_true',
                                 required=False,
                                 help="Move the track file to the default archive directory. "
                                      "For this it must be set once by velohero config --archive_dir 'your_path'."
                                      "Supported placeholder is '{YYYY}'."
                                      "Examples: config --archive_dir='../archive' or config -ad '/home/chris/tracks/{YYYY}'")

    transfer_parser.add_argument("-d", "--dir",
                                 required=False,
                                 help="Move the track file to this archive directory. "
                                      "Supported placeholder is '{YYYY}'."
                                      "Examples: --dir='../archive' or -d '/home/chris/tracks/{YYYY}'")

    transfer_parser.add_argument( "--purge",
                             required=False,
                             help="Delete the activity and remove the load. This option can be useful to get rid of "
                                  "double downloaded files. For security reason the filename is the parameter. "
                                  "Be careful, this can not be undone! "
                                  "Example: 'transfer --purge 20200403-122359.tcx'")

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
                                 help="Set Sport (field 'sport_id'). Value can be sport's id or name (case insensitive). "
                                      "Examples: '1', 'Mountainbike'")

    vh_field_parser.add_argument("-type", "--type_id",
                                 required=False,
                                 help="Set value Training type (field 'type_id'). Value can be id or name "
                                      "(case sensitive). Examples: '7431', 'Training")

    vh_field_parser.add_argument("-route", "--route_id",
                                 required=False,
                                 help="Set value Route (field 'route_id'). Value can be id or name "
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

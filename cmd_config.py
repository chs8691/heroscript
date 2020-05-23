import pickle
import re

import masterdata
from storage import Storage
from utility import log, exit_on_error

import config

def process_config(args):
    log("process_config", "start")

    if args.delete:
        _delete_argument(args.delete)

    elif args.strava_client_id or \
            args.strava_reset or \
            args.velohero_sso_id or \
            args.port or \
            args.strava_description or\
            args.load_dir or \
            args.garmin_connect_username or\
            args.garmin_connect_password or\
            args.archive_dir:
        _set_argument(args)

    elif args.list:
        _list_config()

    else:
        _list_config()

    log("process_config", "end")


def init_config():
    """
    Check and sanatize the persisted config data.py
    Call this every time, config logic has changed, e.g. in startup (after a new script version).
    """
    log("init_config", "start")

    storage = Storage()

    if not storage.get_config_path().exists():
        print("Config not found, create it now: {}".format(storage.get_config_path().absolute()))
        # Create new config and initialize it with default values
        config._save_config(dict())

    myconfig = config.read_config()

    if config.key_port not in myconfig:
        log(f"Create default {config.key_port}", config.default_port)
        config.save_item(config.key_port, config.default_port)

    if config.key_archive_dir not in myconfig:
        log(f"Create default {config.key_archive_dir}", config.default_archive_dir)
        config.save_item(config.key_archive_dir, config.default_archive_dir)

    if config.key_velohero_sso_id not in myconfig:
        log(f"Create empty {config.key_velohero_sso_id}", "")
        config.save_item(config.key_velohero_sso_id, "")

    if config.key_garmin_username not in myconfig:
        log(f"Create empty {config.key_garmin_username}", "")
        config.save_item(config.key_garmin_username, "")

    if config.key_garmin_password not in myconfig:
        log(f"Create empty {config.key_garmin_password}", "")
        config.save_item(config.key_garmin_password, "")

    if config.key_load_dir not in myconfig:
        log(f"Create default {config.key_load_dir}", config.default_load_dir)
        config.save_item(config.key_load_dir, config.default_load_dir)

    if config.key_strava_client_id not in myconfig:
        log("Create default strava_client_id", config.key_strava_client_id)
        config.save_item(config.key_strava_client_id, config.default_strava_client_id)

    if config.key_strava_client_secret not in myconfig:
        log("Create default strava_client_secret", config.key_strava_client_secret)
        config.save_item(config.key_strava_client_secret, config.default_strava_client_secret)

    log("init_config", "end")


def _init_config():
    # Create new config and initialize it with default values
    config._save_config(dict())
    config.save_item(config.key_port, config.default_port)
    config.save_item(config.key_load_dir, config.default_load_dir)


def _delete_argument(key):

    if config.find(key) is None:
        exit_on_error(f"Key '{key}' not found!")

    elif key == config.key_load_dir:
        config.save_item(key, config.default_load_dir)
        reset = True

    elif key == config.key_archive_dir:
        config.save_item(key, config.default_archive_dir)
        reset = True

    else:
        config.delete_item(key)

    if reset:
        print(f"{key} resetted.")


def _set_argument(args):
    """
    Must be expanded for every new key,
    """
    cnt = 0
    if args.velohero_sso_id:
        config.save_item(config.key_velohero_sso_id, args.velohero_sso_id)
        cnt += 1

    if args.port:
        config.save_item(config.key_port, args.port)
        cnt += 1

    if args.strava_client_id:
        config.save_item(config.key_strava_client_id, args.strava_client_id)
        cnt += 1

    if args.load_dir:
        config.save_item(config.key_load_dir, args.load_dir)
        cnt += 1

    if args.archive_dir:
        config.save_item(config.key_archive_dir, args.archive_dir)
        cnt += 1

    if args.garmin_connect_username:
        config.save_item(config.key_garmin_username, args.garmin_connect_username)
        cnt += 1

    if args.garmin_connect_password:
        config.save_item(config.key_garmin_password, args.garmin_connect_password)
        cnt += 1

    if args.strava_reset:
        config.save_item(config.key_strava_access_token, None)
        cnt += 1
        config.save_item(config.key_strava_refresh_token, None)
        cnt += 1
        config.save_item(config.key_strava_expired_at, None)
        cnt += 1

    if args.strava_description:

        regex1 = re.compile("(strava_name)\((.*?)\)\?(.*)")
        res1 = regex1.match(args.strava_description)

        regex2 = re.compile("(training_type)\((.*?)\)\?(.*)")
        res2 = regex2.match(args.strava_description)

        if res1 and len(res1.group(3).strip()) > 0:
                config.save_item("{}{}".format(config.key_strava_description_prefix, res1.group(1)),
                          "{}?{}".format(res1.group(2), res1.group(3)))
                cnt += 1

        elif res2:
            training_type = masterdata.get_type(res2.group(2))
            config.save_item("{}{}".format(config.key_strava_description_prefix, res2.group(1)),
                      "{}?{}".format(training_type['name'], res2.group(3)))
            cnt += 1

        else:
            exit_on_error("Invalid config value. See 'config --help.'")

    if cnt == 0:
        print("No config value set. Did you set proper key? For a value description see: 'config --help'")
    else:
        print(f"Set {cnt} value(s).")


def _list_config():
    """
    List values
    """
    myconfig = config.read_config()

    for key, value in myconfig.items():
        print("{}: {}".format(key, value))

    return

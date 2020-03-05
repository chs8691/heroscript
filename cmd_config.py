import pickle

from storage import Storage
from utility import log, exit_on_error

# For every config item, this constant must be defined
key_velohero_sso_id = 'velohero_sso_id'

key_port = 'port'
default_port='4312'

key_strava_client_id = 'strava_client_id'

# Client ID of my STRAVA API (Christian Schulzendorff). Please, don't use this API only for Heroscript
default_strava_client_id = '43527'

key_strava_client_secret = 'strava_client_secret'

# Please, don't share this 'secret'
default_strava_client_secret = '509d7ed7ab29c93bb1a80fa05f3a1627c57e413f'


def process_config(args):
    log("process_config", "start")

    if args.list:
        _list_config()
    else:
        _set_argument(args)

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
        _save_config(dict())

    config = read_config()

    if key_port not in config:
        log("Create default key_port", default_port)
        save_item(key_port, default_port)

    if key_strava_client_id not in config:
        log("Create default strava_client_id", key_strava_client_id)
        save_item(key_strava_client_id, default_strava_client_id)

    if key_strava_client_secret not in config:
        log("Create default strava_client_secret", key_strava_client_secret)
        save_item(key_strava_client_secret, default_strava_client_secret)

    log("init_config", "end")


def save_item(key, value):
    """
    Add or replace one item in the config list
    :param item: Item to append or replace
    """
    config = read_config()

    log("Setting {}".format(key), value)

    # Remove old item, if exists
    if key in config:
        config.pop(key)

    config[key] = value

    _save_config(config)


def _init_config():
    # Create new config and initialize it with default values
    _save_config(dict())
    save_item(key_port, default_port)


def _set_argument(args):
    """
    Must be expanded for every new key,
    """
    cnt = 0
    if args.velohero_sso_id:
        save_item(key_velohero_sso_id, args.velohero_sso_id)
        cnt += 1

    if args.port:
        save_item(key_port, args.port)
        cnt += 1

    if args.strava_reset:
        save_item(key_strava_access_token, None)
        cnt += 1
        save_item(key_strava_refresh_token, None)
        cnt += 1
        save_item(key_strava_expired_at, None)
        cnt += 1

    if cnt == 0:
        print("No config value set. Did you set proper key? For a value description see: 'config --help'")
    else:
        print(f"Set {cnt} value(s).")


def _list_config():
    """
    List values
    """
    config = read_config()

    for key, value in config.items():
        print("{}: {}".format(key, value))

    return


def _save_config(config):
    storage = Storage()
    file = storage.get_config_path()
    # log("file_name", file)

    with file.open('wb') as file:
        pickle.dump(config, file)


def get_config(key):
    """
    Get the value for the given key.  The key must exist otherwise the exit is processed.
    :param key String with key name
    :return: Found value
    """
    if key in read_config():
        return read_config()[key]
    else:
        exit_on_error(f"Config key '{key}' not found !")


def read_config():
    storage = Storage()

    with storage.get_config_path().open('rb') as file:
        config = pickle.load(file)

    return config


key_strava_access_token = 'strava_access_token'
key_strava_refresh_token = 'strava_refresh_token'
key_strava_expired_at = 'strava_expired_at'
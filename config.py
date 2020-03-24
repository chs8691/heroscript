# For every config item, this constant must be defined
import pickle

from storage import Storage
from utility import log, exit_on_error, warn

key_velohero_sso_id = 'velohero_sso_id'

key_port = 'port'
default_port='4312'

key_load_dir = 'load_dir'

key_archive_dir = 'archive_dir'

key_strava_client_id = 'strava_client_id'

# Client ID of my STRAVA API (Christian Schulzendorff). Please, use this API only for Heroscript
default_strava_client_id = '43527'

key_strava_client_secret = 'strava_client_secret'

# Please, don't share this 'secret'
default_strava_client_secret = '509d7ed7ab29c93bb1a80fa05f3a1627c57e413f'


key_strava_access_token = 'strava.access_token'
key_strava_refresh_token = 'strava.refresh_token'
key_strava_expired_at = 'strava.expired_at'
key_strava_description_prefix = 'strava.description__BY__'


def save_item(key, value):
    """
    Add or replace one item in the config list
    :param item: Item to append or replace
    """
    myconfig = read_config()

    log("Setting {}".format(key), value)

    # Remove old item, if exists
    if key in myconfig:
        myconfig.pop(key)

    myconfig[key] = value

    _save_config(myconfig)


def get_strava_description_items():
    """
    Returns all items with strava.descriptions. The key will be a short cut without 'strava.description' prefix.
    :return: Dictionary with config items with shortcut keys, can be empty. For instance:
            [
                {
                    'condition_field': 'strava.name',
                    'condition_value': 'die runden stunde',
                    'text': 'ttt',
                },
                {
                    'condition_field': 'training_type',
                    'condition_value': 'Etappe',
                    'text': 'bbbb',
                }
            ]

    """
    ret = []
    # for item in read_config().items():

    for (key, value) in [i for i in read_config().items() if i[0].startswith(key_strava_description_prefix)]:
        # print(f"{key} --> {value}")
        parts = value.split("?")

        # Should never hit in production
        if len(parts) != 2:
            warn(f"Invalid config value '{value}' for key '{key}': Missing '?'")
            continue

        ret.append(
            dict(condition_field=key.replace(key_strava_description_prefix,""),
                 condition_value=parts[0],
                 text=parts[1],)
        )

    # print(ret)
    return ret


def find(key):
    """
    Search for the value for the given key.
    :key: Name of a key to search for, can be unknown
    :return: Found value or, if not exists, None
    """
    if key in read_config():
        return read_config()[key]
    else:
        return None


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


def _save_config(config):
    storage = Storage()
    file = storage.get_config_path()
    # log("file_name", file)

    with file.open('wb') as file:
        pickle.dump(config, file)



import pickle
import re

import strava
import velohero
from masterdata import read_masterdata
from storage import Storage
from utility import log, exit_on_error, is_commute_training_type, is_indoor_training_type, is_competition_training_type, \
    is_default_training_type


def _do_list():
    data = read_masterdata()
    log("masterdata", data)

    if 'types' in data:
        print("TYPES")
        for t in data['types']:
            tag = ""
            if is_commute_training_type(t['name']):
                tag = "<=== Maps STRAVA commute flag"
            elif is_indoor_training_type(t['name']):
                tag = "<=== Maps STRAVA indoor flag"
            elif is_competition_training_type(t['name']):
                tag = "<=== Flag STRAVA activity as a Competition"
            elif is_default_training_type(t['name']):
                tag = "<=== Default type, with no special behavior"

            print("  Velohero-ID {id:7d}: {name} {tag}".format(id=int(t['velohero_id']), name=t['name'], tag=tag))
    else:
        "Training Types not set. Use 'reload' to fill data.py"

    if 'equipments' in data:

        print("\nEQUIPMENTS")

        print("    {:10s} | {:10s} | {:20s} | {:20s} | {} "
              .format("VELOHERO-ID", "STRAVA-ID", "ACTIVITY TYPE", "TRAINING TYPE", "NAME"))

        line = "     {id:10s} | {strava_id:10s} | {activity_type:20s} | {training_type:20s} | {name} "
        print("  Shoes")
        for t in [t for t in data['equipments'] if t['type'] == 'shoe']:
            print(line.format(id=str(t['velohero_id']),
                              name=str(t['name']),
                              strava_id=str(t['strava_id']),
                              activity_type=str(t['activity_type']),
                              training_type=str(t['training_type']),
                              ))

        print("  Bikes")
        for t in [t for t in data['equipments'] if t['type'] == 'bike']:
            print(line.format(id=str(t['velohero_id']),
                              name=str(t['name']),
                              strava_id=str(t['strava_id']),
                              activity_type=str(t['activity_type']),
                              training_type=str(t['training_type']),
                              ))

        print("  Unspecified")
        for t in [t for t in data['equipments'] if t['type'] is None]:
            print(line.format(id=str(t['velohero_id']),
                              name=str(t['name']),
                              strava_id=str(t['strava_id']),
                              activity_type=str(t['activity_type']),
                              training_type=str(t['training_type']),
                              ))
    else:
        "Training Types not set. Use 'reload' to fill data.py"


def find_training_type_by_name(text):
    """
    Try to find the type by a (sub-) string.
    :param: text
    :return: S
    """
    hits = []
    regex = re.compile("^" + text.strip() + ".*", re.IGNORECASE)
    for t in [t for t in read_masterdata()['types'] if regex.match(t['name'])]:
        hits.append(t['name'])

    if len(hits) == 0:
        exit_on_error("Training Type input doesn't match. Use 'heroscript masterdata --list' to list all training types.")

    if len(hits) > 1:
        exit_on_error(f"Training Type input not unique, found: {hits}")

    return hits[0]


def process_masterdata(args):

    if args.list:
        _do_list()
    elif args.validate:
        pass
    elif args.refresh:
        _do_refresh()
    else:
        _do_list()


def _merge_equipments(velohero_dict, strava_dict):

    ret = []

    strava_count = len(strava_dict)

    for v in velohero_dict:
        # Compare non-case sensitive, ignore spaces. Velo's name must be a substring from STRAVA's name
        regex = re.compile(".*" + v['name'].replace(" ", "") + ".*", re.IGNORECASE)
        stravas = [s for s in strava_dict if regex.match(s['name'].replace(" ",""))]

        if len(stravas) > 0:
            strava_count -= 1
            ret.append(dict(
                name=v['name'],
                type=stravas[0]['type'],
                velohero_id=v['velohero_id'],
                strava_id=stravas[0]['id'],
                activity_type=stravas[0]['activity_type'],
                training_type=stravas[0]['training_type'],
            ))

            log("Mapped with Strava", f"{v['name']}=={stravas[0]['name']}")

        else:

            ret.append(dict(
                name=v['name'],
                type=None,
                velohero_id=v['velohero_id'],
                strava_id=None,
                activity_type=None,
                training_type=None,
            ))

            log("Velohero only", v)

    if (strava_count==0):
        print("Mapped all ({equi}) Velohero's to Strava's equipments by name.".format(equi=len(ret)))
    else:
        print("Mapped {equi} equipments by name.  But {stravas} Strava equipments could not be mapped:"
              .format(equi=len(ret), stravas=strava_count))
        for s in strava_dict:
            if len([r for r in ret if r['strava_id'] == s['id']]) == 0:
                print(f"  - Missing in Velohero: '{s['name']}'")


    return ret


def _tag_types(types):

    for v in types:
        if v['name'].lower() == 'competition' or v['name'].lower() == 'wettkampf':
            v['tag'] = 'competition'

        elif v['name'].lower() == 'commute' or v['name'].lower() == 'pendel':
            v['tag'] = 'commute'

        elif v['name'].lower() == 'rolle' or v['name'].lower() == 'indoor':
            v['tag'] = 'indoor'

        elif v['name'].lower() == 'training':
            v['tag'] = 'ignore'

        else:
            v['tag'] = 'default'


def _do_refresh():
    log("_refresh_data", "started")

    print("Collecting data from Velohero..", end='', flush=True)
    velohero_dict = velohero.velohero_process_get_masterdata()
    print("done! From Strava..", end='', flush=True)
    strava_dicts = strava.strava_process_get_masterdata()
    print("done!  ")

    equipments = _merge_equipments(velohero_dict['equipments'], strava_dicts)

    data = read_masterdata()

    data['types'] = velohero_dict['types']
    data['equipments'] = equipments

    _save(data)


def init_masterdata_storage():
    """
    Check and sanatize the persisted config data.py
    Call this every time, config logic has changed, e.g. in startup (after a new script version).
    """
    log("init_data", "start")

    storage = Storage()

    if not storage.get_data_path().exists():
        print("Data file not found, create it now: {}. To load master data.py, call 'heroscript data.py --refresh."
              .format(storage.get_data_path().absolute()))
        # Create new config and initialize it with default values
        _save(dict())


def _save(data):
    storage = Storage()
    file = storage.get_data_path()
    # log("file_name", file)

    with file.open('wb') as file:
        pickle.dump(data, file)





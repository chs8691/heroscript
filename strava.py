# Public apps client ID from https://www.strava.com/settings/api
import datetime
import re
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

import stravalib

import config
import utility
from config import key_port, key_strava_client_id, key_strava_client_secret, save_item, \
    key_strava_access_token, key_strava_refresh_token, key_strava_expired_at, get_config, read_config
import masterdata
from load import read_load, save_load
from utility import log, is_commute_training_type, is_indoor_training_type, log_switch, exit_on_error

host_name = "localhost"

# Private apps client secret from https://www.strava.com/settings/api
strava_client_code = None

# Will be set by server response /autorized with a valid code or with "", if permission not granted.
threaded_authorize_code = None

strava_workout_run_competition_type = "1"
strava_workout_bicycle_competition_type = "11"


class MyRequestHandler(BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)
        self.log = log_switch

    def create_404(self, message):

        self.send_response(404)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        self.wfile.write(bytes("<html><head><title>404</title></head>", "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes(f"<p>{message}'</p>", "utf-8"))

        log("[ERROR] 404 for: ", message)

        self.wfile.write(bytes("</body></html>", "utf-8"))

    def handle_authorize(self):
        query = parse_qs(urlparse(self.path).query)
        if 'code' not in query:
            self.create_404("Unexpected request from STRAVA: Expected value 'code' not found, but should be part "
                            "of the query string")
            log("[ERROR]", "Missing 'code' found in redirected request.")
            return

        log("query", query)

        global threaded_authorize_code

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        self.wfile.write(bytes("<html><head><title>Authorized</title></head>", "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))

        if not "activity:write" in query['scope'][0]:
            self.wfile.write(
                bytes("<h3>Upps, you have authorized Heroscript for read access but not for activity write access.</h3>"
                      "<p>You will need activity <b>write access</b> for transfer data.py to STRAVA. If you will not transfer updates to STRAVA, this is OK. "
                      "<p>But if you want to use the full power of Heroscript, you have to allow write access. "
                      "In this case just use '<b>heroscript config --strava_reset</b>' to request the STRAVA authorize page the next time.</p>"
                      "<p>Thank you for using Heroscript. You can close this window now.</p>", "utf-8"))

        else:
            self.wfile.write(
                bytes("<h3>Thank you</h3>"
                      "<p>Well done, you have authorized Heroscript. If you now longer want to use heroscript, "
                      "you can revoke this at any time in your STRAVA settings.</p>"
                      "<p>Thank you for using Heroscript. You can close this window now.</p>", "utf-8"))

        log("code", query['code'][0])
        threaded_authorize_code = query['code'][0]

        self.wfile.write(bytes("</body></html>", "utf-8"))

    def do_GET(self):
        path = urlparse(self.path).path
        log("path", path)
        if path == '/authorize':
            self.handle_authorize()
        else:
            self.create_404(f"Uuups, Page '{path}' not found! Sorry, but something went wrong.")

    def log(self, label, value):
        if self.log:
            print(f"{label}: {value}")


def load_strava_activity():
    """
    Precondition: Load is staged.
    """
    # log("load_strava_activity", "start")

    try:

        client = _setup_client()
        load = read_load()

        log("Searching for an activity at", load.started_at)

        # client.get_activity(1).tr

        for a in client.get_activities(
                after=load.started_at_datetime + datetime.timedelta(seconds=-1),
                before=load.started_at_datetime + datetime.timedelta(seconds=1)):
            log(f"Found STRAVA activity: started at={a.start_date}, "
                f"name='{a.name}' ID", f"'{a.id}', commute={a.commute}, trainer={a.trainer}, "
                                       f"workout type={a.workout_type}")

            if len(a.name.split(": ", 1)) == 2:
                title = a.name.split(": ", 1)[1]
            else:
                title = a.name

            if a.commute:
                type = masterdata.get_commute_type()

            elif a.trainer:
                type = masterdata.get_indoor_type()

            # Type decorates the name as prefix
            elif re.compile(".*: .*").match(a.name):
                type = masterdata.find_type_by_name(a.name.split(": ", 1)[0])

            # Run or bike competition
            elif a.workout_type == strava_workout_run_competition_type or \
                    a.workout_type == strava_workout_bicycle_competition_type:
                type = masterdata.get_competition_type()

            # Strava doesn't have a type
            else:
                type = masterdata.get_default_type()

            log("Detected STRAVA activity type",type['name'])

            equipment_name = None
            if a.gear_id:
                log("gear_id", a.gear_id)
                equipment = masterdata.find_equipment_by_strava_id(a.gear_id)
                if equipment is None:
                    print(f"[WARN] STRAVA equipment with ID {a.gear_id} not found ! To update master data use "
                          f"'masterdata --refresh'")
                else:
                    equipment_name = equipment['name']
            else:
                print("[WARN] STRAVA activity hasn't got a equipment")

            myconfig = config.get_strava_description_items()

            descriptions = []

            log("a.distance", f"{a.distance.num} {a.distance.unit}")
            log("a.total_elevation_gain", f"{a.total_elevation_gain.num} {a.total_elevation_gain.unit}")
            elevation = a.total_elevation_gain.num / (a.distance.num / 1000)
            descriptions.append("\u25B2 {elevation:.1f} {unit1}/k{unit2}"
                                .format(elevation=elevation, unit1=a.total_elevation_gain.unit, unit2=a.distance.unit))

            for item in myconfig:
                log("description rule", item)
                if item['condition_field'] == 'strava.name':
                    if item['condition_value'].lower().strip() == title.lower().strip():
                        descriptions.append(item['text'])

                if item['condition_field'] == 'training_type':
                    if item['condition_value'].lower().strip() == type['name'].lower():
                        descriptions.append(item['text'])

            descriptions.append("Powered by https://github.com/chs8691/heroscript")

            log("descriptions", descriptions)

            load.add_strava(a.id, a.name, type['name'], title, equipment_name, descriptions,
                            masterdata.find_activity_type_by_equipment(equipment_name))

            save_load(load)
            print(f"Found activity on Strava")
            return

        print("[WARN] Strava activity not found !")

    except stravalib.exc.AccessUnauthorized as e:
        log("Exception occurred", e)
        exit_on_error(
            f"STRAVA access failed: Unauthorized. Maybe you have removed the app permission in your STRAVA profile!? "
            "Use 'heroscript config --strava_reset' to remove all login data.py. Then try the command again and you "
            "will be askt for app authorization.")


def strava_do_update():
    """
    Precondition: In Load there is the STRAVA activity ID
    """
    print("Updating STRAVA...", end='', flush=True)

    messages = []

    try:

        client = _setup_client()
        load = read_load()
        type = masterdata.get_type(load.training_type)['name']

        if type == masterdata.get_competition_type()['name']:
            messages.append(("[WARN] Can't set the STRAVA workout type to 'competition', please do this manually "
                  "(missing this feature in stravalib API)"))

        if load.strava_descriptions is None:
            description = None
        else:
            description = "\n".join(load.strava_descriptions)

        log("description", description)

        if len(load.equipment_names) == 9:

            messages.append("[WARN] No equipment in stage, equipment on Strava will not be be updated")

            client.update_activity(activity_id=load.strava_activity_id,
                                   name=load.strava_activity_name,
                                   commute=is_commute_training_type(type),
                                   trainer=is_indoor_training_type(type),
                                   description=description,
                                   )

        else:
            equipment = masterdata.find_first_strava_equipment(load.equipment_names)

            if equipment is None:
                messages.append("No equipment with Strava ID found! Are the master data up-to-date "
                                "(use 'masterdata --refresh' to update)? ")
                gear_id = False
            else:
                gear_id = equipment['strava_id']
                log("Take equipment ID", f"{equipment['strava_id']} '{equipment['name']}'")

            # There can ve prints inside, so print afterwards
            client.update_activity(activity_id=load.strava_activity_id,
                                   name=load.strava_activity_name,
                                   commute=is_commute_training_type(type),
                                   trainer=is_indoor_training_type(type),
                                   gear_id=gear_id,
                                   description=description,
                                   )

        for message in messages:
            print(message)

        print(f" Done (Activity ID {load.strava_activity_id} updated)")

    except stravalib.exc.AccessUnauthorized as e:
        log("Exception occurred", e)
        exit_on_error(
            f"STRAVA access failed: Unauthorized. Maybe you have removed the app permission in your STRAVA profile!? "
            "Use 'heroscript config --strava_reset' to remove all login data.py. Then try the command again and you "
            "will be askt for app authorization.")


def _get_training_type(gear):
    regex = re.compile(".*heroscript\.training_type=\'(.*)\'.*")

    types = masterdata.get_types()

    log("gear.description", gear.description)
    if regex.match(gear.description):
        type = regex.match(gear.description).group(1).strip().lower()
        log("Strava", f"Found training type {type} in gear {gear.name}")
        if type.lower() in [t.lower() for t in types]:
            return [t for t in types if t.lower() == type.lower() ][0]
        else:
            exit_on_error(f"Gear {gear.name}: Unknown training type '{type}'. "
                          f"Please update your Strava equipment description with heroscript.training_type="
                          f"'{types}'")


def _get_activity_type(gear):
    """
    Maps strava gear to a heroscript activity type. First try is to findin the description heroscript.activity_type='..'.
    If not found, the activity type will be set by frame type (for bikes) and 'run' for shoes.
    :param gear: Shoe or Bike
    :return: item from utility.activity_type_list
    :exception: Mapping failed
    """

    regex_activity_type = re.compile(".*heroscript\.activity_type=\'(.*)\'.*")

    log("gear.description", gear.description)
    if regex_activity_type.match(gear.description):
        activity_type = regex_activity_type.match(gear.description).group(1).strip().lower()
        log("Strava", f"Found activity type {activity_type} in gear {gear.name}")
        if activity_type in utility.activity_type_list:
            return activity_type
        else:
            exit_on_error(f"Gear {gear.name}: Unknown activity type '{activity_type}'. "
                          f"Please update your Strava equipment description with heroscript.activity_type='{utility.activity_type_list}'")

    # Only bikes have a frame type
    if hasattr(gear, 'frame_type'):

        # MTB
        if gear.frame_type == 1:
            return utility.activity_type_mtb

        # Cross Bike
        elif gear.frame_type == 2:
            return utility.activity_type_roadbike

        # Race Bike
        elif gear.frame_type == 3:
            return utility.activity_type_roadbike

        # Triathlon Bike
        elif gear.frame_type == 4:
            return utility.activity_type_roadbike

        else:
            exit_on_error(f"Bike '{gear.name}' (ID={gear.id}) has an unknown frame type '{gear.frame_type}'. "
                          "You have to edit this Equipment in Strava.")

    # Shoe
    else:
        # In der Schuh-Beschreibung einen Text z.B. activity_type='hiking' aber auch heroscript._type='roadbike'
        return utility.activity_type_run


def strava_process_get_masterdata():
    """
    Load master data.py from strava
    :returns: List with dictionary of keys id, name, type. Type can have tow values 'shoe' or 'bike'
    """

    ret = []

    client = _setup_client()

    for shoe in client.get_athlete().shoes:
        log("shoe", shoe)
        gear = client.get_gear(shoe.id)
        ret.append(dict(
            id=shoe.id,
            name=shoe.name,
            type='shoe',
            activity_type=_get_activity_type(gear),
            training_type=_get_training_type(gear),
        ))

    for bike in client.get_athlete().bikes:
        log("bike", bike)
        gear = client.get_gear(bike.id)
        ret.append(dict(
            id=bike.id,
            name=bike.name,
            type='bike',
            activity_type=_get_activity_type(gear),
            training_type=_get_training_type(gear),
        ))

    log("Got master data from STRAVA", ret)

    return ret


def _start_server():
    """
    To be run in a thread
    """

    if log_switch:
        print("LOG Starting server {}:{}...".format(host_name, get_config(key_port)))

    myServer = HTTPServer((host_name, int(get_config(key_port))), MyRequestHandler)
    myServer.serve_forever()


def _new_token():
    """
    Exchanges outdated token
    """
    log("_new_token", "start")
    client = stravalib.Client()

    _obtain_new_token(lambda token: client.refresh_access_token(get_config(key_strava_client_id),
                                                                get_config(key_strava_client_secret),
                                                                token),
                      get_config(key_strava_refresh_token))

    log("_new_token", "end")


def _setup_client():
    """
    If not proper authorized, do it. Otherwise just return the client, ready to use.
    :return: Client object
    """

    # For the very first time or after config --strava_reset
    if key_strava_expired_at not in read_config() or not get_config(key_strava_expired_at) \
            or key_strava_access_token not in read_config() or not get_config(key_strava_access_token) \
            or key_strava_refresh_token not in read_config() or not get_config(key_strava_refresh_token):
        _authorize_app()

    # An access_token is only valid for 6 hours
    if get_config(key_strava_expired_at) < round(time.time()):
        _new_token()

    client = stravalib.Client()
    client.access_token = get_config(key_strava_access_token)
    client.refresh_token = get_config(key_strava_refresh_token)
    client.token_exired_at = get_config(key_strava_expired_at)

    return client


def _authorize_app():
    log("_authorize_app", "start")

    dameon = threading.Thread(name='herscript-server', target=_start_server)
    dameon.setDaemon(True)

    dameon.start()

    client = stravalib.Client()
    url = client.authorization_url(client_id=get_config(key_strava_client_id),
                                   redirect_uri='http://{}:{}/authorize'.format(host_name, get_config(key_port)),
                                   scope=['profile:read_all', 'activity:write', 'activity:read', 'activity:read_all'])

    # url = "https://www.strava.com/oauth/authorize?client_id={client_id}"\
    #       "&redirect_uri=http://{host_name}:{port}"\
    #       "&response_type=code"\
    #       "&approval_prompt=auto"\
    #       "&scope=activity:write,read".format(client_id="43527", host_name=host_name, port=port)
    #
    log("url", url)
    print("Starting webbrowser, please authorize heroscript for STRAVA access.")
    #   No glue, why this doesn't work with chromium (no redirection, but normal login)
    webbrowser.get('firefox').open_new(url)
    log("webbrowser", "called")

    i = 10
    print(f"Waiting {i} sec for your authorization: {i:2}", end="", flush=True)
    while i >= 0 and threaded_authorize_code is None:

        i -= 1
        print(f"\b\b{i:2}", end="", flush=True)
        # if authorize_code is None:
        if i == 0:
            exit_on_error("\nTimeout, authorization failed !")
        else:
            time.sleep(1)

    print("")
    if threaded_authorize_code is None:
        exit_on_error("Timeout, Authorization failed.")
    else:
        print("Done.")

    log("Go on now with code", threaded_authorize_code)

    if not key_strava_client_id in read_config():
        exit_on_error(
            "STRAVA client ID not set. Set it with: heroscript config --strava_client_id ID-OF-YOUR-API")

    if not key_strava_client_secret in read_config():
        exit_on_error(
            "STRAVA client secret not set. Set it with: heroscript config --strava_client_secret SECRET-OF-YOUR-API")

    _obtain_new_token(lambda token: client.exchange_code_for_token(client_id=get_config(key_strava_client_id),
                                                                   client_secret=get_config(key_strava_client_secret),
                                                                   code=token),
                      threaded_authorize_code)

    log("_authorize_app", "end")


def _obtain_new_token(func, token):
    """
    Call STRAVA for getting new access token. There are two different methods for that in the STRAVA Client API. Either
    while app authorization and for an expired token.
    :param func: Either client.exchange_code_for_token() or client.refresh_access_token()
    :param token: Either the authorize_token or the request_token.
    """
    token_response = None
    try:
        token_response = func(token)

    # While authorization
    except stravalib.exc.AccessUnauthorized as e:
        log("stravalib.exc.AccessUnauthorized", e)
        exit_on_error("Unauthorized")

    # While reqest expired token
    except stravalib.exc.Fault as e:
        log("stravalib.exc.Fault", e)
        exit_on_error("Obtaining new STRAVA token failed")

    if not 'access_token' in token_response:
        exit_on_error("Unexpected Response: Didn't got the access_toke from STRAVA.")

    if not 'refresh_token' in token_response:
        exit_on_error("Unexpected Response: Didn't got the refresh_token from STRAVA.")

    if not 'expires_at' in token_response:
        utility.exit_on_error("Unexpected Response: Didn't got the expires_at from STRAVA.")

    save_item(key_strava_access_token, token_response['access_token'])
    save_item(key_strava_refresh_token, token_response['refresh_token'])
    save_item(key_strava_expired_at, token_response['expires_at'])

    log("access_token", token_response['access_token'])
    log("refresh_token", token_response['refresh_token'])
    log("expires_at", token_response['expires_at'])

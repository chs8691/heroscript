import argparse
from sys import argv
from pathlib import Path as pathlib_Path
from os import path
import re
import json
import requests as requests
from lxml import html
from html import unescape

args = None

# Filled with ID for SSO login
sso_id = None

# Constant with file name in the users directory
rc_file = ".veloherorc"

# User-Agent string
my_user_agent = "veloheroup/1.0"


def execute_upload():
    log("execute_upload", "start")
    check_sso_login()

    activity_id = -1
    if args.file:
        activity_id = do_upload(args.file)

    log("upload", "end")


def execute_set():
    """
    Update existing workout
    """
    log("execute_set", "start")
    check_sso_login()

    tree = load_workout_data(args.activity_id)

    # Init all field with old data
    workout_date = get_simple_input(tree, 'workout_date')['value']
    workout_start_time = get_simple_input(tree, 'workout_start_time')['value']
    workout_dist_km = get_simple_input(tree, 'workout_dist_km')['value']
    workout_asc_m = get_simple_input(tree, 'workout_asc_m')['value']
    workout_dur_time = get_simple_input(tree, 'workout_dur_time')['value']
    sport_id = get_select_values_value(tree, 'sport_id')
    type_id = get_select_values_value(tree, 'type_id')
    workout_dsc_m = get_simple_input(tree, 'workout_dsc_m')['value']
    workout_alt_min_m = get_simple_input(tree, 'workout_alt_min_m')['value']
    workout_alt_max_m = get_simple_input(tree, 'workout_alt_max_m')['value']
    workout_spd_avg_kph = get_simple_input(tree, 'workout_spd_avg_kph')['value']
    workout_spd_max_kph = get_simple_input(tree, 'workout_spd_max_kph')['value']
    workout_hr_avg_bpm = get_simple_input(tree, 'workout_hr_avg_bpm')['value']
    workout_hr_max_bpm = get_simple_input(tree, 'workout_hr_max_bpm')['value']
    workout_comment = get_textarea(tree, 'workout_comment')['value']

    log('Actual data', ":")
    log('workout_date', workout_date)
    log('workout_start_time', workout_start_time)
    log('workout_dist_km', workout_dist_km)
    log('workout_asc_m', workout_asc_m)
    log('workout_dur_time', workout_dur_time)
    log('sport_id', sport_id)
    log('type_id', type_id)
    log('workout_dsc_m', workout_dsc_m)
    log('workout_alt_min_m', workout_alt_min_m)
    log('workout_alt_max_m', workout_alt_max_m)
    log('workout_spd_avg_kph', workout_spd_avg_kph)
    log('workout_spd_max_kph', workout_spd_max_kph)
    log('workout_hr_avg_bpm', workout_hr_avg_bpm)
    log('workout_hr_max_bpm', workout_hr_max_bpm)
    log('workout_comment', workout_comment)

    # Options
    sport_id_dict = get_select_values(tree, 'sport_id')
    type_id_dict = get_select_values(tree, 'type_id')

    log('sport_id_dict', sport_id_dict)
    log('type_id_dict', type_id_dict)

    # Update fields
    if args.workout_date:
        workout_date = args.workout_date
    if args.workout_start_time:
        workout_start_time = args.workout_start_time
    if args.workout_dist_km:
        workout_dist_km = args.workout_dist_km
    if args.workout_asc_m:
        workout_asc_m = args.workout_asc_m
    if args.workout_dur_time:
        workout_dur_time = args.workout_dur_time
    if args.sport_id:
        sport_id = get_selected_id(sport_id_dict, args.sport_id)
    if args.type_id:
        type_id = get_selected_id(type_id_dict, args.type_id)
    if args.workout_dsc_m:
        workout_dsc_m = args.workout_dsc_m
    if args.workout_alt_min_m:
        workout_alt_min_m = args.workout_alt_min_m
    if args.workout_alt_max_m:
        workout_alt_max_m = args.workout_alt_max_m
    if args.workout_spd_avg_kph:
        workout_spd_avg_kph = args.workout_spd_avg_kph
    if args.workout_spd_max_kph:
        workout_spd_max_kph = args.workout_spd_max_kph
    if args.workout_hr_avg_bpm:
        workout_hr_avg_bpm = args.workout_hr_avg_bpm
    if args.workout_hr_max_bpm:
        workout_hr_max_bpm = args.workout_hr_max_bpm
    if args.workout_comment:
        workout_comment = args.workout_comment

    log('New data', ":")
    log('workout_date', workout_date)
    log('workout_start_time', workout_start_time)
    log('workout_dist_km', workout_dist_km)
    log('workout_asc_m', workout_asc_m)
    log('workout_dur_time', workout_dur_time)
    log('sport_id', sport_id)
    log('type_id', type_id)
    log('workout_dsc_m', workout_dsc_m)
    log('workout_alt_min_m', workout_alt_min_m)
    log('workout_alt_max_m', workout_alt_max_m)
    log('workout_spd_avg_kph', workout_spd_avg_kph)
    log('workout_spd_max_kph', workout_spd_max_kph)
    log('workout_hr_avg_bpm', workout_hr_avg_bpm)
    log('workout_hr_max_bpm', workout_hr_max_bpm)
    log('workout_comment', workout_comment)

    url = "https://app.velohero.com/workouts/edit/{}".format(args.activity_id)
    log("url", str(url))

    # Must contains all workout fields
    r = requests.post(url,
                      headers={
                          'user-agent': my_user_agent,
                      },
                      data={
                          'sso': sso_id,
                          'submit': '1',
                          'workout_date': workout_date,
                          'workout_start_time': workout_start_time,
                          'workout_dist_km': workout_dist_km,
                          'workout_asc_m': workout_asc_m,
                          'workout_dur_time': workout_dur_time,
                          'sport_id': sport_id,
                          'type_id': type_id,
                          'workout_dsc_m': workout_dsc_m,
                          'workout_alt_min_m': workout_alt_min_m,
                          'workout_alt_max_m': workout_alt_max_m,
                          'workout_spd_avg_kph': workout_spd_avg_kph,
                          'workout_spd_max_kph': workout_spd_max_kph,
                          'workout_hr_avg_bpm': workout_hr_avg_bpm,
                          'workout_hr_max_bpm': workout_hr_max_bpm,
                          'workout_comment': workout_comment,
                          # 'equipment_ids': ['17481', '3793'],
                      })

    if r.status_code != 200:
        exit_on_rc_error("HTTP error for {}".format(url), r.status_code)

    # log("response", str(r.text))

    log("set", "done")


def get_selected_id(select_dict, value):
    """
    Exits script, if value is invalid
    :param select_dict: Dictionary which describes the data
    :param value: id or description
    :return: id or, in inital case, empty string
    """
    if value.isdigit():
        key = 'id'
        log('res is digit', value)
    else:
        key = 'description'

    try:
        res = [v for v in select_dict['values'] if v[key] == value][0]['id']
        log('res', res)
        return res
    except IndexError:
        exit_on_rc_error("Unknown value", value)


def execute_show():
    log("execute_show", "start")
    check_sso_login()

    tree = load_workout_data(args.activity_id)
    # log("response", str(r.text))

    print_simple_input(tree, 'workout_date')
    print_simple_input(tree, 'workout_start_time')
    print_simple_input(tree, 'workout_dist_km')
    print_simple_input(tree, 'workout_asc_m')
    print_simple_input(tree, 'workout_dur_time')
    print_simple_input(tree, 'workout_dsc_m')
    print_simple_input(tree, 'workout_alt_min_m')
    print_simple_input(tree, 'workout_alt_max_m')
    print_simple_input(tree, 'workout_spd_avg_kph')
    print_simple_input(tree, 'workout_spd_max_kph')
    print_simple_input(tree, 'workout_hr_avg_bpm')
    print_simple_input(tree, 'workout_hr_max_bpm')
    print_textarea(tree, 'workout_comment')

    print("")
    print_select_values(tree, "sport_id")
    print("")
    print_select_values(tree, "type_id")
    print("")
    print_select_values(tree, "equipment_ids")


def load_workout_data(workload_id):
    """
    Requests the workload for the given ID. Precondition: SSO established
    Returns HTML tree
    """
    log("load_workload_data", "start")

    # just for for testing
    # return html.parse(open('workout.html', 'rt')).getroot()

    url = "https://app.velohero.com/workouts/edit/{}".format(workload_id)
    log("url", str(url))
    r = requests.post(url,
                      headers={
                          'user-agent': my_user_agent,
                      },
                      data={
                          'sso': sso_id,
                      })

    if r.status_code != 200:
        exit_on_rc_error("HTTP error {} for {}".format(url, r.status_code))

    return html.fromstring(r.text)


def get_select_values_value(tree, name):
    """
    Returns only the value of a select field
    :return: Value or empty string
    """
    values = [v for v in get_select_values(tree, name)['values'] if v['selected']]

    if len(values) == 0:
        return ""
    else:
        return values[0]['id']


def get_select_values(tree, name):
    """
    Returns dictionary with id, value, description, for instance
            dict=(id='sport_id',
                  description='Sportart',
                  values=[(id=1, description='Radsport', selectecd=True),
                        id=6, description='Mountainbike', selected=False),
                        ...
                      ]),

    """

    try:

        element = tree.xpath("//select[@id='%s']" % name)[0]

        label_elements = tree.xpath("//label[@for='%s']" % name)

        # Proper HTML: label has a for attribute
        if len(label_elements) > 0:
            label = label_elements[0].text

        # Just for 'Material' / equipment_ids:
        else:
            label = element.getparent().getparent()[0].text

        ret = dict(id=element.name,
                   description=label,
                   values=[])

        # exclude empty item
        for option in [o for o in element if len(o.get('value')) > 0]:
            if option.get('selected'):
                # log('selected', "True")
                selected = True
            else:
                # log('selected', "False")
                selected = False

            ret['values'].append(dict(id=option.get('value'),
                                      description=option.text,
                                      selected=selected))

    except IndexError as e:
        exit_on_rc_error("Element '%s' error: %s " % (name, e))

    return ret


def get_textarea(tree, name):
    """
    Returns dictionary with id, value, description
    """
    log('get_text_area', str(name))
    try:

        label = tree.xpath("//label[@for='%s']" % name)[0].text
        # label inside formatting element, e.g. <span>
        if label is None:
            label = tree.xpath("//label[@for='%s']" % name)[0][0].text

        # log('label', label)
        # log('textarea', str(tree.xpath("//textarea[@id='%s']" % name)[0].value))

        element = tree.xpath("//textarea[@id='%s']" % name)[0]

        # log('element.name', element.name)
        # log('element.value', element.value)

        ret = dict(id=element.name,
                   value=element.value,
                   description=label,
                   )
        # log("get_simple_input ret=", ret)
        return ret

    except IndexError:
        exit_on_rc_error("Element not found: '%s'" % name)


def get_simple_input(tree, name):
    """
    Returns dictionary with id, value, description
    """
    # log('get_simple_input', str(name))
    try:

        label = tree.xpath("//label[@for='%s']" % name)[0].text
        # label inside formatting element, e.g. <span>
        if label is None:
            label = tree.xpath("//label[@for='%s']" % name)[0][0].text

        # log('label', label)

        element = tree.xpath("//input[@id='%s']" % name)[0]

        # log('element', element)

        ret = dict(id=element.name,
                   value=element.value,
                   description=label,
                   )
        # log("get_simple_input ret=", ret)
        return ret

    except IndexError:
        exit_on_rc_error("Element not found: '%s'" % name)


def print_select_values(tree, name):
    data = get_select_values(tree, name)
    print("%s '%s':" % (data['id'], data['description']))

    for option in [o for o in data['values'] if o['id'] is not None]:
        if option['selected'] is True:
            print(">>> %s (%s) <<< SELECTED" % (option['description'], option['id']))
        else:
            print("    %s (%s)" % (option['description'], option['id']))


def print_simple_input(tree, name):
    # log('print_simple_input', str(name))
    data = get_simple_input(tree, name)

    print("%s '%s' = %s" % (data['id'], data['description'], data['value']))


def print_textarea(tree, name):
    log('print_text_area', str(name))
    data = get_textarea(tree, name)

    print("%s '%s' = %s" % (data['id'], data['description'], data['value']))


def parse_args():
    """
    Examples:
        Show info of an activity file:
            main.py info --file=20191221-150315-activity_4355570485.tcx
            main.py info --directory=/home/chris/newActivities

        Upload an activity file and set an attribute:
            main.py upload --file=20191221-150315-activity_4355570485.tcx --sport_id='Mountainbike'

        Pick next file from a directory, upload and set value:
            main.py upload --directory=/home/chris/newActivities --sport_id='Mountainbike'

        Show activity's attributes:
            main.py show --id=4075724

        Update attribute of an an existing activity:
            main.py set --id=4075724 --sport_id=Mountainbike

    """
    global args

    parser = argparse.ArgumentParser(description="Upload activities to velohero an set proper attributes.")

    parser.add_argument("-l", "--log",
                        action='store_true',
                        help="Print log to the console")

    sub_parsers = parser.add_subparsers()

    # ######### upload #########
    upload_parser = sub_parsers.add_parser('upload', help="Upload activity file to velohero")

    upload_parser.add_argument("-f", "--file",
                               required=True,
                               help="Name (path) to the track file to upload")

    upload_parser.set_defaults(func=execute_upload)

    # ######### show #########
    show_parser = sub_parsers.add_parser('show', help="Show existing activity in velohero")

    show_parser.add_argument("-i", "--activity_id",
                             required=True,
                             help="Velohero activity ID.")

    show_parser.set_defaults(func=execute_show)

    # ######### set #########
    set_parser = sub_parsers.add_parser('set', help="Set attributes for an existing activity")

    set_parser.add_argument("-i", "--activity_id",
                            required=True,
                            help="Velohero activity ID.. Example: '4075724'")

    set_parser.add_argument("-dist_km", "--workout_dist_km",
                            required=False,
                            help="Field 'workout_dist_km'. Example: '12345'")

    set_parser.add_argument("-asc_m", "--workout_asc_m",
                            required=False,
                            help="Field 'workout_asc_m'. Example: '1234'")

    set_parser.add_argument("-date", "--workout_date",
                            required=False,
                            help="Field 'workout_date'. Example: '31.12.2020'")

    set_parser.add_argument("-time", "--workout_start_time",
                            required=False,
                            help="Field 'workout_start_time'. Example: '17:59:00'")

    set_parser.add_argument("-dur", "--workout_dur_time",
                            required=False,
                            help="Field 'workout_dur_time'. Example: '2:23:00'")

    set_parser.add_argument("-sport", "--sport_id",
                            required=False,
                            help="Field 'sport_id'. Value can be id or description (case sensitive). "
                                 "Examples: '1', 'Mountainbike")

    set_parser.add_argument("-type", "--type_id",
                            required=False,
                            help="Field 'type_id'. Value can be id or description (case sensitive). "
                                 "Examples: '7431', 'Training")

    set_parser.add_argument("-dsc_m", "--workout_dsc_m",
                            required=False,
                            help="Field 'workout_dsc_m'. Example: '1234'")

    set_parser.add_argument("-alt_min_m", "--workout_alt_min_m",
                            required=False,
                            help="Field 'workout_alt_min_m'. Example: '100'")

    set_parser.add_argument("-alt_max_m", "--workout_alt_max_m",
                            required=False,
                            help="Field 'workout_alt_max_m'. Example: '1000'")

    set_parser.add_argument("-spd_avg_kph", "--workout_spd_avg_kph",
                            required=False,
                            help="Field 'workout_spd_avg_kph'. Example: '23.4'")

    set_parser.add_argument("-spd_max_kph", "--workout_spd_max_kph",
                            required=False,
                            help="Field 'workout_spd_max_kph'. Example: '45.6'")

    set_parser.add_argument("-hr_avg_bpm", "--workout_hr_avg_bpm",
                            required=False,
                            help="Field 'workout_hr_avg_bpm'. Example: '123'")

    set_parser.add_argument("-hr_max_bpm", "--workout_hr_max_bpm",
                            required=False,
                            help="Field 'workout_hr_max_bpm'. Example: '171'")

    set_parser.add_argument("-comment", "--workout_comment",
                            required=False,
                            help="Field 'workout_comment'. Example: 'Frist line '")

    set_parser.set_defaults(func=execute_set)

    args = parser.parse_args()

    if len(argv) < 2:
        exit_on_error("Use --help to show how to use {}".format(argv[0]))

    args.func()


def exit_on_rc_error(message, value):
    exit_on_error("{}: {}".format(message, value))


def exit_on_login_error(message, file_name):
    exit_on_error(("{}: {}\n"
                   "Make shure you have created this file in your home directory and it has read access.\n "
                   "Please go to https://app.velohero.com/sso and get yourself a private single sign-on key. "
                   "That's the long string.\n"
                   "Then create a file '{}' containing\n\n"
                   "----- snip -------------------------------------------------------------\n"
                   "VELOHERO_SSO_KEY=[insert your own]\n"
                   "----- snap -------------------------------------------------------------\n"
                   ).format(message, file_name, file_name))


def check_sso_login():
    log("check_sso_login", "begin")
    global sso_id

    file_name = path.join(str(pathlib_Path.home()), rc_file)

    if not path.exists(file_name):
        exit_on_login_error("File not found", file_name)

    log("found file", file_name)
    with open(file_name) as file:
        for line in file:
            matcher = re.match('^VELOHERO_SSO_KEY\\s*=\\s*(\\S+)\\s*', line, re.I)
            if matcher:
                sso_id = matcher.group(1)
                break

        if sso_id is None:
            exit_on_rc_error("Missing key=value entry", file_name)

    log("sso_id", sso_id)

    r = requests.post("https://app.velohero.com/sso", data={'sso': sso_id})

    # 200 Created
    if r.status_code == 200:
        log("Authentification successful", r.status_code)
        return

    # 403 Forbidden
    if r.status_code == 403:
        exit_on_error("Login forbidden - {}: ".format(r.status_code))
        return


def do_post_workout(file_name):
    """
    Send form data to an existing activity
    """
    log("do_post_workout", "begin")

    r = requests.post("https://app.velohero.com/upload/file",
                      headers={
                          'user-agent': my_user_agent,
                      },
                      data={
                          'sso': sso_id,
                          'view': "json",
                      })
    # log("request.headers", r.request.headers)
    # log("headers", r.headers)
    log("text", r.text)

    text = json.loads(r.text)
    # log("id", text["id"])

    # 200 Created
    if r.status_code == 200:
        log("Upload successful", r.status_code)
        log("Response", str(r))

        return json.loads(r.text)["id"]

    # 403 Forbidden
    if r.status_code == 403:
        exit_on_error("Login forbidden - {}: ".format(r.status_code))
        return False

    # Other error
    exit_on_error("HTTP error - {}: ".format(r.status_code))
    return False


def do_upload(file_name):
    """
    File must exist and of a valid type
    Returns Activity ID or False
    """
    log("upload file", file_name)

    with open(file_name, "rb") as file:
        # content = file.read()
        # log("content", content)
        r = requests.post("https://app.velohero.com/upload/file",
                          headers={
                              'user-agent': my_user_agent,
                          },
                          files={
                              'file': (file_name, file.read()),
                          },
                          data={
                              'sso': sso_id,
                              'view': "json",
                          })
        # log("request.headers", r.request.headers)
        # log("headers", r.headers)
        log("text", r.text)

        text = json.loads(r.text)
        # log("id", text["id"])

        # 200 Created
        if r.status_code == 200:
            log("Upload successful", r.status_code)
            log("Response", str(r))

            return json.loads(r.text)["id"]

        # 403 Forbidden
        if r.status_code == 403:
            exit_on_error("Login forbidden - {}: ".format(r.status_code))
            return False

        # Other error
        exit_on_error("HTTP error - {}: ".format(r.status_code))
        return False


def log(name, value):
    """
        Only switched on for development
    """
    if args.log:
        print("LOG {}={}".format(name, str(value)))


def exit_on_error(message):
    print(message)
    exit(1)


if __name__ == '__main__':
    parse_args()

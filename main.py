import argparse
from sys import argv
from pathlib import Path as pathlib_Path
from os import path
import re
import json
import requests as requests
from lxml import html

args = None

# Filled with ID for SSO login
sso_id = None

# Constant with file name in the users directory
rc_file = ".veloherorc"

# User-Agent string
my_user_agent = "veloheroup/1.0"


def upload():
    log("upload", "start")
    check_sso_login()

    activity_id = -1
    if args.file:
        activity_id = do_upload(args.file)

    log("upload", "end")


def show():
    log("show", "start")
    check_sso_login()

    url = "https://app.velohero.com/workouts/edit/{}".format(args.activity_id)
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

    tree = html.fromstring(r.text)
    # # log("response", str(r.text))
    #
    # # just for for testing
    # # tree = html.parse(open('workout.html', 'rt')).getroot()

    print_simple_input(tree, "workout_date")
    print_simple_input(tree, "workout_start_time")
    print_simple_input(tree, "workout_dur_time")
    print_simple_input(tree, "workout_dist_km")
    print_simple_input(tree, "workout_asc_m")
    print_simple_input(tree, "workout_spd_avg_kph")
    print("")
    print_select_values(tree, "sport_id")
    print("")
    print_select_values(tree, "type_id")
    print("")
    print_select_values(tree, "equipment_ids")


def print_select_values(tree, name):

    try:

        element = tree.xpath("//select[@id='%s']" % name)[0]

        label_elements = tree.xpath("//label[@for='%s']" % name)

        # Proper HTML: lable has a for attribute
        if len(label_elements) > 0:
            label = label_elements[0].text

        # Just for 'Material' / equipment_ids:
        else:
            label = element.getparent().getparent()[0].text

        selected_options = [o for o in element if not o.get('selected') is None]
        if len(selected_options) == 1:
            selected_option_text = selected_options[0].text
        else:
            selected_option_text = "---"

        print("%s '%s': %s" % (label, element.name, selected_option_text))

        for option in [o for o in element if len(o.get('value')) > 0]:
            if option.get('selected'):
                print(">>> %s: %s" % (option.get('value'), option.text))
            else:
                print("    %s: %s" % (option.get('value'), option.text))

    except IndexError as e:
        print("Element '%s' error: %s " % (name, e))


def print_simple_input(tree, name):

    try:

        label = tree.xpath("//label[@for='%s']" % name)[0].text
        # label inside formatting element, e.g. <span>
        if label is None:
            label = tree.xpath("//label[@for='%s']" % name)[0][0].text

        element = tree.xpath("//input[@id='%s']" % name)[0]

        print("%s '%s' = %s" % (label, element.name, element.value))
    except IndexError:
        print("Element not found: '%s'" % name)

def init_args():
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

    upload_parser = sub_parsers.add_parser('upload', help="Upload activity file to velohero")

    upload_parser.add_argument("-f", "--file",
                               required=True,
                               help="Name (path) to the track file to upload")

    upload_parser.set_defaults(func=upload)

    show_parser = sub_parsers.add_parser('set', help="Update existing activity in velohero")

    show_parser.add_argument("-i", "--activity_id",
                            required=True,
                            help="Velohero activity ID. No upload, just set the attributes for this activity")

    show_parser = sub_parsers.add_parser('show', help="Show attributes for an existing activity")

    show_parser.add_argument("-i", "--activity_id",
                            required=True,
                            help="Velohero activity ID.")

    show_parser.set_defaults(func=show)

    args = parser.parse_args()

    if len(argv) < 2:
        exit_on_error("Use --help to show how to use {}".format(argv[0]))

    args.func()


def exit_on_rc_error(message, file_name):
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
        exit_on_rc_error("File not found", file_name)

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
                              # 'file': file,
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
    init_args()

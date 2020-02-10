import datetime
import re
from os import path

log_switch = False


def set_log_switch(value):
    global log_switch
    log_switch = value

def warn(message):
    print("[warning] {}".format(str(message)))


def log(name, value):
    """
        Only switched on for development
    """
    if log_switch:
        print("LOG {}={}".format(name, str(value)))


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


def exit_on_error(message):
    print(message)
    exit(1)


def get_human_date(time_date, format):
    """
    Converts date/Time from track file into readable format. Must be start in format "YYYY-MM-DDT:MM:SS"
    :param time_date: e.g. "2019-12-21T14:03:15.000Z"
    :param format: e.g. "%y-%m-%d %H:%M" -->  '19-12-21 14:03'
    :return: Formatted String or original value
    """
    try:
        d = datetime.datetime.strptime(time_date[0:19], "%Y-%m-%dT%H:%M:%S")
        return d.strftime(format)

    except ValueError:
        return time_date


def resolve_path(directory, time):
    """
    Replace time variables and returns changed path. Supported place holder is {YYYY}
    :param directory: export root directory
    :param subdir: subdirectory, can have place holders.
    :param time: date-time-string, e.g. 20200131T072333.000Z, Must begin with YYYY
    :return: Updated dictionary string
    """
    ret = directory

    if re.compile(".*{YYYY}.*").match(ret):
        ret = ret.replace("{YYYY}", time[0:4])

    return ret
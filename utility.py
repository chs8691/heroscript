import datetime
import re

# Name of the download subdirectory for activity files
load_subdir = "in"

activity_type_run = 'run'
activity_type_mtb = 'mtb'
activity_type_roadbike = 'roadbike'
activity_type_fitness = 'fitness'
activity_type_hiking = 'hiking'

activity_type_list = [activity_type_run,
                      activity_type_mtb,
                      activity_type_roadbike,
                      activity_type_fitness,
                      activity_type_hiking,
                      ]

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


def is_indoor_training_type(training_type):
    """
    Checks if the (valid) training type is indoor (trainer, Rolle). Change this logic for your specific Velohero
    training types. There should only be one traning type for indoor trainer.
    :param training_type: String with type
    :return: true, if type is a indoor type, otherwise false
    """
    return training_type.lower() == 'rolle' or training_type.lower() == 'indoor' or training_type.lower() == 'trainer'


def is_commute_training_type(training_type):
    """
    Checks if the (valid) training type is a commute one (Commute, Pendel). Change this logic for your specific Velohero
    training types. There should only be one traning type for commutes.
    :param training_type: String with type
    :return: true, if type is the commute type, otherwise false
    """
    return training_type.lower() == 'pendel' or training_type.lower() == 'commute'


def is_competition_training_type(training_type):
    """
    Checks if the (valid) training type is a competition one (Commute, Pendel). Change this logic for your specific Velohero
    training types. There should only be one traning type for competitions.
    :param training_type: String with type
    :return: true, if type is the competition type, otherwise false
    """
    return training_type.lower() == 'wettkampf' or training_type.lower() == 'competition'


def is_default_training_type(training_type):
    """
    Checks if the (valid) training type is the default one. Change this logic for your specific Velohero
    training types. The default type has no special behavior and the STRAVA activity name will not be tagged.
    There should only be one traning type defined as default.
    :param training_type: String with type
    :return: true, if type is the default type, otherwise false
    """
    return training_type.lower() == 'training'


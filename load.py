import pickle
from datetime import datetime
from os import path

from storage import Storage
from tcxparser import TCXParser
from utility import log, exit_on_rc_error


class Stage:
    """
    Holds information about the actual loaded activity file
    """

    def __init__(self, file_name):
        self.file_name = file_name

        # Attributes that can be set. Every attribute has also its value from file
        self.original_activity_type = None

        # Must match argument --activity_type
        self.new_activity_type = None

        # Must match training_type name
        self.training_type = None

        # Must match route name (substring)
        self.route_name = None

        # Free text
        self.comment = None

        # Materials must match with their name
        self.equipment_names = None

        # Will be set with activity file. String like 2020-01-31T04:39:19.000Z
        self.started_at = None

        # Will be set with activity file. Is a datetime.datetime
        self.started_at_datetime = None

        # Ascent of workout in in the specified unit
        self.ascent = None

        # Descent of workout in in the specified unit
        self.descent = None

        # Highest altitude in in the specified unit
        self.altitude_max = None

        # Lowest altitude in the specified unit
        self.altitude_min = None

        # in Seconds
        self.duration = None

        # unit for all distance values
        self.distance_units = None

        # MM:SS in the specified unit
        self.pace = None

        # Float in e.g. km/h
        self.velocity_average = None

        # in the specified unit
        self.distance = None

        # Heart Rate average in s-1
        self.hr_average = None

        # Will be set with transfer
        self.velohero_workout_id = None

        # Will be set with transer
        self.archived_to = None

        # STRAVA fields will be set with add_strava
        self.strava_activity_id = None
        self.strava_activity_name = None

    def init_by_tcx(self, tcxparser):
        self.original_activity_type = tcxparser.activity_type
        self.started_at = tcxparser.started_at
        self.started_at_datetime = datetime.strptime(self.started_at[0:19], "%Y-%m-%dT%H:%M:%S")
        self.ascent = tcxparser.ascent
        self.descent = tcxparser.descent
        self.altitude_max = tcxparser.altitude_max
        self.altitude_min = tcxparser.altitude_min
        self.duration = tcxparser.duration
        self.distance_units = tcxparser.distance_units
        self.pace = tcxparser.pace
        self.velocity_average = tcxparser.velocity_average
        self.distance = tcxparser.distance
        self.hr_average = tcxparser.hr_avg

    def add_strava(self, id, name, type):
        """
        Add STRAVA data.py.
        :param id: STRAVA Activity ID as int
        :param name: Activity's name as String
        :param type: Extracted type name
        """
        self.strava_activity_id = id
        self.strava_activity_name = name
        self.training_type = type


    def distance_unit_abbreviation(self):
        """
        Short form the the distance/1000, e.g. km or kmi
        """
        if self.distance_units.lower() == "meters":
            return "m"
        if self.distance_units.lower() == "miles":
            return "mi"
        else:
            return self.distance_units[0:1]

    def set_activity_type(self, value):
        self.new_activity_type = value

    def set_training_type(self, value):
        self.training_type = value

    def set_route_name(self, value):
        self.route_name = value

    def set_comment(self, value):
        self.comment = value

    def set_equipment_names(self, values):
        self.equipment_names = values

    def set_strava_activity_name(self, name):
        self.strava_activity_name = name

    def set_velohero_workout_id(self, value):
        """
        Save ID or, init to None
        :param value: ID or None
        """
        self.velohero_workout_id = value

    def set_archived_to(self, value):
        """
        Path to archived file or None
        :param value: String with path or None
        """
        self.archived_to = value



def save_load(load):
    storage = Storage()
    file = storage.get_stage_path()
    log("file_name", file)

    filehandler = file.open('wb')
    pickle.dump(load, filehandler)


def read_load():
    """
    Returns the actual Stage
    :rtype: :class:`load.Stage`
    """
    storage = Storage()
    filehandler = storage.get_stage_path().open('rb')
    load = pickle.load(filehandler)
    return load


def create_load(file_name):
    """
    :param file_name: String with file path
    """
    log("do_input", "start")

    # Init a new load
    new_load = read_tcx(file_name)

    save_load(new_load)
    print("File loaded: %s" % file_name)

    log('original_activity_type', new_load.original_activity_type)

    log("do_input", "end")


def read_tcx(file_name):
    """
    Read TCX file grab some data.py
    :param file_name: TCX file name
    :return: instance of a Load
    """
    if not path.exists(file_name):
        exit_on_rc_error("File not found", file_name)

    load = Stage(file_name)

    tcxparser = TCXParser(file_name)
    load.init_by_tcx(tcxparser)

    return load
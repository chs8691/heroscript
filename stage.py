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

        # Must match training_type
        self.training_type = None

        # Must match route name (substring)
        self.route_name = None

        # Free text
        self.comment = None

        # Materials must match with their name
        self.equipment_names = None

        # Will be set with activity file
        self.started_at = None

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


    def init_by_tcx(self, tcxparser):
        self.original_activity_type = tcxparser.activity_type
        self.started_at = tcxparser.started_at
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


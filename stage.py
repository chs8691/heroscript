from utility import log


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

        # Will be set with update
        self.velohero_workout_id = None

    def set_tcx(self, tcxparser):
        self.original_activity_type = tcxparser.activity_type

    def set_velohero_workout_id(self, value):
        """
        Save ID or, init to None
        :param value: ID or None
        """
        self.velohero_workout_id = value

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



from pathlib import Path as pathlib_Path

from utility import log


class Storage():
    """
    All pickle stuff
    """

    def __init__(self):
        self.dir_name = '.heroscript'
        self.stage_file_name = 'stage'
        self.config_file_name = 'config'
        self.data_file_name = 'masterdata.py'
        my_path = pathlib_Path.home().joinpath(self.dir_name)

        if not my_path.exists():
            my_path.mkdir(parents=True, exist_ok=True)

    def get_stage_path(self):
        """
        Path to stage file
        :return: 
        """
        return pathlib_Path.home().joinpath(self.dir_name, self.stage_file_name)

    def get_config_path(self):
        """
        Path to config file
        :return: 
        """
        # log("get_config_path", "start")
        return pathlib_Path.home().joinpath(self.dir_name, self.config_file_name)

    def get_data_path(self):
        """
        Path to data.py file
        :return:
        """
        # log("get_config_path", "start")
        return pathlib_Path.home().joinpath(self.dir_name, self.data_file_name)





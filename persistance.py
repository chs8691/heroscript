from pathlib import Path as pathlib_Path
from os import path
from stage import Stage
from tcxparser import TCXParser
import pickle

from utility import log, exit_on_rc_error


def save_load(load):
    storage = Storage()
    file = storage.get_stage()
    log("file_name", file)

    filehandler = file.open('wb')
    pickle.dump(load, filehandler)


def read_load():
    storage = Storage()
    filehandler = storage.get_stage().open('rb')
    load = pickle.load(filehandler)
    return load


def create_load(file_name):
    """
    :param file_name: String with file path
    """
    log("do_input", "start")

    # Init a new load
    new_load = __read_tcx(file_name)

    save_load(new_load)
    print("File loaded: %s" % file_name)

    log('original_activity_type', new_load.original_activity_type)

    log("do_input", "end")


def __read_tcx(file_name):
    """
    Read TCX file grab some data
    :param file_name: TCX file name
    :return: instance of a Load
    """
    if not path.exists(file_name):
        exit_on_rc_error("File not found", file_name)

    load = Stage(file_name)

    tcxparser = TCXParser(file_name)
    load.init_by_tcx(tcxparser)

    return load


class Storage():
    """
    All pickle stuff
    """

    def __init__(self):
        self.dir_name = '.heroscript'
        self.stage_file_name = 'stage'
        self.config_file_name = 'config'
        my_path = pathlib_Path.home().joinpath(self.dir_name)

        if not my_path.exists():
            my_path.mkdir(parents=True, exist_ok=True)

    def get_stage(self):
        return pathlib_Path.home().joinpath(self.dir_name, self.stage_file_name)

    def get_config(self):
        return pathlib_Path.home().joinpath(self.dir_name, self.stage_file_name)

class Config():

    # def __init__(self):

    def read(self):
        storage = Storage()
        filehandler = storage.get_config().open('rb')
        load = pickle.load(filehandler)


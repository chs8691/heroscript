"""
Master Data. Are stored as dictionary:

"""
import pickle

from storage import Storage
from utility import exit_on_error, is_commute_training_type, is_indoor_training_type, is_competition_training_type, \
    is_default_training_type


def read_masterdata():
    storage = Storage()

    with storage.get_data_path().open('rb') as file:
        data = pickle.load(file)

    return data


def get_type(name):
    """
    Returns type dictionary by name. Name must match an existing type
    Precondition: Type must exists, otherwise exit will processed
    :return: E.g. dict(name='Pendel', tag='commute', velohero_id='7433')
    """

    if not 'types' in read_masterdata():
        exit_on_error("Master data not found. Use 'heroscript masterdata --refresh' to load data from Velohero")

    return [t for t in read_masterdata()['types'] if t['name'] == name][0]


def get_commute_type():
    """
    Counter part of utility.is_commute_training_type()
    :return: Type whis is tagged as commute or, if not found, None
    """
    for type in read_masterdata()['types']:
        if is_commute_training_type(type['name']):
            return type
    
    return None


def get_indoor_type():
    """
    Counter part of utility.is_indoor_training_type()
    :return: Type whis is tagged as indoor or, if not found, None
    """
    for type in read_masterdata()['types']:
        if is_indoor_training_type(type['name']):
            return type
    
    return None


def find_type_by_name(name):
    """
    Checks, if the name matchs a type an returns it.
    :param name: String with the name to parse
    :return: Matching type or, if not found, default type
    """
    for type in [t for t in read_masterdata()['types'] if t['name'].lower() == name.lower().strip()]:
        return type

    return get_default_type()


def get_competition_type():
    """
    Counter part of utility.is_competition_training_type()
    :return: Type whis is tagged as competition or, if not found, None
    """
    for type in read_masterdata()['types']:
        if is_competition_training_type(type['name']):
            return type
    
    return None


def get_default_type():
    """
    Counter part of utility.is_default_training_type()
    :return: Type whis is tagged as default or, if not found, None
    """
    for type in read_masterdata()['types']:
        if is_default_training_type(type['name']):
            return type
    
    return None


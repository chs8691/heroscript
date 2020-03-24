import time

import tempfile
import webbrowser
from os import path

from load import read_load
from tcxparser import TCXParser

import utility


def show_map():
    p = path.join(tempfile.gettempdir(), "heroscript_map.html")
    utility.log("Temp html", p)
    with open(p, "w") as file:
        file.write(Map().get())
        # print("See your default browser.".format(p))
        webbrowser.open(file.name)


class Map(object):
    def __init__(self):
        self._load = read_load()

        self._points = self.get_track_points()
        utility.log("Map imported track points", len(self._points))
        self._title = utility.get_human_date(self._load.started_at, "%y-%m-%d %H:%M")

        self._max_lon = None
        self._min_lon = None
        self._max_lat = None
        self._min_lat = None

    def update_center(self, lon, lat):
        if self._max_lat is None or (lat > self._max_lat):
            self._max_lat = lat
        if self._min_lat is None or (lat < self._min_lat):
            self._min_lat = lat
        if self._max_lon is None or (lon > self._max_lon):
            self._max_lon = lon
        if self._min_lon is None or (lon < self._min_lon):
            self._min_lon = lon
        # utility.log("extremas={}, {}, {}, {}".format(self._min_lon, self._max_lon, self._min_lat, self._max_lat))

    def get_center(self):
        """
        Returns always a coordinate
        :return: String with center or default center as (lon, lat)
        """
        # utility.log("extremas", "{}, {}, {}, {}".format(self._min_lon, self._max_lon, self._min_lat, self._max_lat))
        if self._max_lat is None or self._max_lon is None or self._min_lat is None or self._min_lon is None:
            ret = "[50.1, 7.1]"
        else:
            ret = "[{}, {}]".format(self._min_lat + (self._max_lat - self._min_lat) / 2.0,
                                    self._min_lon + (self._max_lon - self._min_lon) / 2.0)

        utility.log("Center", ret)
        return ret

    def get_track_points(self):
        """
        Returns tuple list with trackpoints e.g. [(50.18564460799098, 9.137571640312672), (50.18564460799098, 9.137571640312672)]
        :return: tuple list with (lat, lon), can be empty
        """
        with open(self._load.file_name, "r") as file:
            utility.log("parsing file", self._load.file_name)
            return TCXParser(self._load.file_name).position_values()

    def build_coordinates(self):
        """
        Creates a string with coordinates
        :return: e.g. "[[-0.09, 50.5],  [-0.2, 50.6]]"
        """
        ret = ""
        point_strings = []
        for (lat, lon) in self._points:
            p = "[{}, {}]".format(lon, lat)
            point_strings.append(p)
            # utility.log("p", p)
            self.update_center(lon, lat)

        ret = ", ".join(point_strings)
        # utility.log("point_strings={}".format(point_strings))
        ret = "[{}]".format(ret)
        # utility.log("ret={}".format(ret))

        return ret

    def get(self):
        with open('map.html', "r") as out:
            return out.read().format(coordinates=self.build_coordinates(), title=self._title,
                                     center=self.get_center(), start="[{}, {}]".format(self._points[0][0],
                                                                                       self._points[0][1]),
                                     end="[{}, {}]".format(self._points[-1][0],
                                                           self._points[-1][1]),
                                     bounds="[[{}, {}], [{}, {}]]".format(self._max_lat, self._min_lon,
                                                                          self._min_lat, self._max_lon)
                                     )


def process_show(args):
    utility.log("process_show", "start")

    load = read_load()

    if args.map:
        show_map()
        # print("Opening map in default Browser...", end='', flush=True)
        # tracksfer_gps.map("track.gps")
        # print("Done.")
        return

    if not path.exists(load.file_name):
        file_message = "<--------- MISSING !!!"
    else:
        file_message = ""

    print('File Name              : {} {}'.format(load.file_name, file_message))

    print('--- ATTRIBUTES ---')

    if load.new_activity_type is None:
        print(f"Activity Type          : ({load.original_activity_type})  "
              f"<=== Use set --activity_type {utility.activity_type_list}")
    else:
        print('Activity Type          : %s (original: %s)' %
              (load.new_activity_type, load.original_activity_type))

    print('Training Type          : %s' % load.training_type)

    print('Route Name             : %s' % load.route_name)

    print('Equipment Names        : %s' % load.equipment_names)

    print(f"Name                   : '{load.title}'")

    print("Comment                : '%s'" % load.comment)
    print("")

    print("Started at (GMT)       : {}".format(utility.get_human_date(load.started_at, "%a %y-%m-%d %H:%M")))

    print("Distance               : {0:.1f} k{1}".format(load.distance/1000, load.distance_unit_abbreviation()))

    print("Duration               : {} h".format(time.strftime('%H:%M:%S', time.gmtime(load.duration))))

    print("Velocity - Pace (total): {0:.1f} k{1}/h - {2}/k{3}".format(
        load.velocity_average, load.distance_unit_abbreviation(), load.pace, load.distance_unit_abbreviation()))

    print("Altitude               : \u25B2 {0:.0f} \u25bc {1:.0f}  [{2:.0f}..{3:.0f}] {4}".format(
        load.ascent, load.descent, load.altitude_min, load.altitude_max, load.distance_units))

    print('--- STRAVA ---')
    print(f'Activity ID            : {load.strava_activity_id}')
    print(f'Activity Name          : {load.strava_activity_name}')

    if(load.strava_descriptions is None):
        print('Description (generated): None')
    else:
        print(f'Description (generated):')
        for description in load.strava_descriptions:
            print(f'    {description}')

    print('--- STATUS ---')
    print('Velohero Workout ID    : %s' % load.velohero_workout_id)

    print("Archived to            : {}".format(load.archived_to))

    utility.log("process_show", "end")
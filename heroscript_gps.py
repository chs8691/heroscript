import webbrowser
from datetime import datetime

from persistance import read_load
from tcxparser import TCXParser
import tempfile
from os import path

from utility import log, get_human_date


def show_map():
    p = path.join(tempfile.gettempdir(), "heroscript_map.html")
    log("Temp html", p)
    with open(p, "w") as file:
        file.write(Map().get())
        # print("See your default browser.".format(p))
        webbrowser.open(file.name)


class Map(object):
    def __init__(self):
        self._load = read_load()

        self._points = self.get_track_points()
        log("Map imported track points", len(self._points))
        self._title = get_human_date(self._load.started_at, "%y-%m-%d %H:%M")

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
        # log("extremas={}, {}, {}, {}".format(self._min_lon, self._max_lon, self._min_lat, self._max_lat))

    def get_center(self):
        """
        Returns always a coordinate
        :return: String with center or default center as (lon, lat)
        """
        # log("extremas", "{}, {}, {}, {}".format(self._min_lon, self._max_lon, self._min_lat, self._max_lat))
        if self._max_lat is None or self._max_lon is None or self._min_lat is None or self._min_lon is None:
            ret = "[50.1, 7.1]"
        else:
            ret = "[{}, {}]".format(self._min_lat + (self._max_lat - self._min_lat) / 2.0,
                                    self._min_lon + (self._max_lon - self._min_lon) / 2.0)

        log("Center", ret)
        return ret

    def get_track_points(self):
        """
        Returns tuple list with trackpoints e.g. [(50.18564460799098, 9.137571640312672), (50.18564460799098, 9.137571640312672)]
        :return: tuple list with (lat, lon), can be empty
        """
        with open(self._load.file_name, "r") as file:
            log("parsing file", self._load.file_name)
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
            # log("p", p)
            self.update_center(lon, lat)

        ret = ", ".join(point_strings)
        # log("point_strings={}".format(point_strings))
        ret = "[{}]".format(ret)
        # log("ret={}".format(ret))

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

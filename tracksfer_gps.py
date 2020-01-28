import os
import sys
import webbrowser
from shutil import copy

from utility import log


class Map(object):
    def __init__(self):
        self._points = []

    def add_point(self, coordinates):
        """
        Adds new marker
        :param coordinates: array with lan, lon, title, label
        :return:
        """
        self._points.append(coordinates)

    def count(self):
        """
        Returns the nr. of points
        :return: Positive integer
        """
        return len(self._points)

    def __str__(self):

        track_code = """\n  
            var map;
            
            function init(gpxfile) {{
                map = new OpenLayers.Map ("map", {{
                    maxExtent: new OpenLayers.Bounds(-20037508.34,-20037508.34,20037508.34,20037508.34),
                    maxResolution: 156543.0399,
                    numZoomLevels: 19,
                    units: 'm',
                    projection: new OpenLayers.Projection("EPSG:900913"),
                    displayProjection: new OpenLayers.Projection("EPSG:4326")
                }} );
            
                layerMapnik = new OpenLayers.Layer.OSM();
                map.addLayer(layerMapnik);
            
                var lgpx = new OpenLayers.Layer.GML("GPS route", "{gpxfile}", {{
                    format: OpenLayers.Format.GPX,
                    style: {{strokeColor: "red", strokeWidth: 5, strokeOpacity: 0.5}},
                    projection: new OpenLayers.Projection("EPSG:4326")
                }});
                map.addLayer(lgpx);
            
                if( ! map.getCenter() ){{
                    lgpx.events.register('loadend', map, function(){{this.zoomToExtent(lgpx.getDataExtent())}});
                    map.setCenter(null, null);
                }}
            }}
            
            init();
        """.format(gpxfile="track.gpx")

        return """
            <html>
            <body>
              <div id="mapdiv"></div>
              <script src="http://www.openlayers.org/api/OpenLayers.js"></script>
              <script>
                {track_code}
              </script>
            </body></html>
        """.format(track_code=track_code)


def map(image_path):
    """
    Show map with pins for all jpg images in the given path
    :param image_path: String with path
    :return: -
    """
    map = Map()

    # Sorted list by date, so the labels will be sorted

    file_path = "map.html"
    with open(file_path, "w") as out:
        print(map, file=out)
        webbrowser.open(file_path)


def do(analysis, force, verbose, write_path):
    """
    Cpmmand gps execution.
    """
    cnt_set = 0
    cnt_overwritten = 0
    cnt_nothing_done = 0

    print('Path to images: {}'.format(analysis['image_path']))
    print('Path to tracks: {}'.format(analysis['track_path']))
    if write_path is not None:
        print('Path to write track file copies: {}'.format(write_path))

    name_col_len = 1
    # Column length for image name
    for each in analysis['files']:
        if len(each['image_name']) > name_col_len:
            name_col_len = len(each['image_name'])

    if not verbose:
        # print('Processing images', end='')
        index = 0
        progress = progress_prepare(len(analysis['files']), 'Processing', analysis['image_path'])

    # --write: Do this in a separate step
    copy_list = []

    for each in analysis['files']:
        if not verbose:
            # print('.', end='')
            index += 1
            sys.stdout.write(progress['back'] + progress['formatting'].format(str(index)))
            sys.stdout.flush()
        action = ' '
        gpx_name = ''
        if each['image_gps'] is None:
            has_gps = ' '
        else:
            has_gps = 'g'
        if not force:
            cnt_nothing_done += 1
            continue

        gps_new = None
        for each_track in each['tracks']:
            image_write_gps(
                '{}/{}'.format(analysis['image_path'], each['image_name']),
                '{}/{}'.format(analysis['track_path'], each_track))
            gps_new = image_get_exifs(analysis['image_path'], each['image_name'])['gps']

            # Exit criteria: gps set
            if gps_new is not None:
                if gps_new == each['image_gps']:
                    # Same gps, try again
                    continue
                has_gps = 'g'
                gpx_name = each_track
                if each['image_gps'] is None:
                    action = '+'
                else:
                    action = '*'
                    cnt_overwritten += 1
                break

        if action == ' ':
            cnt_nothing_done += 1
        else:
            cnt_set += 1

        if verbose:
            # +g img001.jpg 20160321.gpx
            formatting = '{}{} {:<' + str(name_col_len) + '} {}'
            print(formatting.format(action, has_gps, each['image_name'], gpx_name))

        if action != ' ' and write_path is not None:
            copy_list.append(gpx_name)

    if not verbose:
        # print('Done.')
        sys.stdout.write('\n')

    # --write: Now copy found track files to destination
    cnt_write_err = 0
    cnt_write = 0
    cnt_overwritten = 0
    for each in frozenset(copy_list):
        if each in analysis['existing_track_files']:
            verb = "Done (overwritten)."
        else:
            verb = "Done."
        try:
            copy(os.path.join(analysis['track_path'], each), write_path)
            if verbose:
                print("Copy {} {}".format(each, verb))
            cnt_write += 1
            if each in analysis['existing_track_files']:
                cnt_overwritten += 1
        except IOError as e:
            print("Copy {} failed: {}".format(each, e))
            cnt_write_err += 1

    if write_path is None:
        print('{} images processed, {} gps data set (where {} existing gps data were changed).'
              .format(len(analysis['files']), cnt_set, cnt_overwritten))
    else:
        print(('{} images processed, {} gps data set (where {} existing gps data were changed). '
               'Copied {} track file(s), {} overwritten, {} failed.')
              .format(len(analysis['files']), cnt_set, cnt_overwritten, cnt_write, cnt_overwritten, cnt_write_err))


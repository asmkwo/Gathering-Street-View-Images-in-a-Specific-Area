from typing import Dict, Union

from osmnx import downloader, utils_geo

from jeddah.conversion_functions import coords_as_path_str
from jeddah.create_path import compute_distance_with_haversine, filling_missing_points
from jeddah.display_map import get_map, get_map_w_paths, save_map_from_request
from jeddah.point import Point
from settings.settings import settings


API_KEY = settings.api_key.get_secret_value()
BASE_MAPS = settings.maps_base
DATABASE_DIRECTORY = settings.database_directory


def deadal_from_point(
    center_point: Point, radius: int, network_type: str = "all_private"
) -> Dict[str, Union[int, str]]:
    """
    Create a graph from OSM within some distance of some (lat, lng) point.

    """
    custom_filter = None
    # create bounding box from center point and distance in each direction
    north, south, east, west = utils_geo.bbox_from_point(point=center_point, dist=radius)

    # convert bounding box to a polygon
    polygon = utils_geo.bbox_to_poly(north, south, east, west)

    if not polygon.is_valid:
        raise ValueError("The geometry to query within is invalid")

    nodes = dict()
    paths = dict()
    # download the network data from OSM
    response_jsons = downloader._osm_network_download(
        polygon, network_type, custom_filter
    )

    accepted_highway_types = [
        "motorway",
        "trunk",
        "primary",
        "secondary",
        "tertiary",
        "unclassified",
        "residential",
        "motorway_link",
        "trunk_link",
        "primary_link",
        "seconday_link",
        "tertiary_link",
        "living_street",
        "pedestrian",
    ]

    for response_json in response_jsons:
        for element in response_json["elements"]:
            # we have to be sure that all nodes are handled first. Maybe modify code
            if element["type"] == "node":
                nodes[element["id"]] = Point(element["lat"], element["lon"])
            elif (
                element["type"] == "way"
                and element["tags"]["highway"] in accepted_highway_types
            ):
                paths[element["id"]] = element["nodes"]

    center_point = Point(center_point[0], center_point[1])
    paths_points = dict()

    for id, node_list in paths.items():
        list_of_points = []
        for node_id in node_list:
            if (
                compute_distance_with_haversine(nodes[node_id], center_point)
                < radius + 50
            ):
                list_of_points.append(nodes[node_id])
        paths_points[id] = list_of_points

    path_str = []
    big_point_list = []
    paths_filled = dict()
    for id, point_list in paths_points.items():
        # adding weight info is for the google maps API line tracing.
        path_str.append("weight:1|" + coords_as_path_str(point_list))

        # filling each path
        if len(point_list) != 0:
            point_list_filled = filling_missing_points(point_list, threshold=10)
            # TODO replace threshold
            paths_filled[id] = point_list_filled

    # putting all points together to create markers map
    for id, point_list in paths_points.items():
        # put here the line for the API that was higher
        for point in point_list:
            big_point_list.append(point)

    map_request = get_map_w_paths(path_str[240:300], center_point)
    save_map_from_request(map_request, DATABASE_DIRECTORY)
    map_request_markers = get_map(big_point_list[0:80])
    save_map_from_request(map_request_markers, DATABASE_DIRECTORY, "_markers")

    return paths_filled

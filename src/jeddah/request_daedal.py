from typing import Any, Dict, List, Tuple

from osmnx import downloader, utils_geo
from shapely.geometry import Polygon

from jeddah.create_path import compute_distance_with_haversine, process_path
from jeddah.point import Point


def daedal_from_point(
    center_point: Point, radius: int, threshold: int
) -> Dict[int, List[Point]]:
    polygon_boundaries = create_polygon(center_point, radius)
    nodes_dict, paths_dict = request_nodes_and_paths(polygon_boundaries)
    paths_pruned = keep_points_within_radius(center_point, radius, nodes_dict, paths_dict)
    path_filled = complete_all_paths(paths_pruned, threshold)
    return path_filled


def create_polygon(center_point: Point, radius: int) -> Polygon:
    north, south, east, west = utils_geo.bbox_from_point(
        point=(center_point.latitude, center_point.longitude), dist=radius
    )
    # convert bounding box to a polygon
    polygon = utils_geo.bbox_to_poly(north, south, east, west)
    return polygon


def request_nodes_and_paths(
    polygon: Polygon,
) -> Tuple[Dict[int, Point], Dict[int, Any]]:
    nodes = dict()
    paths = dict()
    network_type = "all_private"
    custom_filter = None

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
                nodes[int(element["id"])] = Point(element["lat"], element["lon"])
            elif (
                element["type"] == "way"
                and element["tags"]["highway"] in accepted_highway_types
            ):
                paths[int(element["id"])] = element["nodes"]

    return nodes, paths


def keep_points_within_radius(
    center_point: Point, radius: int, nodes: Dict[int, Point], paths: Dict[int, Any]
) -> Dict[int, List[Point]]:
    # center_point = Point(center_point[0], center_point[1])
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

    return paths_points


def complete_all_paths(
    paths_points: Dict[int, List[Point]], threshold: int
) -> Dict[int, List[Point]]:
    paths_filled = dict()
    for id, point_list in paths_points.items():
        if len(point_list) != 0:
            point_list_processed = process_path(point_list, threshold)
            paths_filled[id] = point_list_processed

    return paths_filled


# the part that creates the final map should be inserted here

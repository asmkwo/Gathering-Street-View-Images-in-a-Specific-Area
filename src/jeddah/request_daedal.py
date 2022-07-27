from osmnx import downloader, utils_geo
from shapely.geometry import MultiPolygon, Polygon

from jeddah.conversion_functions import coords_as_path_str
from jeddah.create_path import compute_distance_with_haversine, filling_missing_points
from jeddah.display_map import get_map, get_map_w_paths, save_map_from_request
from jeddah.point import Point
from settings.settings import settings


API_KEY = settings.api_key.get_secret_value()
BASE_MAPS = settings.maps_base
DATABASE_DIRECTORY = settings.database_directory


def deadal_from_point(
    center_point,
    radius,
    dist_type="bbox",
    network_type="all_private",
    custom_filter=None,
):
    """
    Create a graph from OSM within some distance of some (lat, lng) point.

    """

    if dist_type not in {"bbox", "network"}:  # pragma: no cover
        raise ValueError('dist_type must be "bbox" or "network"')

    # create bounding box from center point and distance in each direction
    north, south, east, west = utils_geo.bbox_from_point(point=center_point, dist=radius)

    # convert bounding box to a polygon
    polygon = utils_geo.bbox_to_poly(north, south, east, west)

    if not polygon.is_valid:
        raise ValueError("The geometry to query within is invalid")
    if not isinstance(polygon, (Polygon, MultiPolygon)):  # pragma: no cover
        raise TypeError(
            "Geometry must be a shapely Polygon or MultiPolygon. If you requested "
            "graph from place name, make sure your query resolves to a Polygon or "
            "MultiPolygon, and not some other geometry, like a Point. See OSMnx "
            "documentation for details."
        )

    # if clean_periphery=False, just use the polygon as provided
    nodes = dict()
    paths = dict()
    # download the network data from OSM
    response_jsons = downloader._osm_network_download(
        polygon, network_type, custom_filter
    )

    accepted_highway_types = [
        'motorway',
        'trunk',
        'primary',
        'secondary',
        'tertiary',
        'unclassified',
        'residential',
        'motorway_link',
        'trunk_link',
        'primary_link',
        'seconday_link',
        'tertiary_link',
        'living_street',
        'pedestrian',
    ]

    for response_json in response_jsons:
        for element in response_json['elements']:
            # we have to be sure that all nodes are handled first. Maybe modify code
            if element['type'] == 'node':
                nodes[element['id']] = Point(element['lat'], element['lon'])
            elif (
                element['type'] == 'way'
                and element['tags']['highway'] in accepted_highway_types
            ):
                paths[element['id']] = element['nodes']
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
    counter_before = 0
    counter_after = 0
    for id, point_list in paths_points.items():
        counter_before += len(point_list)
        # adding weight info is for the google maps API line tracing.
        path_str.append('weight:1|' + coords_as_path_str(point_list))

        # filling each path
        # tester de snap to road and interpolate
        if len(point_list) != 0:
            point_list_filled = filling_missing_points(point_list, threshold=10)
            paths_filled[id] = point_list_filled
            counter_after += len(point_list_filled)
        # putting all points together to create markers map
        for point in point_list:
            big_point_list.append(point)

    print(f"Before filling : {counter_before}")
    print(f"After filling : {counter_after}")

    map_request = get_map_w_paths(path_str[240:300], center_point)
    save_map_from_request(map_request, DATABASE_DIRECTORY)
    map_request_markers = get_map(big_point_list[0:80])
    save_map_from_request(map_request_markers, DATABASE_DIRECTORY, '_markers')

    return paths_filled

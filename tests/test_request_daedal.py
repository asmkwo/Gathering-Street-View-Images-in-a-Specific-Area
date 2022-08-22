import math

from osmnx import downloader
from shapely.geometry import Polygon

import jeddah
from jeddah.point import Point
from jeddah.request_daedal import (
    complete_all_paths,
    create_polygon,
    keep_points_within_radius,
    request_nodes_and_paths,
)


def test_create_polygon_returns_the_expected_polygon():
    expected_polygon_boundaries = (-3.704688, 40.407372, -3.681063, 40.425359)
    error_tolerance = 1e-05
    center_point = Point(40.416366, -3.692876)
    radius = 1000
    polygon = create_polygon(center_point, radius)
    polygon_boundaries = polygon.bounds
    assert math.isclose(
        polygon_boundaries[0], expected_polygon_boundaries[0], abs_tol=error_tolerance
    )
    assert math.isclose(
        polygon_boundaries[1], expected_polygon_boundaries[1], abs_tol=error_tolerance
    )
    assert math.isclose(
        polygon_boundaries[2], expected_polygon_boundaries[2], abs_tol=error_tolerance
    )
    assert math.isclose(
        polygon_boundaries[3], expected_polygon_boundaries[3], abs_tol=error_tolerance
    )


def test_request_path_and_nodes_returns_the_expected_dictionary(monkeypatch):
    def mock_return(polygon, network_type, custom_filter):
        mock_response = [
            {
                'version': 0.6,
                'generator': 'Overpass API 0.7.58.5 b0c4acbb',
                'osm3s': {
                    'timestamp_osm_base': '2022-08-05T09:47:23Z',
                    'copyright': 'The data included in this document is from '
                    'www.openstreetmap.org. The data is made available under ODbL.',
                },
                'elements': [
                    {
                        'type': 'node',
                        'id': 1209331632,
                        'lat': 40.4168917,
                        'lon': -3.6927969,
                    },
                    {
                        'type': 'node',
                        'id': 1522689902,
                        'lat': 40.4158491,
                        'lon': -3.6929779,
                    },
                    {
                        'type': 'node',
                        'id': 1522689905,
                        'lat': 40.4160869,
                        'lon': -3.6929365,
                    },
                    {
                        'type': 'node',
                        'id': 1522689910,
                        'lat': 40.416112,
                        'lon': -3.6929321,
                    },
                    {'type': 'node', 'id': 1522689937, 'lat': 40.41631, 'lon': -3.692836},
                    {
                        'type': 'node',
                        'id': 1522689938,
                        'lat': 40.4163123,
                        'lon': -3.6928982,
                    },
                    {
                        'type': 'node',
                        'id': 1522689939,
                        'lat': 40.4163172,
                        'lon': -3.6929512,
                    },
                    {
                        'type': 'node',
                        'id': 1522689941,
                        'lat': 40.4163472,
                        'lon': -3.6927737,
                    },
                    {
                        'type': 'node',
                        'id': 1522689951,
                        'lat': 40.4164225,
                        'lon': -3.6927587,
                    },
                    {
                        'type': 'node',
                        'id': 1522689961,
                        'lat': 40.4164741,
                        'lon': -3.692813,
                    },
                    {
                        'type': 'node',
                        'id': 1522689962,
                        'lat': 40.4164809,
                        'lon': -3.6928683,
                    },
                    {
                        'type': 'node',
                        'id': 1522689963,
                        'lat': 40.4164844,
                        'lon': -3.6929254,
                    },
                    {
                        'type': 'node',
                        'id': 1522689992,
                        'lat': 40.4166764,
                        'lon': -3.6928282,
                    },
                    {
                        'type': 'node',
                        'id': 1522689998,
                        'lat': 40.4166982,
                        'lon': -3.6928255,
                    },
                    {
                        'type': 'way',
                        'id': 138884787,
                        'nodes': [1209331632, 1522689998, 1522689992, 1522689962],
                        'tags': {'highway': 'motorway'},
                    },
                    {
                        'type': 'way',
                        'id': 138884788,
                        'nodes': [1522689938, 1522689910, 1522689905, 1522689902],
                        'tags': {'highway': 'motorway'},
                    },
                    {
                        'type': 'way',
                        'id': 138884795,
                        'nodes': [
                            1522689938,
                            1522689937,
                            1522689941,
                            1522689951,
                            1522689961,
                            1522689962,
                            1522689963,
                            1522689939,
                            1522689938,
                        ],
                        'tags': {'highway': 'motorway'},
                    },
                ],
            }
        ]
        return mock_response

    monkeypatch.setattr(downloader, "_osm_network_download", mock_return)

    polygon = Polygon()

    expected_nodes = {
        1209331632: Point(40.4168917, -3.6927969),
        1522689902: Point(40.4158491, -3.6929779),
        1522689905: Point(40.4160869, -3.6929365),
        1522689910: Point(40.416112, -3.6929321),
        1522689937: Point(40.41631, -3.692836),
        1522689938: Point(40.4163123, -3.6928982),
        1522689939: Point(40.4163172, -3.6929512),
        1522689941: Point(40.4163472, -3.6927737),
        1522689951: Point(40.4164225, -3.6927587),
        1522689961: Point(40.4164741, -3.692813),
        1522689962: Point(40.4164809, -3.6928683),
        1522689963: Point(40.4164844, -3.6929254),
        1522689992: Point(40.4166764, -3.6928282),
        1522689998: Point(40.4166982, -3.6928255),
    }

    expected_paths = {
        138884787: [1209331632, 1522689998, 1522689992, 1522689962],
        138884788: [1522689938, 1522689910, 1522689905, 1522689902],
        138884795: [
            1522689938,
            1522689937,
            1522689941,
            1522689951,
            1522689961,
            1522689962,
            1522689963,
            1522689939,
            1522689938,
        ],
    }

    nodes, paths = request_nodes_and_paths(polygon)
    assert nodes == expected_nodes
    assert paths == expected_paths


def test_keep_points_within_radius_effectively_keeps_points_within():

    radius = 550
    center_point = Point(48.858516, 2.348244)

    nodes = {
        1: Point(48.861872, 2.350718),
        2: Point(48.861982, 2.350205),
        3: Point(48.862786, 2.350638),
        4: Point(48.863365, 2.350958),
        5: Point(48.864484, 2.351608),
        6: Point(48.864861, 2.353372),
        7: Point(48.865362, 2.355636),
        8: Point(48.865976, 2.358352),
        9: Point(48.860222, 2.350792),
    }

    paths = {10: [1, 2, 3, 4, 5, 6, 7, 8, 9]}

    expected_path = {
        10: [
            Point(48.861872, 2.350718),
            Point(48.861982, 2.350205),
            Point(48.862786, 2.350638),
            Point(48.863365, 2.350958),
            Point(48.860222, 2.350792),
        ]
    }

    path_in_radius = keep_points_within_radius(center_point, radius, nodes, paths)

    assert path_in_radius == expected_path


def test_complete_all_paths_completes_all_paths(monkeypatch):
    def mock_return(point_list, threshold):
        mock_response = [
            Point(48.866972, 2.356597),
            Point(48.867107, 2.356678),
            Point(48.867252, 2.356781),
            Point(48.867335, 2.356371),
            Point(48.867519, 2.355772),
            Point(48.867724, 2.354896),
            Point(48.867931, 2.355010),
            Point(48.868157, 2.355126),
        ]
        return mock_response

    monkeypatch.setattr(jeddah.request_daedal, "process_path", mock_return)

    path_to_fill = {
        1: [
            Point(48.866972, 2.356597),
            Point(48.867252, 2.356781),
            Point(48.867724, 2.354896),
            Point(48.868157, 2.355126),
        ]
    }
    expected_path_filled = {
        1: [
            Point(48.866972, 2.356597),
            Point(48.867107, 2.356678),
            Point(48.867252, 2.356781),
            Point(48.867335, 2.356371),
            Point(48.867519, 2.355772),
            Point(48.867724, 2.354896),
            Point(48.867931, 2.355010),
            Point(48.868157, 2.355126),
        ]
    }

    point_list_filled = complete_all_paths(path_to_fill, threshold=10)

    assert point_list_filled == expected_path_filled

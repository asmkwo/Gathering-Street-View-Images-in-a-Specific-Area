from jeddah.conversion_functions import (
    coords_as_path,
    create_point_list,
    json_as_point_list,
)
from jeddah.point import Point


def test_coords_as_path():
    point_list = [Point(44.56, 27.83), Point(45.89, 28.12), Point(47.63, 29.35)]
    point_list_as_path = coords_as_path(point_list)
    assert point_list_as_path == '44.56,27.83|45.89,28.12|47.63,29.35'


def test_json_as_point_list():
    json_simulated_response = {
        'snappedPoints': [
            {
                'location': {
                    'latitude': 44.85130749493737,
                    'longitude': -0.6090405982459559,
                },
                'originalIndex': 0,
                'placeId': 'ChIJj3Sv__jXVA0RgPl6rn0njSg',
            },
            {
                'location': {'latitude': 44.8512127, 'longitude': -0.6086045},
                'placeId': 'ChIJj3Sv__jXVA0RgPl6rn0njSg',
            },
            {'location': {'latitude': 44.8511461, 'longitude': -0.6083333}},
        ]
    }
    json_as_list = json_as_point_list(json_simulated_response)
    point_list = [
        Point(44.85130749493737, -0.6090405982459559),
        Point(44.8512127, -0.6086045),
        Point(44.8511461, -0.6083333),
    ]

    assert json_as_list == point_list


def test_create_create_point_list():
    path = (
        '48.860597,2.349461|48.862039,2.350262|48.863353,2.350998|48.862670,2.354307'
        '|48.862385,2.357433'
    )
    point_list = create_point_list(path)
    assert len(point_list) == 5
    point_1 = point_list[2]
    assert point_1.latitude == 48.863353

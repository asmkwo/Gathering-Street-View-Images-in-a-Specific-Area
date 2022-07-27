from jeddah.conversion_functions import coords_as_path_str, create_path, json_as_path
from jeddah.point import Point


def test_coords_as_path_str_transforms_list_of_points_into_google_api_path_format():
    initial_path = [Point(44.56, 27.83), Point(45.89, 28.12), Point(47.63, 29.35)]
    expected_path = '44.56,27.83|45.89,28.12|47.63,29.35'
    path_str = coords_as_path_str(initial_path)
    assert path_str == expected_path


def test_json_as_path_transforms_json_returned_by_roads_API_into_google_api_path_format():
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
    expected_path = [
        Point(44.85130749493737, -0.6090405982459559),
        Point(44.8512127, -0.6086045),
        Point(44.8511461, -0.6083333),
    ]

    json_as_list = json_as_path(json_simulated_response)

    assert json_as_list == expected_path


def test_create_path_transforms_a_google_api_path_into_a_list_of_points():
    path_str = (
        '48.860597,2.349461|48.862039,2.350262|48.863353,2.350998|48.862670,2.354307'
        '|48.862385,2.357433'
    )
    expected_path = [
        Point(48.860597, 2.349461),
        Point(48.862039, 2.350262),
        Point(48.863353, 2.350998),
        Point(48.862670, 2.354307),
        Point(48.862385, 2.357433),
    ]

    path = create_path(path_str)

    assert path == expected_path

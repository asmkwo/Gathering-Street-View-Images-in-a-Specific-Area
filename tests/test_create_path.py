import math

import requests

from jeddah.create_path import (
    compute_distance_with_haversine,
    filling_missing_points,
    get_delta_shift,
    get_heading,
    interpolate_points,
    make_a_step_and_snap,
    prune_point_list_with_threshold,
    snap_to_road_and_interpolate,
)
from jeddah.point import Point


def test_snap_to_road_and_interpolate_returns_a_list_filled_with_more_points():
    point_list = [Point(44.851332, -0.609030), Point(44.850580, -0.606297)]
    point_list_snapped = snap_to_road_and_interpolate(point_list)
    assert len(point_list) <= len(point_list_snapped)


def test_snap_to_road_and_interpolate_call_works(monkeypatch):
    def mock_return(link_base_for_api, params):
        mock_response = requests.Response()
        mock_response._content = (
            b'{\n  "snappedPoints": [\n    {\n      '
            b'"location": {\n        "latitude": '
            b'44.851307494937373,\n        "longitude": '
            b'-0.60904059824595591\n      },\n      '
            b'"originalIndex": 0,\n      "placeId": '
            b'"ChIJj3Sv__jXVA0RgPl6rn0njSg"\n    },\n    {\n'
            b'      "location": {\n        "latitude": 44.8512127'
            b',\n        "longitude": -0.6086045\n      },\n'
            b'      "placeId": "ChIJj3Sv__jXVA0RgPl6rn0njSg"\n'
            b'    },\n    {\n      "location": {\n        '
            b'"latitude": 44.8511461,\n        "longitude":'
            b' -0.6083333\n      },\n      "placeId": '
            b'"ChIJj3Sv__jXVA0RgPl6rn0njSg"\n    },\n    {\n'
            b'      "location": {\n        "latitude": '
            b'44.8511461,\n        "longitude": -0.6083333\n'
            b'      },\n      "placeId": "ChIJj3Sv_'
            b'_jXVA0RomqVVljJ56Q"\n    },\n    {\n     '
            b' "location": {\n        "latitude": 44.8511381,'
            b'\n        "longitude": -0.6083008\n      },\n '
            b'     "placeId": "ChIJj3Sv__jXVA0RomqVVljJ56Q"\n '
            b'   },\n    {\n      "location": {\n        '
            b'"latitude": 44.8509623,\n        "longitude": '
            b'-0.6077105\n      },\n      "placeId": "ChIJj3Sv_'
            b'_jXVA0RomqVVljJ56Q"\n    },\n    {\n      '
            b'"location": {\n        "latitude": 44.8509623,\n'
            b'        "longitude": -0.6077105\n      },\n      '
            b'"placeId": "ChIJ20kT2_jXVA0Rj1aiCKibEAE"\n    },\n'
            b'    {\n      "location": {\n        "latitude": '
            b'44.850606299999995,\n        "longitude": '
            b'-0.60656310000000013\n      },\n      "placeId":'
            b' "ChIJ20kT2_jXVA0Rj1aiCKibEAE"\n    },\n    {\n'
            b'      "location": {\n        "latitude": '
            b'44.8505891,\n        "longitude": '
            b'-0.60649009999999992\n      },\n      "placeId": '
            b'"ChIJ20kT2_jXVA0Rj1aiCKibEAE"\n    },\n    {\n'
            b'      "location": {\n        "latitude": '
            b'44.8505839,\n        "longitude": '
            b'-0.60644259999999994\n      },\n      '
            b'"placeId": "ChIJ20kT2_jXVA0Rj1aiCKibEAE"\n'
            b'    },\n    {\n      "location": {\n        '
            b'"latitude": 44.85058639999999,\n        '
            b'"longitude": -0.60641649999999991\n      },\n'
            b'      "placeId": "ChIJ20kT2_jXVA0Rj1aiCKibEAE"\n'
            b'    },\n    {\n      "location": {\n        '
            b'"latitude": 44.8505906,\n        "longitude":'
            b' -0.6063942\n      },\n      "placeId": '
            b'"ChIJ20kT2_jXVA0Rj1aiCKibEAE"\n    },\n    {\n '
            b'     "location": {\n        "latitude": '
            b'44.8506065,\n        "longitude": '
            b'-0.60636309999999993\n      },\n      "placeId":'
            b' "ChIJ20kT2_jXVA0Rj1aiCKibEAE"\n    },\n    {\n'
            b'      "location": {\n        "latitude": '
            b'44.850617104797166,\n        "longitude": '
            b'-0.60634764000036812\n      },\n      '
            b'"originalIndex": 1,\n      "placeId": '
            b'"ChIJ20kT2_jXVA0Rj1aiCKibEAE"\n    }\n  ]\n}\n'
        )
        mock_response.status_code = 200
        mock_response.headers = {
            'Content-Type': 'application/json; charset=UTF-8',
            'Vary': 'Origin, X-Origin, Referer',
            'Date': 'Fri, 29 Jul 2022 11:37:36 GMT',
            'Server': 'scaffolding on HTTPServer2',
            'Content-Length': '2323',
            'X-XSS-Protection': '0',
            'X-Frame-Options': 'SAMEORIGIN',
            'X-Content-Type-Options': 'nosniff',
            'Alt-Svc': 'h3=":443"; ma=2592000,h3-29=":443"; ma=2592000,h3-Q050=":443"'
            '; ma=2592000,h3-Q046=":443"; ma=2592000,h3-Q043=":443"; '
            'ma=2592000,quic=":443"; ma=2592000; v="46,43"',
        }
        mock_response.url = (
            'https://roads.googleapis.com/v1/snapToRoads?key=AIzaSyBQC'
            'oecaoG-zGCi7ZarhVumEGqXJtnPIII&path=44.851332%2C-0.60903%'
            '7C44.85058%2C-0.606297&interpolate=true'
        )
        mock_response.encoding = 'UTF-8'
        mock_response.reason = 'OK'
        return mock_response

    monkeypatch.setattr(requests, "get", mock_return)

    point_list = [Point(44.851332, -0.609030), Point(44.850580, -0.606297)]
    expected_point_list = [
        Point(44.851307494937373, -0.60904059824595591),
        Point(44.8512127, -0.6086045),
        Point(44.8511461, -0.6083333),
        Point(44.8511461, -0.6083333),
        Point(44.8511381, -0.6083008),
        Point(44.8509623, -0.6077105),
        Point(44.8509623, -0.6077105),
        Point(44.850606299999995, -0.60656310000000013),
        Point(44.8505891, -0.60649009999999992),
        Point(44.8505839, -0.60644259999999994),
        Point(44.85058639999999, -0.60641649999999991),
        Point(44.8505906, -0.6063942),
        Point(44.8506065, -0.60636309999999993),
        Point(44.850617104797166, -0.60634764000036812),
    ]
    point_list_snapped = snap_to_road_and_interpolate(point_list)
    assert point_list_snapped == expected_point_list


def test_filling_missing_points_adds_points_between_two_given_points():

    point_list = [Point(44.851332, -0.60903), Point(44.85058, -0.606297)]
    expected_point_list = [
        Point(44.851332, -0.60903),
        Point(44.851332, -0.60903),
        Point(44.85123541970356, -0.6086751031515364),
        Point(44.85113883940713, -0.6083202068982047),
        Point(44.85104225911069, -0.6079653112400017),
        Point(44.850945678814256, -0.6076104161769247),
        Point(44.85084909851782, -0.6072555217089703),
        Point(44.850752518221384, -0.6069006278361359),
        Point(44.85065593792495, -0.6065457345584181),
        Point(44.85058, -0.606297),
    ]

    point_list_filled = filling_missing_points(point_list, 30)
    assert point_list_filled == expected_point_list


def test_filling_missing_points_outputs_points_that_are_not_too_far():
    point_list = [Point(44.851332, -0.60903), Point(44.85058, -0.606297)]
    point_list_filled = [
        Point(44.851332, -0.60903),
        Point(44.851332, -0.60903),
        Point(44.85123541970356, -0.6086751031515364),
        Point(44.85113883940713, -0.6083202068982047),
        Point(44.85104225911069, -0.6079653112400017),
        Point(44.850945678814256, -0.6076104161769247),
        Point(44.85084909851782, -0.6072555217089703),
        Point(44.850752518221384, -0.6069006278361359),
        Point(44.85065593792495, -0.6065457345584181),
        Point(44.85058, -0.606297),
    ]
    distance_start_and_end_point = compute_distance_with_haversine(
        point_list[0], point_list[1]
    )
    sum_distance_between_each_point = 0
    sum_distance_between_each_point += compute_distance_with_haversine(
        point_list_filled[0], point_list_filled[1]
    )
    sum_distance_between_each_point += compute_distance_with_haversine(
        point_list_filled[1], point_list_filled[2]
    )
    sum_distance_between_each_point += compute_distance_with_haversine(
        point_list_filled[2], point_list_filled[3]
    )
    sum_distance_between_each_point += compute_distance_with_haversine(
        point_list_filled[3], point_list_filled[4]
    )
    sum_distance_between_each_point += compute_distance_with_haversine(
        point_list_filled[4], point_list_filled[5]
    )
    sum_distance_between_each_point += compute_distance_with_haversine(
        point_list_filled[5], point_list_filled[6]
    )
    sum_distance_between_each_point += compute_distance_with_haversine(
        point_list_filled[6], point_list_filled[7]
    )
    sum_distance_between_each_point += compute_distance_with_haversine(
        point_list_filled[7], point_list_filled[8]
    )
    sum_distance_between_each_point += compute_distance_with_haversine(
        point_list_filled[8], point_list_filled[9]
    )

    assert sum_distance_between_each_point <= 2 * distance_start_and_end_point


def test_haversine_distance_returns_the_correct_distance_between_two_points():
    point_1, point_2 = Point(44.851332, -0.609030), Point(44.850580, -0.606297)
    measured_distance_between_points_1_and_2 = 231
    distance = compute_distance_with_haversine(point_1, point_2)
    assert math.isclose(distance, measured_distance_between_points_1_and_2, abs_tol=1)


def test_interpolate_points_places_new_points_between_two_others():
    point_list = [Point(44.851332, -0.609030), Point(44.850580, -0.606297)]
    list_of_interpolated_points = interpolate_points(point_list[0], point_list[1], 23)
    assert len(list_of_interpolated_points) == 11


def test_get_heading_returns_the_right_direction_2_points_are_pointing_towards():
    expected_heading = 111
    heading = get_heading(Point(44.851332, -0.609030), Point(44.850580, -0.606297))
    assert math.isclose(heading, expected_heading, abs_tol=3)


def test_make_a_step_and_snap_creates_a_new_point_in_the_given_direction_and_distance():
    reference_point = Point(44.851332, -0.609030)
    heading, distance = 110, 25
    point_after_step_snapped = make_a_step_and_snap(heading, reference_point, distance)

    assert 44.8512 <= point_after_step_snapped.latitude <= 44.8513
    assert -0.6088 <= point_after_step_snapped.longitude <= -0.6087
    assert (
        compute_distance_with_haversine(reference_point, point_after_step_snapped)
        <= 1.5 * 25
    )


def test_get_delta_shift_returns_variations_that_match_the_expected_distance():
    heading, expected_distance = 110, 25
    x_variation, y_variation = get_delta_shift(heading, expected_distance)
    distance = int(math.sqrt(x_variation**2 + y_variation**2))
    assert distance == expected_distance


def test_point_list_with_threshold_retains_points_separated_by_a_certain_distance():

    point_list_separated_by_5_meters = [
        Point(52.514894, 13.391269),
        Point(52.514900, 13.391376),
        Point(52.514908, 13.391498),
        Point(52.514915, 13.391610),
        Point(52.514923, 13.391728),
        Point(52.514931, 13.391846),
        Point(52.514939, 13.391957),
        Point(52.514942, 13.392021),
        Point(52.514946, 13.392092),
    ]
    threshold = 8
    expected_remaining_points = 5
    point_list_thresholded = prune_point_list_with_threshold(
        point_list_separated_by_5_meters, threshold
    )
    assert len(point_list_thresholded) == expected_remaining_points

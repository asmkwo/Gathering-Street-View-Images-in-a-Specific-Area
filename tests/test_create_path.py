import math

from _pytest import monkeypatch
import requests

from jeddah.conversion_functions import create_path
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


class MockResponse:
    @staticmethod
    def json():
        return {
            'snappedPoints': [
                {'location': {'latitude': 44.8512127, 'longitude': -0.6086045}},
                {'location': {'latitude': 44.8511461, 'longitude': -0.6083333}},
                {'location': {'latitude': 44.8511461, 'longitude': -0.6083333}},
                {'location': {'latitude': 44.8511381, 'longitude': -0.6083008}},
                {'location': {'latitude': 44.8509623, 'longitude': -0.6077105}},
                {'location': {'latitude': 44.8509623, 'longitude': -0.6077105}},
                {'location': {'latitude': 44.8505891, 'longitude': -0.6064900999999999}},
                {'location': {'latitude': 44.8505839, 'longitude': -0.6064425999999999}},
                {'location': {'latitude': 44.8505906, 'longitude': -0.6063942}},
                {'location': {'latitude': 44.8506065, 'longitude': -0.6063630999999999}},
            ]
        }


def test_snap_to_road_and_interpolate_call_works(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(requests, 'get', mock_get)

    point_list = [Point(44.851332, -0.609030), Point(44.850580, -0.606297)]
    point_list_snapped = snap_to_road_and_interpolate(point_list)
    assert len(point_list) <= len(point_list_snapped)


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

    # now we just going to check if the results are coherent
    distance_start_and_end_point = compute_distance_with_haversine(
        point_list[0], point_list[1]
    )
    sum_distance_between_each_point = 0
    for index in (0, len(point_list_filled) - 2):
        sum_distance_between_each_point += compute_distance_with_haversine(
            point_list_filled[index], point_list_filled[index + 1]
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

    assert (
        44.8512 <= point_after_step_snapped.latitude <= 44.8513
    )  # not sure of this kind of testing but hey
    assert -0.6088 <= point_after_step_snapped.longitude <= -0.6087
    assert (
        compute_distance_with_haversine(reference_point, point_after_step_snapped)
        <= 1.5 * 25
    )  # that may be better


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

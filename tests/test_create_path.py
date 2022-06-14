import math

from jeddah.conversion_functions import create_point_list
from jeddah.create_path import (
    compute_distance_with_haversine,
    filling_missing_points,
    get_delta_shift,
    get_heading,
    get_point_after_step,
    interpolate_points,
    make_a_step_and_snap,
    point_list_with_threshold,
    snap_single_point_to_roads,
    snap_to_road_and_interpolate,
)
from jeddah.point import Point


# from jeddah.point import Point


def test_snap_to_road_and_interpolate():
    path = '44.851332,-0.609030|44.850580,-0.606297'
    point_list = create_point_list(path)
    len_point_list = len(point_list)
    point_list_snapped = snap_to_road_and_interpolate(point_list)
    assert len_point_list <= len(point_list_snapped)


def test_filling_missing_points():
    path = '44.851332,-0.609030|44.850580,-0.606297'
    point_list = create_point_list(path)
    point_list_snapped = snap_to_road_and_interpolate(point_list)
    point_list_filled = filling_missing_points(point_list_snapped, 25)
    assert len(point_list_snapped) <= len(point_list_filled)
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


def test_haversine_distance():
    distance = compute_distance_with_haversine(
        Point(44.851332, -0.609030), Point(44.850580, -0.606297)
    )
    assert math.isclose(distance, 231, abs_tol=1)  # supposed to be 231


def test_interpolate_points():
    path = '44.851332,-0.609030|44.850580,-0.606297'
    point_list = create_point_list(path)
    list_of_interpolated_points = interpolate_points(point_list[0], point_list[1], 23)
    assert len(list_of_interpolated_points) == 11  # maybe change this for an interval


def test_get_heading():
    heading_111 = get_heading(Point(44.851332, -0.609030), Point(44.850580, -0.606297))
    assert 105 <= heading_111 <= 115  # supposed to be 111 but changes +- 2 degrees


def test_make_a_step_and_snap():
    reference_point = Point(44.851332, -0.609030)
    point_after_step_snapped = make_a_step_and_snap(110, reference_point, 25)
    assert (
        44.8512 <= point_after_step_snapped.latitude <= 44.8513
    )  # not sure of this kind of testing but hey
    assert -0.6088 <= point_after_step_snapped.longitude <= -0.6087
    assert (
        compute_distance_with_haversine(reference_point, point_after_step_snapped)
        <= 1.5 * 25
    )  # that may be better


def test_get_lat_long_after_step():
    reference_point = Point(44.851332, -0.609030)
    point_after_step = get_point_after_step(110, reference_point, 25)
    assert (
        44.8512 <= point_after_step.latitude <= 44.8513
    )  # not sure of this kind of testing but hey
    assert -0.6088 <= point_after_step.longitude <= -0.6087
    assert (
        compute_distance_with_haversine(reference_point, point_after_step) <= 1.5 * 25
    )  # that may be better


def test_get_delta_shift():
    dx, dy = get_delta_shift(heading=110, distance=25)
    assert int(math.sqrt(dx**2 + dy**2)) == 25


def test_snap_a_single_point_to_road():
    reference_point = Point(44.849989, -0.602469)
    point_snapped = snap_single_point_to_roads(reference_point)
    assert (
        29 <= compute_distance_with_haversine(point_snapped, reference_point) <= 31
    )  # equals 29.84
    assert (
        90 <= get_heading(reference_point, point_snapped) <= 270
    )  # pointing towards south hemisphere


def test_point_list_with_threshold():
    path = (
        '52.514894, 13.391269|52.514900, 13.391376|52.514908, 13.391498|52.514915, '
        '13.391610|52.514923, 13.391728|52.514931, 13.391846|52.514939,'
        ' 13.391957|52.514942,'
        ' 13.392021|52.514946, 13.392092'
    )
    # all these points are approximately 5 meters appart from each other
    point_list = create_point_list(path)
    point_list_thresholded = point_list_with_threshold(point_list, 8)
    assert len(point_list_thresholded) == 5  # should be only 5 points remaining

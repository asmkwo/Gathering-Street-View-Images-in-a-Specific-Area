import math
import os
from typing import List, Tuple

import pyproj
import requests

from jeddah.conversion_functions import (
    coords_as_path,
    create_point_list,
    json_as_point_list,
)
from jeddah.point import Point


# GLOBAL LINKS
META_BASE = 'https://maps.googleapis.com/maps/api/streetview/metadata?'
PIC_BASE = 'https://maps.googleapis.com/maps/api/streetview?'
ROADS_BASE = 'https://roads.googleapis.com/v1/snapToRoads?'
MAPS_BASE = 'https://maps.googleapis.com/maps/api/staticmap?'

# GLOBAL VARIABLES
EARTH_RADIUS_IN_KILOMETERS = 6378
API_KEY = os.environ['API_KEY']


def snap_to_road_and_interpolate(point_list: List[Point]) -> List[Point]:
    """
    Snaps a list of points to the nearest Road using Google's Roads API, and can add new
     points in between the ones in the given list if interpolation_boolean set to 'true'

    """
    # request to Roads API requires the path to be a certain string format
    coords_as_path_for_api = coords_as_path(point_list)

    params = {
        'key': API_KEY,
        'path': coords_as_path_for_api,
        'interpolate': 'true',
    }
    # requesting the Roads API
    try:
        response = requests.get(ROADS_BASE, params=params)
        json_path = response.json()

        # turn the json response into a list
        point_list = json_as_point_list(json_path)

    except requests.exceptions.HTTPError as e:
        print("Error: " + str(e))

    return point_list


def filling_missing_points(point_list: List[Point], threshold: int) -> List[Point]:
    """
    Fills the input list with new points if some are too far apart from each other

    :param threshold: Minimum distance that should separate 2 points
    """

    points_list_filled = []

    for index in range(0, len(point_list) - 1):

        distance_from_next_point = compute_distance_with_haversine(
            point_list[index], point_list[index + 1]
        )
        if distance_from_next_point > threshold:
            # the interpolate_points functions adds points between the two current ones
            interpolated_points = interpolate_points(
                point_list[index], point_list[index + 1], threshold
            )
            points_list_filled.append(point_list[index])

            # adding all the interpolated points to our list
            for interpolated_point in interpolated_points:
                points_list_filled.append(interpolated_point)

        else:
            points_list_filled.append(point_list[index])

    points_list_filled.append(point_list[-1])

    return points_list_filled


def compute_distance_with_haversine(point_1: Point, point_2: Point) -> float:
    """
    Calculates the distance, in meters, between two points using their coordinates and
    haversine formula
    """

    lat1, lng1 = point_1.latitude, point_1.longitude
    lat2, lng2 = point_2.latitude, point_2.longitude

    lat1_radians = math.radians(lat1)
    lat2_radians = math.radians(lat2)

    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)

    haversine_delta_lat = math.sin(delta_lat / 2) ** 2
    haversine_delta_lng = math.sin(delta_lng / 2) ** 2

    haversine_central_angle = (
        haversine_delta_lat
        + math.cos(lat1_radians) * math.cos(lat2_radians) * haversine_delta_lng
    )
    spherical_distance = 2 * math.atan2(
        math.sqrt(haversine_central_angle), math.sqrt(1 - haversine_central_angle)
    )
    kilo = 1000
    distance_in_meters = EARTH_RADIUS_IN_KILOMETERS * kilo * spherical_distance

    return distance_in_meters


def interpolate_points(point_1: Point, point_2: Point, threshold: int) -> List[Point]:
    """
    Used when two points are too far apart from each other. Will create new points between
     them, separated by the given threshold distance.
    """

    current_point = point_1
    added_points = [current_point]

    while compute_distance_with_haversine(current_point, point_2) > threshold:
        heading = get_heading(current_point, point_2)
        created_point = make_a_step_and_snap(heading, current_point, threshold)
        current_point = created_point
        added_points.append(current_point)

    return added_points


def get_heading(point_1: Point, point_2: Point) -> int:
    """
    Calculates the azimuth (angle defined by the line linking the two points and true
    north)  between two points
    """

    geodesic = pyproj.Geod(ellps='WGS84')
    lat1, long1 = point_1.latitude, point_1.longitude
    lat2, long2 = point_2.latitude, point_2.longitude
    fwd_azimuth, _, _ = geodesic.inv(long1, lat1, long2, lat2)
    if int(fwd_azimuth) < 0:
        fwd_azimuth += 360
    return int(fwd_azimuth)


def make_a_step_and_snap(heading: int, current_point: Point, distance: int) -> Point:
    """
    Make a step of a certain distance in the given direction (heading), creates a point
    and snaps it to the nearest road
    """
    next_point = get_point_after_step(heading, current_point, distance)

    snapped_point = snap_single_point_to_roads(next_point)

    return snapped_point


def get_point_after_step(heading: int, current_point: Point, distance: int) -> Point:
    """
    Creates a new points after making a step
    """
    lat, long = current_point.latitude, current_point.longitude

    dy, dx = get_delta_shift(heading, distance)

    new_lat = lat + (dy / (EARTH_RADIUS_IN_KILOMETERS * 1000) * (180 / math.pi))
    new_long = long + (dx / (EARTH_RADIUS_IN_KILOMETERS * 1000)) * (
        180 / math.pi
    ) / math.cos(lat * math.pi / 180)
    next_point = Point(new_lat, new_long)

    return next_point


def get_delta_shift(heading: int, distance: int) -> Tuple[float, float]:
    """
    Returns the small variation of distance (meters) along x and y axis that will separate
     our current point from the next point

    :param heading : Direction in which you want to make a step
    :param threshold : Distance of the step
    """
    theta = math.radians(heading)
    dx = distance * math.cos(theta)
    dy = distance * math.sin(theta)
    return dx, dy


def snap_single_point_to_roads(point: Point) -> Point:
    string_point = point.to_simple_string()
    params = {
        'key': API_KEY,
        'path': string_point,
    }
    response = requests.get(ROADS_BASE, params=params)
    json_path = response.json()

    point_list = json_as_point_list(json_path)
    snapped_point = point_list[0]

    return snapped_point


def point_list_with_threshold(point_list: List[Point], threshold: int) -> List[Point]:
    """
    Returns a list containing the points that are at least separated by the distance
     defined by the threshold
    """
    current_point = point_list[0]
    point_list_with_threshold = [current_point]

    for point in point_list:
        distance = compute_distance_with_haversine(current_point, point)

        if distance > threshold:
            point_list_with_threshold.append(point)
            current_point = point

    return point_list_with_threshold


def path_process(path: str) -> List[Point]:
    """
    :return: List of points fully processed, with points evenly separated
    """
    point_list = create_point_list(path)
    point_list_snapped = snap_to_road_and_interpolate(point_list)
    threshold = 10
    point_list_filled = filling_missing_points(point_list_snapped, threshold)
    point_list_pruned = point_list_with_threshold(point_list_filled, threshold)
    return point_list_pruned

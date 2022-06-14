from typing import Any, List

from jeddah.point import Point


def coords_as_path(point_list: List[Point]) -> str:
    """
    Turns a list of points' coordinates into the format required by the Roads API.
    """

    coords_as_path = ""

    for index, point in enumerate(point_list):
        coords_as_path += str(point.latitude) + "," + str(point.longitude)

        if index < len(point_list) - 1:
            coords_as_path += "|"

    return coords_as_path


def json_as_point_list(json_path: Any) -> List[Point]:
    """
    Turns the json format returned by the Roads API and turns it into a list of points
    """

    point_list = [
        Point(
            snapped_point["location"]["latitude"],
            snapped_point["location"]["longitude"],
        )
        for snapped_point in json_path['snappedPoints']
    ]

    return point_list


def create_point_list(path: str) -> List[Point]:
    """
    Converts a certain path into a list of Point objects
    """
    point_list = []
    split_path = path.split("|")
    for point in split_path:
        split_point = point.split(",")
        new_point = Point(float(split_point[0]), float(split_point[1]))
        point_list.append(new_point)

    return point_list

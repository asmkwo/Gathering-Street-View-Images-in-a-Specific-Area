from typing import Any, List

from jeddah.point import Point


def coords_as_path_str(path: List[Point]) -> str:
    """
    Turns a list of points' coordinates into the string format required by the Roads API.
    """

    return "|".join([str(point) for point in path])


def json_as_path(json_path: Any) -> List[Point]:
    """
    Turns the json format returned by the Roads API and turns it into a list of points
    """

    path = [
        Point(
            snapped_point["location"]["latitude"],
            snapped_point["location"]["longitude"],
        )
        for snapped_point in json_path['snappedPoints']
    ]

    return path


def create_path(path_str: str) -> List[Point]:
    """
    Converts a certain path into a list of Point objects
    """
    path = []
    split_path = path_str.split("|")
    for point in split_path:
        split_point = point.split(",")
        new_point = Point(float(split_point[0]), float(split_point[1]))
        path.append(new_point)

    return path

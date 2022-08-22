from pathlib import Path
import typing
from typing import Dict, List, Union

import requests
from requests import Response

from jeddah.conversion_functions import coords_as_path_str
from jeddah.point import Point
from settings.settings import settings


API_KEY = settings.api_key.get_secret_value()
BASE_MAPS = settings.maps_base


def get_map(path: List[Point]) -> Response:
    """
    Returns a map with the markers placed where indicated by path
    """
    params: Dict[str, Union[int, str]] = {
        "key": API_KEY,
        "markers": "size:small|" + coords_as_path_str(path),
        "size": "500x400",
        "scale": 4,
    }
    response = requests.get(BASE_MAPS, params=params)
    return response


def get_map_w_paths(
    path_list: List[str], center_point: typing.Tuple[float, float]
) -> Union[Response, str]:
    """
    Returns a map with the markers placed where indicated by path
    """
    params: Dict[str, Union[int, str, List[str]]] = {
        "key": API_KEY,
        "size": "500x400",
        "scale": 2,
        "format": "PNG",
        "path": path_list,
        "markers": str(center_point),
        "center": "48.869196 2.338722",
        "zoom": 15,
    }
    response = requests.get(BASE_MAPS, params=params)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        # response = requests.Response()
        return "Error" + str(e)

    return response


def save_map(path: List[Point], project_directory: Path) -> None:
    """
    Requests a map and stores it into the project directory
    """
    map_request = get_map(path)
    map_path = project_directory / "map.png"
    with map_path.open("wb") as file:
        file.write(map_request.content)
    map_request.close()


def save_map_from_request(
    map_request: Response, project_directory: Path, name: str = ""
) -> None:
    name_of_image = "map" + name + ".png"
    map_path = project_directory / name_of_image
    with map_path.open("wb") as file:
        file.write(map_request.content)
    map_request.close()

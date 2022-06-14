import os
from pathlib import Path
from typing import Dict, List, Union

import requests
from requests import Response

from jeddah.conversion_functions import coords_as_path
from jeddah.point import Point


base_maps = 'https://maps.googleapis.com/maps/api/staticmap?'
API_KEY = os.environ['API_KEY']


def get_map(point_list: List[Point]) -> Response:
    """
    Returns a map with the markers placed where indicated by point_list
    """
    params: Dict[str, Union[int, str]] = {
        'key': API_KEY,
        'markers': 'size:small' + coords_as_path(point_list),
        'size': '500x400',
        'scale': 4,
    }
    response = requests.get(base_maps, params=params)
    return response


def save_map(point_list: List[Point], project_directory: Path) -> None:
    """
    Requests a map and stores it into the project directory
    """
    map_request = get_map(point_list)
    map_path = project_directory / 'map.png'
    with map_path.open('wb') as file:
        file.write(map_request.content)
    map_request.close()

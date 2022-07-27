import os
from pathlib import Path

from jeddah.create_path import create_path
from jeddah.display_map import get_map, save_map


DATABASE_DIRECTORY = Path(os.getcwd())
path = (
    '48.860597,2.349461|48.862039,2.350262|48.863353,2.350998|48.862670,2.354307'
    '|48.862385,2.357433'
)
point_list = create_path(path)


def test_get_map_effectively_returns_a_map_image():
    response = get_map(point_list)
    assert response.headers['Content-Type'] == 'image/png'


def test_save_map():
    save_map(point_list, DATABASE_DIRECTORY)
    map_path = DATABASE_DIRECTORY / 'map.png'
    assert map_path.is_file()
    os.remove(str(map_path))  # temporary

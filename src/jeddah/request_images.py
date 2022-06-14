import os
from pathlib import Path
from typing import Any, Dict, List, Union

import requests
from requests import Response

from jeddah.create_path import get_heading
from jeddah.database_config import Database, Image, PathForDatabase, PointForDatabase
from jeddah.point import Point


# GLOBAL VARIABLES

API_KEY = os.environ['API_KEY']

# GLOBAL LINKS
META_BASE = 'https://maps.googleapis.com/maps/api/streetview/metadata?'
PIC_BASE = 'https://maps.googleapis.com/maps/api/streetview?'


def get_single_image(point: Point, heading: int = 0) -> Response:
    """
    :return: JSON containing the .jpg requested image
    """

    params: Dict[str, Union[int, str]] = {
        'key': API_KEY,
        'location': point.to_simple_string(),
        'size': "640x640",
        'fov': 100,
        'heading': heading,
        'source': 'outdoor',
        'pitch': 20,
        'radius': 50,
        'return-error-code': 'true',
    }
    response = requests.get(PIC_BASE, params=params)

    return response


def get_metadata(point: Point) -> Any:
    """
    Not used at the moment, could be for future issues
    """
    params = {'key': API_KEY, 'location': point.to_simple_string()}
    meta_response = requests.get(META_BASE, params=params)
    return meta_response


def get_both_direction_images(
    point: Point,
    project_path: Path,
    azimuth: int,
    index: int,
    point_for_db: PointForDatabase,
) -> None:
    """
    :param azimuth: direction in which the google street view car is heading, in order to
    get side view images
    """

    headings_offsets = [90, -90]  # to get image on right and left side
    for heading_offset in headings_offsets:
        str_heading = str(heading_offset)
        heading = azimuth + heading_offset
        img_request = get_single_image(point, heading)
        name_of_image = 'image_point_' + str(index) + '_' + str_heading + '.jpg'
        image_path = project_path / name_of_image
        with image_path.open('wb') as file:
            file.write(img_request.content)
        # creating image object for db
        image_stored = Image(
            img_path=str(image_path),
            heading=heading,
        )
        point_for_db.image_relation.append(image_stored)

        img_request.close()


def get_images_along_path(
    point_list: List[Point],
    project_name: str,
    database: Database,
    project_directory: Path,
) -> None:
    """
    Gets all the side images along the given points

    :param project_name: Name to recognize the project
    :param project_directory: Where requested images will be stored
    """

    # creating path object for database
    path = PathForDatabase(
        name=project_name,
        client='Tesla',
        street='needs geocoding',
        city='needs geocoding',
        country='needs geocoding',
    )
    # duplicating last point so it's not ignored in the for loop
    point_list.append(point_list[-1])
    for index, point in enumerate(point_list[:-1]):
        azimuth = get_heading(point_list[index], point_list[index + 1])
        # creating point object for db
        point_for_db = PointForDatabase(
            path_index=index, latitude=point.latitude, longitude=point.longitude
        )
        path.path_relation.append(point_for_db)
        get_both_direction_images(
            point,
            project_directory,
            azimuth,
            index,
            point_for_db,
        )
    database.save(path)

from pathlib import Path
from typing import Tuple

import typer

from jeddah.conversion_functions import create_path
from jeddah.create_path import process_path
from jeddah.database_config import Database
from jeddah.display_map import save_map
from jeddah.point import Point
from jeddah.request_daedal import daedal_from_point
from jeddah.request_images import get_images_along_path
from settings.settings import settings


# GLOBAL VARIABLES
DATABASE_DIRECTORY = settings.database_directory
if not Path.exists(DATABASE_DIRECTORY):
    DATABASE_DIRECTORY.mkdir()

API_KEY = settings.api_key.get_secret_value()

app = typer.Typer()


@app.command()
def main(project_name: str, center_point_as_tuple: Tuple[float, float]) -> None:
    database = Database()
    center_point = Point(
        center_point_as_tuple[0], center_point_as_tuple[1]
    )  # add right database name, depends on final place where img stored
    database.setup()
    project_directory = DATABASE_DIRECTORY / project_name
    project_directory.mkdir(parents=True)
    daedal = daedal_from_point(center_point=center_point, radius=300, threshold=10)
    for id, path in daedal.items():
        path_directory = project_directory / str(id)
        path_directory.mkdir()
        get_images_along_path(path, project_name, database, path_directory)
        save_map(path, path_directory)


def add_path(project_name: str, path: str) -> None:
    database = (
        Database()
    )  # add right database name, depends on final place where img stored
    database.setup()
    project_directory = DATABASE_DIRECTORY / project_name
    project_directory.mkdir(parents=True)
    path_as_point_list = create_path(path)
    processed_path = process_path(path_as_point_list)
    get_images_along_path(processed_path, project_name, database, project_directory)
    save_map(processed_path, project_directory)


if __name__ == "__main__":
    app()

from pathlib import Path
from typing import Tuple

import typer

from jeddah.create_path import process_path
from jeddah.database_config import Database
from jeddah.display_map import save_map
from jeddah.request_daedal import deadal_from_point
from jeddah.request_images import get_images_along_path
from settings.settings import settings


# GLOBAL VARIABLES
DATABASE_DIRECTORY = settings.database_directory
if not Path.exists(DATABASE_DIRECTORY):
    DATABASE_DIRECTORY.mkdir()

API_KEY = settings.api_key.get_secret_value()

app = typer.Typer()


@app.command()
def main(project_name: str, center_point: Tuple[float, float]) -> None:
    database = (
        Database()
    )  # add right database name, depends on final place where img stored
    database.setup()
    project_directory = DATABASE_DIRECTORY / project_name
    project_directory.mkdir(parents=True)
    daedal = deadal_from_point(center_point=center_point, radius=500)
    for id, path in daedal.items():
        processed_path = process_path(path)
        # get_images_along_path(processed_path, project_name, database, project_directory)
        save_map(processed_path, project_directory)


def add_path(project_name: str, path: str) -> None:
    database = (
        Database()
    )  # add right database name, depends on final place where img stored
    database.setup()
    project_directory = DATABASE_DIRECTORY / project_name
    project_directory.mkdir(parents=True)
    processed_path = process_path(path)
    get_images_along_path(processed_path, project_name, database, project_directory)
    save_map(processed_path, project_directory)


if __name__ == '__main__':
    app()

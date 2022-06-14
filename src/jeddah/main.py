import os
from pathlib import Path

from jeddah.create_path import path_process
from jeddah.database_config import Database
from jeddah.display_map import save_map
from jeddah.request_images import get_images_along_path


DATABASE_DIRECTORY = Path(os.environ['DATABASE_PATH'])
if not Path.exists(DATABASE_DIRECTORY):
    DATABASE_DIRECTORY.mkdir()
project_name = 'Rue Grand Lebrun, Caudéran 7'

if __name__ == '__main__':
    database = Database()
    database.setup()
    path = '44.851332,-0.609030|44.850580,-0.606297'
    project_directory = DATABASE_DIRECTORY / project_name
    project_directory.mkdir(parents=True)
    processed_point_list = path_process(path)
    get_images_along_path(processed_point_list, project_name, database, project_directory)
    save_map(processed_point_list, project_directory)

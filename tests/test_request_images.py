import glob
import os
from pathlib import Path
import shutil

from sqlalchemy.orm import sessionmaker

from jeddah.create_path import create_point_list
from jeddah.database_config import Database, Image, PathForDatabase, PointForDatabase
from jeddah.point import Point
from jeddah.request_images import (
    get_both_direction_images,
    get_images_along_path,
    get_metadata,
    get_single_image,
)


DATABASE_DIRECTORY = Path(os.environ['DATABASE_TEST_PATH'])
if not Path.exists(DATABASE_DIRECTORY):
    DATABASE_DIRECTORY.mkdir()

# sqlalchemy database setup
test_database = Database()
test_database.setup('street_view_db_test')


def test_get_single_image():
    point = Point(44.56, 27.83)
    response = get_single_image(point, 120)
    assert response.headers['Content-Type'] == 'image/jpeg'


def test_get_metadata():
    point = Point(48.858984, 2.293419)
    response = get_metadata(point)
    content = response.content
    content_as_str = content.decode()
    index = content_as_str.find('status')
    status_part = content_as_str[index : index + 15]
    is_ok_present = status_part.find('OK')
    assert is_ok_present != -1  # returns -1 if not found


def test_get_both_direction_images_stores_in_db():
    Session = sessionmaker(test_database.engine)
    session = Session()
    if session.query(Image).count() != 0:
        session.query(Image).delete()
        session.commit()
    point = Point(48.858987, 2.293388)
    path = DATABASE_DIRECTORY
    path_for_db = PathForDatabase(
        name='test_path',
        client='test_client',
        street='test_street',
        city='test_city',
        country='swatziland',
    )
    point_for_db = PointForDatabase(path_index=0, latitude=45.2, longitude=24.3)
    path_for_db.path_relation.append(point_for_db)

    get_both_direction_images(
        point,
        path,
        azimuth=100,
        index=0,
        point_for_db=point_for_db,
    )
    test_database.save(path_for_db)

    assert session.query(Image).count() == 2
    session.query(Image).delete()
    session.query(PointForDatabase).delete()
    session.query(PathForDatabase).delete()
    session.commit()


def test_get_both_direction_images_store_locally():
    """
    Verifies that previous test has written the two images in storage
    """
    i = 0
    images_list = DATABASE_DIRECTORY / '*.jpg'
    image_list_str = str(images_list)
    for image in glob.glob(image_list_str):
        i += 1
        os.remove(image)  # temporary
    assert i == 2


def test_get_images_along_path_check_for_project_directory():
    path = '44.851332,-0.609030|44.850580,-0.606297'
    point_list = create_point_list(path)
    test_project_path = DATABASE_DIRECTORY / 'test_project'
    if test_project_path.exists():
        shutil.rmtree(str(test_project_path))
    test_project_path.mkdir(parents=True)
    get_images_along_path(point_list, 'test_project', test_database, test_project_path)
    assert test_project_path.is_dir()

    shutil.rmtree(str(test_project_path))
    Session = sessionmaker(test_database.engine)
    session = Session()

    session.query(Image).delete()
    session.query(PointForDatabase).delete()
    session.query(PathForDatabase).delete()
    session.commit()

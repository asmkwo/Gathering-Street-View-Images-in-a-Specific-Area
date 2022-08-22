import pytest
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists

from jeddah.database_config import Database, Image, PathForDatabase, PointForDatabase


@pytest.fixture
def database():
    database = Database(db_name="street_view_db_testing")
    database.setup()
    yield database
    database.destroy()


@pytest.fixture
def path():
    path_for_db = PathForDatabase(
        name="test_path",
        client="test_client",
        street="test_street",
        city="test_city",
        country="swatziland",
    )
    return path_for_db


def test_setup_database_exists(database):
    assert database_exists(database.engine.url)


def test_setup_table_paths_exists(database):
    inspector = inspect(database.engine)
    assert inspector.has_table("paths")


def test_setup_table_points_exists(database):
    inspector = inspect(database.engine)
    assert inspector.has_table("points")


def test_setup_table_images_exists(database):
    inspector = inspect(database.engine)
    assert inspector.has_table("images")


@pytest.mark.integtest
def test_save_path_effectively_saves_a_path(database, path):
    database.save(path)
    Session = sessionmaker(database.engine)
    session = Session()
    try:
        path_instance = session.query(PathForDatabase).where(
            PathForDatabase.name == "test_path"
        )
        assert path_instance is not None
    finally:
        session.close()


@pytest.mark.integtest
def test_save_point_saves_a_point_in_database(database, path):
    point_1 = PointForDatabase(path_index=0, latitude=45.2, longitude=24.3)
    point_2 = PointForDatabase(path_index=1, latitude=15.9, longitude=67.3)
    path.path_relation.append(point_1)
    path.path_relation.append(point_2)

    database.save(path)
    Session = sessionmaker(database.engine)
    session = Session()

    latitude_for_db_query = 45.2
    longitude_for_db_query = 67.3
    try:
        point_1_instance = session.query(PointForDatabase).where(
            PointForDatabase.latitude == latitude_for_db_query
        )
        point_2_instance = session.query(PointForDatabase).where(
            PointForDatabase.longitude == longitude_for_db_query
        )
        assert point_1_instance is not None
        assert point_2_instance is not None

        session.query(PointForDatabase).delete()
        session.query(PathForDatabase).delete()
        session.commit()
    finally:
        session.close()


@pytest.mark.integtest
def test_save_image_saves_image_details_in_database(database, path):
    point = PointForDatabase(path_index=0, latitude=45.2, longitude=24.3)
    path.path_relation.append(point)

    image_1 = Image(img_path="test_path", heading=120)
    image_2 = Image(img_path="test_path_2", heading=30)
    point.image_relation.append(image_1)
    point.image_relation.append(image_2)
    database.save(path)
    Session = sessionmaker(database.engine)
    session = Session()
    expected_number_of_images = 2
    try:
        assert session.query(Image).count() == expected_number_of_images
        session.query(Image).delete()
        session.query(PointForDatabase).delete()
        session.query(PathForDatabase).delete()
        session.commit()
    finally:
        session.close()

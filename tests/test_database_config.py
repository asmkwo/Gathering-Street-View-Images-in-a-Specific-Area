from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists

from jeddah.database_config import Database, Image, PathForDatabase, PointForDatabase


database = Database()
database.setup(db_name='street_view_db_testing')


def test_setup_database_exists():
    assert database_exists(database.engine.url)


def test_setup_table_paths_exists():
    inspector = inspect(database.engine)
    assert inspector.has_table('paths')


def test_setup_table_points_exists():
    inspector = inspect(database.engine)
    assert inspector.has_table('points')


def test_setup_table_images_exists():
    inspector = inspect(database.engine)
    assert inspector.has_table('images')


def test_path_instance():
    path = PathForDatabase(
        name='test_path',
        client='test_client',
        street='test_street',
        city='test_city',
        country='swatziland',
    )
    assert path.name == 'test_path'


def test_save_path():
    path = PathForDatabase(
        name='test_path',
        client='test_client',
        street='test_street',
        city='test_city',
        country='swatziland',
    )
    database.save(path)
    Session = sessionmaker(database.engine)
    session = Session()
    path_instance = session.query(PathForDatabase).where(
        PathForDatabase.name == 'test_path'
    )
    assert path_instance is not None


def test_point_instance():

    point = PointForDatabase(path_index=0, latitude=45.2, longitude=24.3)
    assert point.latitude == 45.2


def test_save_point():
    # need to create a path first as both are linked by backref
    path = PathForDatabase(
        name='test_path',
        client='test_client',
        street='test_street',
        city='test_city',
        country='swatziland',
    )

    point_1 = PointForDatabase(path_index=0, latitude=45.2, longitude=24.3)
    point_2 = PointForDatabase(path_index=1, latitude=15.9, longitude=67.3)
    path.path_relation.append(point_1)
    path.path_relation.append(point_2)

    database.save(path)
    Session = sessionmaker(database.engine)
    session = Session()
    point_1_instance = session.query(PointForDatabase).where(
        PointForDatabase.latitude == 45.2
    )
    point_2_instance = session.query(PointForDatabase).where(
        PointForDatabase.longitude == 67.3
    )
    assert point_1_instance is not None
    assert point_2_instance is not None

    session.query(PointForDatabase).delete()
    session.query(PathForDatabase).delete()
    session.commit()


def test_image_instance():
    image = Image(img_path='test_path', heading=120)
    assert image.heading == 120


def test_save_image():
    path = PathForDatabase(
        name='test_path',
        client='test_client',
        street='test_street',
        city='test_city',
        country='swatziland',
    )
    point = PointForDatabase(path_index=0, latitude=45.2, longitude=24.3)
    path.path_relation.append(point)

    image_1 = Image(img_path='test_path', heading=120)
    image_2 = Image(img_path='test_path_2', heading=30)
    point.image_relation.append(image_1)
    point.image_relation.append(image_2)
    database.save(path)
    Session = sessionmaker(database.engine)
    session = Session()

    assert session.query(Image).count() == 2
    session.query(Image).delete()
    session.query(PointForDatabase).delete()
    session.query(PathForDatabase).delete()
    session.commit()

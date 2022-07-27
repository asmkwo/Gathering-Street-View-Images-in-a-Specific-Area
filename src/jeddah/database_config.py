from typing import Any, List

from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    Integer,
    Sequence,
    String,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy_utils import create_database, database_exists

from settings.settings import settings


Base = declarative_base()


class Image(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    id_point = Column(Integer, ForeignKey('points.id_point'))
    img_path = Column(String)
    heading = Column(Integer)

    def __repr__(self) -> str:
        return (
            f"<Image(id={self.id}, id_of_360_view={self.id_point}, "
            f"image_path='{self.img_path}', heading_angle={self.heading})> "
        )


class PointForDatabase(Base):
    __tablename__ = 'points'
    id_point = Column(Integer, Sequence('id_point_seq'), primary_key=True)
    id_path = Column(Integer, ForeignKey('paths.id_path'))
    path_index = Column(Integer)  # order in the path
    latitude = Column(Float)
    longitude = Column(Float)
    # defining 1 to 2 relationship
    image_relation: List[Image] = relationship(
        'Image',
        backref='points',
        lazy='select',
        cascade='all, delete-orphan',
        collection_class=list,
    )

    def __repr__(self) -> str:
        return (
            f"<PointForDatabase(id_point={self.id_point}, id_of_path={self.id_path},"
            f" path_index={self.path_index}, latitude={self.latitude}, "
            f"longitude={ self.longitude})>"
        )


class PathForDatabase(Base):
    __tablename__ = 'paths'
    id_path = Column(Integer, Sequence('id_paths_seq'), primary_key=True)
    name = Column(String)
    client = Column(String)
    street = Column(String)
    city = Column(String)
    country = Column(String)
    # 1 to n relationship
    path_relation: List[PointForDatabase] = relationship(
        'PointForDatabase',
        backref='paths',
        lazy='select',
        cascade='all, delete-orphan',
        collection_class=list,
    )

    def __repr__(self) -> str:
        return (
            f"<PathForDatabase(id_path={self.id_path}, name_of_the_path='{self.name}',"
            f" client='{self.client}', street='{ self.street}',"
            f" city='{self.city}', country='{self.country}')>"
        )


class Database:
    def __init__(self, db_name: str = 'street_view_db') -> None:
        db_host = settings.postgresql_hostname
        db_port = settings.postgresql_port
        self.url = (
            f"postgresql+psycopg2://postgres:postgres@{db_host}:{db_port}/{db_name}"
        )
        self.engine = create_engine(self.url, echo=True)

    def setup(self) -> Any:

        if not database_exists(self.engine.url):
            create_database(self.engine.url)

        Base.metadata.create_all(self.engine)

        Image.__table__.create(bind=self.engine, checkfirst=True)
        PointForDatabase.__table__.create(bind=self.engine, checkfirst=True)
        PathForDatabase.__table__.create(bind=self.engine, checkfirst=True)

        return self.engine

    def save(self, object_to_save: Base) -> None:  # changed from Any to Base, workin ?
        Session = sessionmaker(self.engine)
        session = Session()
        try:
            session.add(object_to_save)
            session.commit()
        finally:
            session.close()

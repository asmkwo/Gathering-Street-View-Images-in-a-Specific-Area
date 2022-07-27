from pathlib import Path

from pydantic import BaseSettings, Field, SecretStr


class Settings(BaseSettings):
    # Map

    maps_base: str = "https://maps.googleapis.com/maps/api/staticmap?"
    meta_base: str = 'https://maps.googleapis.com/maps/api/streetview/metadata?'
    pic_base: str = 'https://maps.googleapis.com/maps/api/streetview?'
    roads_base: str = 'https://roads.googleapis.com/v1/snapToRoads?'

    # Api key
    api_key: SecretStr = Field('')

    # Database
    database_directory: Path = Path('/home/asmkwo/Documents/Upciti/jeddah/database')

    # PostgreSQL
    postgresql_hostname: str = "127.0.0.1"
    postgresql_username: str = "postgres"
    postgresql_password: str = "postgres"
    postgresql_port: int = 5432


settings = Settings()

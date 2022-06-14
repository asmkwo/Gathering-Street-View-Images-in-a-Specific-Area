import math
from typing import Any


class Point:
    def __init__(self, latitude: float, longitude: float):
        # assert -90 < latitude < 90
        # assert -180 < longitude < 180
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self) -> str:
        return "Latitude : " + str(self.latitude) + " Longitude : " + str(self.longitude)

    def __eq__(self, other: Any) -> bool:
        """
        :raises: TypeError
        """
        if isinstance(other, Point):
            if math.isclose(self.latitude, other.latitude) and math.isclose(
                self.longitude, other.longitude
            ):
                return True
            else:
                return False
        else:
            raise TypeError('Wrong type comparison. You are not comparing two points. ')

    def to_simple_string(self) -> str:
        """
        Turns the latitude and longitude into string a simple string for the request
        module
        """
        return str(self.latitude) + "," + str(self.longitude)

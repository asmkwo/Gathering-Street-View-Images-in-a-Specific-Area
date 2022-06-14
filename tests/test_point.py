from jeddah.point import Point


def test_point():
    point = Point(44.56, 27.83)
    assert point.latitude == 44.56
    assert point.longitude == 27.83


def test_to_simple_string():
    point = Point(44.56, 27.83)
    assert point.to_simple_string() == '44.56,27.83'


def test__eq__():
    point_1 = Point(44.85130749493737, -0.6090405982459559)
    point_2 = Point(44.85130749493737, -0.6090405982459559)
    assert point_1 == point_2

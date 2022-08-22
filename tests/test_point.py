from jeddah.point import Point


def test_eq_effectively_overrides_equality_test_method():
    point_1 = Point(44.85130749493737, -0.6090405982459559)
    point_2 = Point(44.85130749493737, -0.6090405982459559)
    assert point_1 == point_2


def test_str_returns_the_expected_string_format():
    point_1 = Point(44.85130749493737, -0.6090405982459559)
    assert str(point_1) == "44.85130749493737,-0.6090405982459559"

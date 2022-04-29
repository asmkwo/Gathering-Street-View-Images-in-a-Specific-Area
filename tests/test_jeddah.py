from jeddah import __version__
import jeddah.__init__ as script


def test_version():
    assert __version__ == '0.1.0'


def test_check_function():
    assert script.check_function(2) == 4

import os
from pathlib import Path

import requests

from jeddah.create_path import create_path
from jeddah.display_map import get_map, save_map


DATABASE_DIRECTORY = Path(os.getcwd())
path = (
    "48.860597,2.349461|48.862039,2.350262|48.863353,2.350998|48.862670,2.354307"
    "|48.862385,2.357433"
)
point_list = create_path(path)


def test_get_map_effectively_returns_a_map_image(monkeypatch):
    def mock_return(link_base_for_api, params):
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response.headers = {
            'Content-Type': 'image/png',
            'Date': 'Fri, 29 Jul 2022 14:41:35 GMT',
            'Expires': 'Sat, 30 Jul 2022 14:41:35 GMT',
            'Cache-Control': 'public, max-age=86400',
            'Vary': 'Accept-Language',
            'Access-Control-Allow-Origin': '*',
            'Server': 'scaffolding on HTTPServer2',
            'Content-Length': '116557',
            'X-XSS-Protection': '0',
            'X-Frame-Options': 'SAMEORIGIN',
            'Server-Timing': 'gfet4t7; dur=84',
            'Alt-Svc': 'h3=":443"; ma=2592000,h3-29=":443"; '
            'ma=2592000,h3-Q050=":443"; ma=2592000,h3-Q046=":443"'
            '; ma=2592000,h3-Q043=":443"; ma=2592000,quic=":443"; '
            'ma=2592000; v="46,43"',
        }
        mock_response.encoding = None
        mock_response.reason = "OK"
        return mock_response

    monkeypatch.setattr(requests, "get", mock_return)

    response = get_map(point_list)
    expected_type = "image/png"
    expected_date = "Fri, 29 Jul 2022 14:41:35 GMT"

    assert response.headers["Content-Type"] == expected_type
    assert response.headers["Date"] == expected_date


def test_save_map():
    save_map(point_list, DATABASE_DIRECTORY)
    map_path = DATABASE_DIRECTORY / "map.png"
    assert map_path.is_file()
    os.remove(str(map_path))  # temporary

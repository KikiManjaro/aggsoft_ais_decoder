import pytest
from unittest.mock import AsyncMock
import httpx

SAMPLE_HTML_RESPONSE = """<!DOCTYPE html>
<html>
<head><title>AIS Decoder</title></head>
<body>
<table>
<tr><th>Name</th><th>Value</th></tr>
<tr><td>MMSI:</td><td>226666007</td></tr>
<tr><td>Ship Name:</td><td>TEST VESSEL</td></tr>
<tr><td>Callsign:</td><td>TST1234</td></tr>
<tr><td>IMO Number:</td><td>1234567</td></tr>
<tr><td>Vessel Type:</td><td>37</td></tr>
<tr><td>Latitude:</td><td>48.8566</td></tr>
<tr><td>Longitude:</td><td>2.3522</td></tr>
<tr><td>Speed Over Ground:</td><td>10.5</td></tr>
<tr><td>Course Over Ground:</td><td>180.0</td></tr>
<tr><td>Heading:</td><td>90</td></tr>
<tr><td>Navigation Status:</td><td>0</td></tr>
<tr><td>Destination:</td><td>PARIS</td></tr>
<tr><td>ETA:</td><td>12:00</td></tr>
<tr><td>Dimension to Bow:</td><td>10</td></tr>
<tr><td>Dimension to Stern:</td><td>10</td></tr>
<tr><td>Dimension to Port:</td><td>3</td></tr>
<tr><td>Dimension to Starboard:</td><td>3</td></tr>
</table>
</body>
</html>"""

SAMPLE_HTML_MINIMAL = """<!DOCTYPE html>
<html>
<body>
<table>
<tr><td>MMSI:</td><td>987654321</td></tr>
<tr><td>Latitude:</td><td>35.6762</td></tr>
<tr><td>Longitude:</td><td>139.6503</td></tr>
</table>
</body>
</html>"""

SAMPLE_HTML_NO_DATA = """<!DOCTYPE html>
<html>
<body>
<h1>No data found</h1>
</body>
</html>"""

SAMPLE_NMEA_MSG1 = "!AIVDM,1,1,,A,13u@ND0P01PJ=0lMH0nN20pl,0*7D"
SAMPLE_NMEA_MSG5 = "!AIVDO,1,1,,A,703ltL0Q7D@GH0l0e0O,0*2F"


@pytest.fixture
def sample_html_response():
    return SAMPLE_HTML_RESPONSE


@pytest.fixture
def sample_html_minimal():
    return SAMPLE_HTML_MINIMAL


@pytest.fixture
def sample_html_no_data():
    return SAMPLE_HTML_NO_DATA


@pytest.fixture
def sample_nmea_msg1():
    return SAMPLE_NMEA_MSG1


@pytest.fixture
def sample_nmea_msg5():
    return SAMPLE_NMEA_MSG5


@pytest.fixture
def mock_httpx_success(sample_html_response):
    return AsyncMock(
        spec=httpx.AsyncClient,
        status_code=200,
        text=sample_html_response,
        is_closed=False,
    )


@pytest.fixture
def expected_ship_data():
    return {
        "mmsi": "226666007",
        "ship_name": "TEST VESSEL",
        "callsign": "TST1234",
        "imo_number": "1234567",
        "vessel_type": "37",
        "vessel_type_description": "Pleasure craft",
        "position": {"latitude": 48.8566, "longitude": 2.3522},
        "speed_over_ground": 10.5,
        "course_over_ground": 180.0,
        "heading": 90,
        "navigation_status": "Under way using engine",
        "destination": "PARIS",
        "eta": "12:00",
        "dimensions": {
            "to_bow": 10,
            "to_stern": 10,
            "to_port": 3,
            "to_starboard": 3,
        },
    }
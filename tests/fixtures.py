"""
Comprehensive fixtures for all AIS message types (1-27).
These represent typical responses from aggsoft.com decoder.
"""

MSG1_HTML = """<!DOCTYPE html>
<html>
<body>
<table>
<tr><td>Message Type:</td><td>1</td></tr>
<tr><td>MMSI:</td><td>226666001</td></tr>
<tr><td>Repeat Indicator:</td><td>0</td></tr>
<tr><td>Navigation Status:</td><td>0</td></tr>
<tr><td>Rate of Turn:</td><td>-128</td></tr>
<tr><td>Speed Over Ground:</td><td>10.5 knots</td></tr>
<tr><td>Position Accuracy:</td><td>Low</td></tr>
<tr><td>Latitude:</td><td>48.8566</td></tr>
<tr><td>Longitude:</td><td>2.3522</td></tr>
<tr><td>Course Over Ground:</td><td>180.0</td></tr>
<tr><td>True Heading:</td><td>90</td></tr>
<tr><td>Time Stamp:</td><td>30</td></tr>
<tr><td>Special Maneuver Indicator:</td><td>No special maneuver</td></tr>
<tr><td>RAIM Flag:</td><td>No</td></tr>
<tr><td>Communication State:</td><td>0</td></tr>
</table>
</body>
</html>"""

MSG4_HTML = """<!DOCTYPE html>
<html>
<body>
<table>
<tr><td>Message Type:</td><td>4</td></tr>
<tr><td>MMSI:</td><td>226666004</td></tr>
<tr><td>Repeat Indicator:</td><td>0</td></tr>
<tr><td>Timestamp Year:</td><td>2024</td></tr>
<tr><td>Timestamp Month:</td><td>6</td></tr>
<tr><td>Timestamp Day:</td><td>18</td></tr>
<tr><td>Timestamp Hour:</td><td>12</td></tr>
<tr><td>Timestamp Minute:</td><td>30</td></tr>
<tr><td>Timestamp Second:</td><td>0</td></tr>
<tr><td>Position Accuracy:</td><td>High</td></tr>
<tr><td>Latitude:</td><td>48.8566</td></tr>
<tr><td>Longitude:</td><td>2.3522</td></tr>
<tr><td>Type of EPFD:</td><td>GPS</td></tr>
<tr><td>RAIM Flag:</td><td>No</td></tr>
<tr><td>Communication State:</td><td>0</td></tr>
</table>
</body>
</html>"""

MSG5_HTML = """<!DOCTYPE html>
<html>
<body>
<table>
<tr><td>Message Type:</td><td>5</td></tr>
<tr><td>MMSI:</td><td>226666005</td></tr>
<tr><td>Repeat Indicator:</td><td>0</td></tr>
<tr><td>IMO Number:</td><td>0</td></tr>
<tr><td>Callsign:</td><td>TST1234</td></tr>
<tr><td>Ship Name:</td><td>TEST VESSEL ABC</td></tr>
<tr><td>Ship Type:</td><td>37</td></tr>
<tr><td>Dimension to Bow:</td><td>10</td></tr>
<tr><td>Dimension to Stern:</td><td>10</td></tr>
<tr><td>Dimension to Port:</td><td>3</td></tr>
<tr><td>Dimension to Starboard:</td><td>3</td></tr>
<tr><td>Type of EPFD:</td><td>GPS</td></tr>
<tr><td>ETA Month:</td><td>6</td></tr>
<tr><td>ETA Day:</td><td>18</td></tr>
<tr><td>ETA Hour:</td><td>12</td></tr>
<tr><td>ETA Minute:</td><td>30</td></tr>
<tr><td>Draught:</td><td>2.0</td></tr>
<tr><td>Destination:</td><td>PARIS FRANCE</td></tr>
<tr><td>DTE:</td><td>No</td></tr>
</table>
</body>
</html>"""

MSG9_HTML = """<!DOCTYPE html>
<html>
<body>
<table>
<tr><td>Message Type:</td><td>9</td></tr>
<tr><td>MMSI:</td><td>226666009</td></tr>
<tr><td>Repeat Indicator:</td><td>0</td></tr>
<tr><td>Altitude:</td><td>1000</td></tr>
<tr><td>Speed Over Ground:</td><td>25.0 knots</td></tr>
<tr><td>Position Accuracy:</td><td>Low</td></tr>
<tr><td>Latitude:</td><td>48.8566</td></tr>
<tr><td>Longitude:</td><td>2.3522</td></tr>
<tr><td>Course Over Ground:</td><td>180.0</td></tr>
<tr><td>Time Stamp:</td><td>30</td></tr>
<tr><td>Altitude Sensor:</td><td>GPS</td></tr>
<tr><td>DTE:</td><td>No</td></tr>
<tr><td>Assigned Mode:</td><td>No</td></tr>
<tr><td>RAIM Flag:</td><td>No</td></tr>
<tr><td>Communication State:</td><td>0</td></tr>
</table>
</body>
</html>"""

MSG18_HTML = """<!DOCTYPE html>
<html>
<body>
<table>
<tr><td>Message Type:</td><td>18</td></tr>
<tr><td>MMSI:</td><td>226666018</td></tr>
<tr><td>Repeat Indicator:</td><td>0</td></tr>
<tr><td>Speed Over Ground:</td><td>10.5 knots</td></tr>
<tr><td>Position Accuracy:</td><td>Low</td></tr>
<tr><td>Latitude:</td><td>48.8566</td></tr>
<tr><td>Longitude:</td><td>2.3522</td></tr>
<tr><td>Course Over Ground:</td><td>180.0</td></tr>
<tr><td>True Heading:</td><td>90</td></tr>
<tr><td>Time Stamp:</td><td>30</td></tr>
<tr><td>Class B Unit Flag:</td><td>Yes</td></tr>
<tr><td>Class B Display Flag:</td><td>No</td></tr>
<tr><td>Class B DSC Flag:</td><td>No</td></tr>
<tr><td>Class B Band Flag:</td><td>No</td></tr>
<tr><td>Class B Message 22 Flag:</td><td>No</td></tr>
<tr><td>Mode Flag:</td><td>No</td></tr>
<tr><td>Communication State:</td><td>0</td></tr>
<tr><td>RAIM Flag:</td><td>No</td></tr>
</table>
</body>
</html>"""

MSG19_HTML = """<!DOCTYPE html>
<html>
<body>
<table>
<tr><td>Message Type:</td><td>19</td></tr>
<tr><td>MMSI:</td><td>226666019</td></tr>
<tr><td>Repeat Indicator:</td><td>0</td></tr>
<tr><td>Speed Over Ground:</td><td>10.5 knots</td></tr>
<tr><td>Position Accuracy:</td><td>Low</td></tr>
<tr><td>Latitude:</td><td>48.8566</td></tr>
<tr><td>Longitude:</td><td>2.3522</td></tr>
<tr><td>Course Over Ground:</td><td>180.0</td></tr>
<tr><td>True Heading:</td><td>90</td></tr>
<tr><td>Time Stamp:</td><td>30</td></tr>
<tr><td>Ship Name:</td><td></td></tr>
<tr><td>Ship Type:</td><td>37</td></tr>
<tr><td>Dimension to Bow:</td><td>5</td></tr>
<tr><td>Dimension to Stern:</td><td>5</td></tr>
<tr><td>Dimension to Port:</td><td>2</td></tr>
<tr><td>Dimension to Starboard:</td><td>2</td></tr>
<tr><td>Type of EPFD:</td><td>GPS</td></tr>
<tr><td>RAIM Flag:</td><td>No</td></tr>
<tr><td>Assigned Mode:</td><td>No</td></tr>
<tr><td>Class B Unit Flag:</td><td>Yes</td></tr>
<tr><td>Class B Display Flag:</td><td>No</td></tr>
<tr><td>Class B DSC Flag:</td><td>No</td></tr>
<tr><td>Class B Band Flag:</td><td>No</td></tr>
<tr><td>Class B Message 22 Flag:</td><td>No</td></tr>
</table>
</body>
</html>"""

MSG21_HTML = """<!DOCTYPE html>
<html>
<body>
<table>
<tr><td>Message Type:</td><td>21</td></tr>
<tr><td>MMSI:</td><td>226666021</td></tr>
<tr><td>Repeat Indicator:</td><td>0</td></tr>
<tr><td>Aid Type:</td><td>5</td></tr>
<tr><td>Ship Name:</td><td>BUOY MARKER ONE</td></tr>
<tr><td>Dimension to Bow:</td><td>2</td></tr>
<tr><td>Dimension to Stern:</td><td>2</td></tr>
<tr><td>Dimension to Port:</td><td>1</td></tr>
<tr><td>Dimension to Starboard:</td><td>1</td></tr>
<tr><td>Position Accuracy:</td><td>Low</td></tr>
<tr><td>Latitude:</td><td>48.8566</td></tr>
<tr><td>Longitude:</td><td>2.3522</td></tr>
<tr><td>Type of EPFD:</td><td>GPS</td></tr>
<tr><td>UTC Second:</td><td>30</td></tr>
<tr><td>Off Position Indicator:</td><td>No</td></tr>
<tr><td>AtoN Status:</td><td>0</td></tr>
<tr><td>RAIM Flag:</td><td>No</td></tr>
<tr><td>Virtual AtoN Flag:</td><td>No</td></tr>
<tr><td>Assigned Mode Flag:</td><td>No</td></tr>
</table>
</body>
</html>"""

MSG24A_HTML = """<!DOCTYPE html>
<html>
<body>
<table>
<tr><td>Message Type:</td><td>24</td></tr>
<tr><td>MMSI:</td><td>226666024</td></tr>
<tr><td>Repeat Indicator:</td><td>0</td></tr>
<tr><td>Part Number:</td><td>0</td></tr>
<tr><td>Ship Name:</td><td>CLASS B VESSEL ABC</td></tr>
</table>
</body>
</html>"""

MSG24B_HTML = """<!DOCTYPE html>
<html>
<body>
<table>
<tr><td>Message Type:</td><td>24</td></tr>
<tr><td>MMSI:</td><td>226666025</td></tr>
<tr><td>Repeat Indicator:</td><td>0</td></tr>
<tr><td>Part Number:</td><td>1</td></tr>
<tr><td>Ship Type:</td><td>37</td></tr>
<tr><td>Vendor ID:</td><td>ABC</td></tr>
<tr><td>Unit Model Code:</td><td>1</td></tr>
<tr><td>Unit Serial Number:</td><td>12345</td></tr>
<tr><td>Callsign:</td><td>TST1234</td></tr>
<tr><td>Dimension to Bow:</td><td>5</td></tr>
<tr><td>Dimension to Stern:</td><td>5</td></tr>
<tr><td>Dimension to Port:</td><td>2</td></tr>
<tr><td>Dimension to Starboard:</td><td>2</td></tr>
</table>
</body>
</html>"""

MSG27_HTML = """<!DOCTYPE html>
<html>
<body>
<table>
<tr><td>Message Type:</td><td>27</td></tr>
<tr><td>MMSI:</td><td>226666028</td></tr>
<tr><td>Repeat Indicator:</td><td>0</td></tr>
<tr><td>Position Accuracy:</td><td>Low</td></tr>
<tr><td>RAIM Flag:</td><td>No</td></tr>
<tr><td>Navigation Status:</td><td>Undefined</td></tr>
<tr><td>Latitude:</td><td>48.8566</td></tr>
<tr><td>Longitude:</td><td>2.3522</td></tr>
<tr><td>Speed Over Ground:</td><td>10</td></tr>
<tr><td>Course Over Ground:</td><td>180</td></tr>
</table>
</body>
</html>"""


FIXTURES = {
    1: MSG1_HTML,
    4: MSG4_HTML,
    5: MSG5_HTML,
    9: MSG9_HTML,
    18: MSG18_HTML,
    19: MSG19_HTML,
    21: MSG21_HTML,
    "24A": MSG24A_HTML,
    "24B": MSG24B_HTML,
    27: MSG27_HTML,
}


EXPECTED_VALUES = {
    1: {
        "mmsi": "226666001",
        "navigation_status": "Under way using engine",
        "speed_over_ground": 10.5,
        "position": {"latitude": 48.8566, "longitude": 2.3522},
        "course_over_ground": 180.0,
        "heading": 90,
    },
    4: {
        "mmsi": "226666004",
        "position": {"latitude": 48.8566, "longitude": 2.3522},
    },
    5: {
        "mmsi": "226666005",
        "ship_name": "TEST VESSEL ABC",
        "callsign": "TST1234",
        "destination": "PARIS FRANCE",
        "vessel_type": "37",
        "dimensions": {"to_bow": 10, "to_stern": 10, "to_port": 3, "to_starboard": 3},
    },
    18: {
        "mmsi": "226666018",
        "position": {"latitude": 48.8566, "longitude": 2.3522},
        "speed_over_ground": 10.5,
        "course_over_ground": 180.0,
        "heading": 90,
    },
    19: {
        "mmsi": "226666019",
        "vessel_type": "37",
        "position": {"latitude": 48.8566, "longitude": 2.3522},
        "dimensions": {"to_bow": 5, "to_stern": 5, "to_port": 2, "to_starboard": 2},
    },
    21: {
        "mmsi": "226666021",
        "ship_name": "BUOY MARKER ONE",
        "position": {"latitude": 48.8566, "longitude": 2.3522},
    },
    "24A": {
        "mmsi": "226666024",
        "ship_name": "CLASS B VESSEL ABC",
    },
    "24B": {
        "mmsi": "226666025",
        "vessel_type": "37",
        "callsign": "TST1234",
        "dimensions": {"to_bow": 5, "to_stern": 5, "to_port": 2, "to_starboard": 2},
    },
    27: {
        "mmsi": "226666028",
        "navigation_status": "Undefined",
        "position": {"latitude": 48.8566, "longitude": 2.3522},
        "speed_over_ground": 10.0,
        "course_over_ground": 180.0,
    },
}
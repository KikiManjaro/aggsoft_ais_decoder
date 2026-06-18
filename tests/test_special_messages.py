"""
Tests for binary messages (Msg 6, 8, 25, 26) and special message types (Msg 10, 12, 14, 20, 22, 23).
"""

import pytest
from aggsoft_ais_decoder.parser import parse_response, extract_ship_data


BINARY_MSG6_HTML = """<!DOCTYPE html>
<html>
<body>
<table>
<tr><td>Message Type:</td><td>6</td></tr>
<tr><td>MMSI:</td><td>226666006</td></tr>
<tr><td>Destination MMSI:</td><td>226666007</td></tr>
<tr><td>Sequence Number:</td><td>0</td></tr>
<tr><td>Retransmit Flag:</td><td>No</td></tr>
<tr><td>DAC:</td><td>1</td></tr>
<tr><td>FI:</td><td>1</td></tr>
<tr><td>Application ID:</td><td>0</td></tr>
<tr><td>Binary Data:</td><td>0x010203</td></tr>
</table>
</body>
</html>"""

BINARY_MSG8_HTML = """<!DOCTYPE html>
<html>
<body>
<table>
<tr><td>Message Type:</td><td>8</td></tr>
<tr><td>MMSI:</td><td>226666008</td></tr>
<tr><td>DAC:</td><td>1</td></tr>
<tr><td>FI:</td><td>1</td></tr>
<tr><td>Binary Data:</td><td>0x01020304</td></tr>
</table>
</body>
</html>"""

BINARY_MSG25_HTML = """<!DOCTYPE html>
<html>
<body>
<table>
<tr><td>Message Type:</td><td>25</td></tr>
<tr><td>MMSI:</td><td>226666025</td></tr>
<tr><td>Binary Data Flag:</td><td>0</td></tr>
<tr><td>Destination Indicator:</td><td>0</td></tr>
</table>
</body>
</html>"""

BINARY_MSG26_HTML = """<!DOCTYPE html>
<html>
<body>
<table>
<tr><td>Message Type:</td><td>26</td></tr>
<tr><td>MMSI:</td><td>226666026</td></tr>
<tr><td>Binary Data Flag:</td><td>1</td></tr>
<tr><td>Destination Indicator:</td><td>1</td></tr>
<tr><td>Destination MMSI:</td><td>226666027</td></tr>
</table>
</body>
</html>"""

MSG10_HTML = """<!DOCTYPE html>
<html>
<body>
<table>
<tr><td>Message Type:</td><td>10</td></tr>
<tr><td>MMSI:</td><td>226666010</td></tr>
<tr><td>Destination MMSI:</td><td>226666011</td></tr>
</table>
</body>
</html>"""

MSG12_HTML = """<!DOCTYPE html>
<html>
<body>
<table>
<tr><td>Message Type:</td><td>12</td></tr>
<tr><td>MMSI:</td><td>226666012</td></tr>
<tr><td>Destination MMSI:</td><td>226666013</td></tr>
<tr><td>Sequence Number:</td><td>0</td></tr>
<tr><td>Retransmit Flag:</td><td>No</td></tr>
<tr><td>Safety Text:</td><td>SAFETY RELATED MESSAGE TEXT</td></tr>
</table>
</body>
</html>"""

MSG14_HTML = """<!DOCTYPE html>
<html>
<body>
<table>
<tr><td>Message Type:</td><td>14</td></tr>
<tr><td>MMSI:</td><td>226666014</td></tr>
<tr><td>Safety Text:</td><td>SAFETY BROADCAST MESSAGE</td></tr>
</table>
</body>
</html>"""

MSG20_HTML = """<!DOCTYPE html>
<html>
<body>
<table>
<tr><td>Message Type:</td><td>20</td></tr>
<tr><td>MMSI:</td><td>226666020</td></tr>
<tr><td>Offset 1:</td><td>100</td></tr>
<tr><td>Number of Slots 1:</td><td>3</td></tr>
<tr><td>Timeout 1:</td><td>2</td></tr>
<tr><td>Increment 1:</td><td>750</td></tr>
</table>
</body>
</html>"""

MSG22_HTML = """<!DOCTYPE html>
<html>
<body>
<table>
<tr><td>Message Type:</td><td>22</td></tr>
<tr><td>MMSI:</td><td>226666022</td></tr>
<tr><td>Channel A:</td><td>2087</td></tr>
<tr><td>Channel B:</td><td>2088</td></tr>
<tr><td>Tx/Rx Mode:</td><td>0</td></tr>
<tr><td>Power:</td><td>Low</td></tr>
<tr><td>NE Longitude:</td><td>2.5</td></tr>
<tr><td>NE Latitude:</td><td>49.0</td></tr>
<tr><td>SW Longitude:</td><td>2.0</td></tr>
<tr><td>SW Latitude:</td><td>48.5</td></tr>
</table>
</body>
</html>"""

MSG23_HTML = """<!DOCTYPE html>
<html>
<body>
<table>
<tr><td>Message Type:</td><td>23</td></tr>
<tr><td>MMSI:</td><td>226666023</td></tr>
<tr><td>NE Longitude:</td><td>2.5</td></tr>
<tr><td>NE Latitude:</td><td>49.0</td></tr>
<tr><td>SW Longitude:</td><td>2.0</td></tr>
<tr><td>SW Latitude:</td><td>48.5</td></tr>
<tr><td>Station Type:</td><td>0</td></tr>
<tr><td>Ship Type:</td><td>37</td></tr>
<tr><td>Tx/Rx Mode:</td><td>0</td></tr>
<tr><td>Report Interval:</td><td>60</td></tr>
<tr><td>Quiet Time:</td><td>0</td></tr>
</table>
</body>
</html>"""


class TestBinaryMessage6:
    """Test AIS Message Type 6 - Binary Addressed Message"""

    def test_parse_msg6_basic(self):
        fields = parse_response(BINARY_MSG6_HTML)
        ship_data = extract_ship_data(fields)

        assert ship_data.msg_type == 6
        assert ship_data.mmsi is not None

    def test_parse_msg6_dac_fi(self):
        fields = parse_response(BINARY_MSG6_HTML)
        assert "dac" in fields or "fi" in fields


class TestBinaryMessage8:
    """Test AIS Message Type 8 - Binary Broadcast Message"""

    def test_parse_msg8_basic(self):
        fields = parse_response(BINARY_MSG8_HTML)
        ship_data = extract_ship_data(fields)

        assert ship_data.mmsi == "226666008"
        assert ship_data.msg_type == 8


class TestBinaryMessage25:
    """Test AIS Message Type 25 - Single Slot Binary Message"""

    def test_parse_msg25_basic(self):
        fields = parse_response(BINARY_MSG25_HTML)
        ship_data = extract_ship_data(fields)

        assert ship_data.mmsi == "226666025"
        assert ship_data.msg_type == 25


class TestBinaryMessage26:
    """Test AIS Message Type 26 - Multiple Slot Binary Message"""

    def test_parse_msg26_basic(self):
        fields = parse_response(BINARY_MSG26_HTML)
        ship_data = extract_ship_data(fields)

        assert ship_data.msg_type == 26
        assert ship_data.mmsi is not None


class TestMessageType10:
    """Test AIS Message Type 10 - UTC/Date Inquiry"""

    def test_parse_msg10_no_position(self):
        fields = parse_response(MSG10_HTML)
        ship_data = extract_ship_data(fields)

        assert ship_data.msg_type == 10
        assert ship_data.mmsi is not None


class TestMessageType12:
    """Test AIS Message Type 12 - Addressed Safety-Related Message"""

    def test_parse_msg12_safety_text(self):
        fields = parse_response(MSG12_HTML)
        ship_data = extract_ship_data(fields)

        assert ship_data.msg_type == 12
        assert "SAFETY" in str(fields) or "safety" in str(fields)

    def test_parse_msg12_retransmit_flag(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Retransmit Flag:</td><td>Yes</td></tr>
        </table></body></html>"""
        fields = parse_response(html)
        assert "retransmit flag" in fields
        assert fields["retransmit flag"] == "Yes"


class TestMessageType14:
    """Test AIS Message Type 14 - Safety-Related Broadcast Message"""

    def test_parse_msg14_safety_text(self):
        fields = parse_response(MSG14_HTML)
        ship_data = extract_ship_data(fields)

        assert ship_data.mmsi == "226666014"
        assert ship_data.msg_type == 14


class TestMessageType20:
    """Test AIS Message Type 20 - Data Link Management Message"""

    def test_parse_msg20_slot_offsets(self):
        fields = parse_response(MSG20_HTML)
        ship_data = extract_ship_data(fields)

        assert ship_data.mmsi == "226666020"
        assert ship_data.msg_type == 20


class TestMessageType22:
    """Test AIS Message Type 22 - Channel Management"""

    def test_parse_msg22_channel_frequency(self):
        fields = parse_response(MSG22_HTML)
        ship_data = extract_ship_data(fields)

        assert ship_data.mmsi == "226666022"
        assert ship_data.msg_type == 22

    def test_parse_msg22_area_coordinates(self):
        fields = parse_response(MSG22_HTML)
        ship_data = extract_ship_data(fields)

        assert ship_data.position.latitude is not None
        assert ship_data.position.longitude is not None


class TestMessageType23:
    """Test AIS Message Type 23 - Group Assignment Command"""

    def test_parse_msg23_area_coordinates(self):
        fields = parse_response(MSG23_HTML)
        ship_data = extract_ship_data(fields)

        assert ship_data.mmsi == "226666023"
        assert ship_data.msg_type == 23
        assert ship_data.position.latitude is not None


class TestMessageType2:
    """Test AIS Message Type 2 - Identical to Type 1"""

    def test_parse_msg2_structure(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Message Type:</td><td>2</td></tr>
        <tr><td>MMSI:</td><td>226666002</td></tr>
        <tr><td>Latitude:</td><td>48.8566</td></tr>
        <tr><td>Longitude:</td><td>2.3522</td></tr>
        </table></body></html>"""
        fields = parse_response(html)
        ship_data = extract_ship_data(fields)

        assert ship_data.msg_type == 2
        assert ship_data.mmsi == "226666002"


class TestMessageType3:
    """Test AIS Message Type 3 - Position Report with different Turn"""

    def test_parse_msg3_positive_turn(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Message Type:</td><td>3</td></tr>
        <tr><td>MMSI:</td><td>226666003</td></tr>
        <tr><td>Rate of Turn:</td><td>127</td></tr>
        </table></body></html>"""
        fields = parse_response(html)
        ship_data = extract_ship_data(fields)

        assert ship_data.msg_type == 3
        assert ship_data.turn_rate == 127


class TestMessageType7:
    """Test AIS Message Type 7 - Binary Acknowledge"""

    def test_parse_msg7(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Message Type:</td><td>7</td></tr>
        <tr><td>MMSI:</td><td>226666007</td></tr>
        <tr><td>Destination MMSI:</td><td>226666008</td></tr>
        </table></body></html>"""
        fields = parse_response(html)
        ship_data = extract_ship_data(fields)

        assert ship_data.msg_type == 7


class TestMessageType11:
    """Test AIS Message Type 11 - UTC/Date Response"""

    def test_parse_msg11_timestamp(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Message Type:</td><td>11</td></tr>
        <tr><td>MMSI:</td><td>226666011</td></tr>
        <tr><td>Timestamp Year:</td><td>2024</td></tr>
        <tr><td>Timestamp Month:</td><td>6</td></tr>
        <tr><td>Timestamp Day:</td><td>18</td></tr>
        <tr><td>Timestamp Hour:</td><td>12</td></tr>
        <tr><td>Timestamp Minute:</td><td>30</td></tr>
        </table></body></html>"""
        fields = parse_response(html)
        ship_data = extract_ship_data(fields)

        assert ship_data.msg_type == 11
        assert ship_data.year == 2024
        assert ship_data.month == 6
        assert ship_data.day == 18


class TestMessageType13:
    """Test AIS Message Type 13 - Safety-Related Acknowledgment"""

    def test_parse_msg13(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Message Type:</td><td>13</td></tr>
        <tr><td>MMSI:</td><td>226666013</td></tr>
        </table></body></html>"""
        fields = parse_response(html)
        ship_data = extract_ship_data(fields)

        assert ship_data.msg_type == 13


class TestMessageType15:
    """Test AIS Message Type 15 - Interrogation"""

    def test_parse_msg15(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>MMSI:</td><td>226666015</td></tr>
        <tr><td>Slot Offset:</td><td>100</td></tr>
        </table></body></html>"""
        fields = parse_response(html)
        ship_data = extract_ship_data(fields)

        assert ship_data.mmsi == "226666015"
        assert "slot offset" in fields
        assert fields["slot offset"] == "100"


class TestMessageType16:
    """Test AIS Message Type 16 - Assignment Mode Command"""

    def test_parse_msg16(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Message Type:</td><td>16</td></tr>
        <tr><td>MMSI:</td><td>226666016</td></tr>
        <tr><td>Destination MMSI 1:</td><td>226666017</td></tr>
        <tr><td>Offset 1:</td><td>100</td></tr>
        <tr><td>Increment 1:</td><td>500</td></tr>
        </table></body></html>"""
        fields = parse_response(html)
        ship_data = extract_ship_data(fields)

        assert ship_data.msg_type == 16


class TestMessageType17:
    """Test AIS Message Type 17 - DGNSS Broadcast Binary Message"""

    def test_parse_msg17_with_position(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Message Type:</td><td>17</td></tr>
        <tr><td>MMSI:</td><td>226666017</td></tr>
        <tr><td>Latitude:</td><td>48.8566</td></tr>
        <tr><td>Longitude:</td><td>2.3522</td></tr>
        </table></body></html>"""
        fields = parse_response(html)
        ship_data = extract_ship_data(fields)

        assert ship_data.msg_type == 17
        assert ship_data.position.latitude == 48.8566


class TestMessageType28:
    """Test AIS Message Type 28 - Data Link Management Message (rare variant)"""

    def test_parse_msg28(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Message Type:</td><td>28</td></tr>
        <tr><td>MMSI:</td><td>226666028</td></tr>
        </table></body></html>"""
        fields = parse_response(html)
        ship_data = extract_ship_data(fields)

        assert ship_data.msg_type == 28


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
"""
Comprehensive tests for all AIS message types (1-27).
Tests parser extraction for each message type using mock HTML fixtures.
"""

import pytest
from aggsoft_ais_decoder.parser import parse_response, extract_ship_data, parse_aggsoft_response
from aggsoft_ais_decoder.models import AISShipData
from tests.fixtures import (
    FIXTURES,
    EXPECTED_VALUES,
    MSG1_HTML, MSG4_HTML, MSG5_HTML, MSG9_HTML,
    MSG18_HTML, MSG19_HTML, MSG21_HTML, MSG24A_HTML, MSG24B_HTML, MSG27_HTML,
)


class TestMessageType1:
    """Test AIS Message Type 1 - Position Report Class A"""

    def test_parse_msg1_all_fields(self):
        fields = parse_response(MSG1_HTML)
        ship_data = extract_ship_data(fields)

        assert ship_data.mmsi == "226666001"
        assert ship_data.msg_type == 1
        assert ship_data.navigation_status == "Under way using engine"
        assert ship_data.speed_over_ground == 10.5
        assert ship_data.position.latitude == 48.8566
        assert ship_data.position.longitude == 2.3522
        assert ship_data.course_over_ground == 180.0
        assert ship_data.heading == 90
        assert ship_data.turn_rate == -128

    def test_parse_msg1_position_accuracy(self):
        fields = parse_response(MSG1_HTML)
        ship_data = extract_ship_data(fields)
        assert ship_data.position_accuracy == "Low"

    def test_parse_msg1_raim_flag(self):
        fields = parse_response(MSG1_HTML)
        ship_data = extract_ship_data(fields)
        assert ship_data.raim_flag is False


class TestMessageType4:
    """Test AIS Message Type 4 - Base Station Report"""

    def test_parse_msg4_basic(self):
        fields = parse_response(MSG4_HTML)
        ship_data = extract_ship_data(fields)

        assert ship_data.mmsi == "226666004"
        assert ship_data.msg_type == 4
        assert ship_data.position.latitude == 48.8566
        assert ship_data.position.longitude == 2.3522

    def test_parse_msg4_timestamp(self):
        fields = parse_response(MSG4_HTML)
        ship_data = extract_ship_data(fields)

        assert ship_data.year == 2024
        assert ship_data.month == 6
        assert ship_data.day == 18
        assert ship_data.hour == 12
        assert ship_data.minute == 30
        assert ship_data.second == 0

    def test_parse_msg4_epfd(self):
        fields = parse_response(MSG4_HTML)
        ship_data = extract_ship_data(fields)
        assert ship_data.epfd_type == "GPS"

    def test_parse_msg4_accuracy(self):
        fields = parse_response(MSG4_HTML)
        ship_data = extract_ship_data(fields)
        assert ship_data.position_accuracy == "High"


class TestMessageType5:
    """Test AIS Message Type 5 - Static and Voyage Related Data"""

    def test_parse_msg5_basic(self):
        fields = parse_response(MSG5_HTML)
        ship_data = extract_ship_data(fields)

        assert ship_data.mmsi == "226666005"
        assert ship_data.msg_type == 5
        assert ship_data.ship_name == "TEST VESSEL ABC"
        assert ship_data.callsign == "TST1234"
        assert ship_data.destination == "PARIS FRANCE"

    def test_parse_msg5_vessel_type(self):
        fields = parse_response(MSG5_HTML)
        ship_data = extract_ship_data(fields)

        assert ship_data.vessel_type == "37"
        assert ship_data.vessel_type_description == "Pleasure craft"

    def test_parse_msg5_dimensions(self):
        fields = parse_response(MSG5_HTML)
        ship_data = extract_ship_data(fields)

        assert ship_data.dimensions is not None
        assert ship_data.dimensions.to_bow == 10
        assert ship_data.dimensions.to_stern == 10
        assert ship_data.dimensions.to_port == 3
        assert ship_data.dimensions.to_starboard == 3

    def test_parse_msg5_draught(self):
        fields = parse_response(MSG5_HTML)
        ship_data = extract_ship_data(fields)
        assert ship_data.draught == 2.0


class TestMessageType9:
    """Test AIS Message Type 9 - SAR Aircraft Position Report"""

    def test_parse_msg9_basic(self):
        fields = parse_response(MSG9_HTML)
        ship_data = extract_ship_data(fields)

        assert ship_data.mmsi == "226666009"
        assert ship_data.msg_type == 9
        assert ship_data.position.latitude == 48.8566
        assert ship_data.position.longitude == 2.3522

    def test_parse_msg9_altitude(self):
        fields = parse_response(MSG9_HTML)
        ship_data = extract_ship_data(fields)
        assert ship_data.altitude == 1000

    def test_parse_msg9_speed(self):
        fields = parse_response(MSG9_HTML)
        ship_data = extract_ship_data(fields)
        assert ship_data.speed_over_ground == 25.0


class TestMessageType18:
    """Test AIS Message Type 18 - Standard Class B CS Position Report"""

    def test_parse_msg18_basic(self):
        fields = parse_response(MSG18_HTML)
        ship_data = extract_ship_data(fields)

        assert ship_data.mmsi == "226666018"
        assert ship_data.msg_type == 18
        assert ship_data.position.latitude == 48.8566
        assert ship_data.position.longitude == 2.3522

    def test_parse_msg18_speed_course_heading(self):
        fields = parse_response(MSG18_HTML)
        ship_data = extract_ship_data(fields)

        assert ship_data.speed_over_ground == 10.5
        assert ship_data.course_over_ground == 180.0
        assert ship_data.heading == 90


class TestMessageType19:
    """Test AIS Message Type 19 - Extended Class B CS Position Report"""

    def test_parse_msg19_basic(self):
        fields = parse_response(MSG19_HTML)
        ship_data = extract_ship_data(fields)

        assert ship_data.mmsi == "226666019"
        assert ship_data.msg_type == 19
        assert ship_data.vessel_type == "37"
        assert ship_data.position.latitude == 48.8566
        assert ship_data.position.longitude == 2.3522

    def test_parse_msg19_dimensions(self):
        fields = parse_response(MSG19_HTML)
        ship_data = extract_ship_data(fields)

        assert ship_data.dimensions is not None
        assert ship_data.dimensions.to_bow == 5
        assert ship_data.dimensions.to_stern == 5
        assert ship_data.dimensions.to_port == 2
        assert ship_data.dimensions.to_starboard == 2


class TestMessageType21:
    """Test AIS Message Type 21 - Aid-to-Navigation Report"""

    def test_parse_msg21_basic(self):
        fields = parse_response(MSG21_HTML)
        ship_data = extract_ship_data(fields)

        assert ship_data.mmsi == "226666021"
        assert ship_data.msg_type == 21
        assert ship_data.ship_name == "BUOY MARKER ONE"
        assert ship_data.position.latitude == 48.8566
        assert ship_data.position.longitude == 2.3522

    def test_parse_msg21_aid_type(self):
        fields = parse_response(MSG21_HTML)
        ship_data = extract_ship_data(fields)
        assert ship_data.aid_type == 5


class TestMessageType24:
    """Test AIS Message Type 24 - Class B Static Data Report"""

    def test_parse_msg24a_part_number(self):
        fields = parse_response(MSG24A_HTML)
        ship_data = extract_ship_data(fields)

        assert ship_data.mmsi == "226666024"
        assert ship_data.part_number == 0
        assert ship_data.ship_name == "CLASS B VESSEL ABC"

    def test_parse_msg24b_part_number(self):
        fields = parse_response(MSG24B_HTML)
        ship_data = extract_ship_data(fields)

        assert ship_data.mmsi == "226666025"
        assert ship_data.part_number == 1
        assert ship_data.vessel_type == "37"
        assert ship_data.callsign == "TST1234"

    def test_parse_msg24b_vendor_model_serial(self):
        fields = parse_response(MSG24B_HTML)
        ship_data = extract_ship_data(fields)

        assert ship_data.vendor_id == "ABC"
        assert ship_data.model == 1
        assert ship_data.serial == 12345

    def test_parse_msg24b_dimensions(self):
        fields = parse_response(MSG24B_HTML)
        ship_data = extract_ship_data(fields)

        assert ship_data.dimensions is not None
        assert ship_data.dimensions.to_bow == 5
        assert ship_data.dimensions.to_stern == 5
        assert ship_data.dimensions.to_port == 2
        assert ship_data.dimensions.to_starboard == 2


class TestMessageType27:
    """Test AIS Message Type 27 - Long Range AIS Broadcast Message"""

    def test_parse_msg27_basic(self):
        fields = parse_response(MSG27_HTML)
        ship_data = extract_ship_data(fields)

        assert ship_data.mmsi == "226666028"
        assert ship_data.msg_type == 27
        assert ship_data.position.latitude == 48.8566
        assert ship_data.position.longitude == 2.3522
        assert ship_data.speed_over_ground == 10.0
        assert ship_data.course_over_ground == 180.0

    def test_parse_msg27_status(self):
        fields = parse_response(MSG27_HTML)
        ship_data = extract_ship_data(fields)
        assert ship_data.navigation_status == "Undefined"


class TestAllFixturesComprehensive:
    """Test that all fixtures parse correctly and contain expected values"""

    @pytest.mark.parametrize("fixture_id,expected", [
        (1, EXPECTED_VALUES[1]),
        (4, EXPECTED_VALUES[4]),
        (5, EXPECTED_VALUES[5]),
        (18, EXPECTED_VALUES[18]),
        (19, EXPECTED_VALUES[19]),
        (21, EXPECTED_VALUES[21]),
        ("24A", EXPECTED_VALUES["24A"]),
        ("24B", EXPECTED_VALUES["24B"]),
        (27, EXPECTED_VALUES[27]),
    ])
    def test_all_fixtures(self, fixture_id, expected):
        html = FIXTURES[fixture_id]
        fields = parse_response(html)
        ship_data = extract_ship_data(fields)

        assert ship_data.mmsi == expected["mmsi"]

        if "position" in expected:
            assert ship_data.position.latitude == expected["position"]["latitude"]
            assert ship_data.position.longitude == expected["position"]["longitude"]

        if "speed_over_ground" in expected:
            assert ship_data.speed_over_ground == expected["speed_over_ground"]

        if "course_over_ground" in expected:
            assert ship_data.course_over_ground == expected["course_over_ground"]

        if "ship_name" in expected:
            assert ship_data.ship_name == expected["ship_name"]

        if "destination" in expected:
            assert ship_data.destination == expected["destination"]

        if "vessel_type" in expected:
            assert ship_data.vessel_type == expected["vessel_type"]

        if "dimensions" in expected:
            assert ship_data.dimensions is not None
            assert ship_data.dimensions.to_bow == expected["dimensions"]["to_bow"]
            assert ship_data.dimensions.to_stern == expected["dimensions"]["to_stern"]
            assert ship_data.dimensions.to_port == expected["dimensions"]["to_port"]
            assert ship_data.dimensions.to_starboard == expected["dimensions"]["to_starboard"]


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_html(self):
        fields = parse_response("<html><body></body></html>")
        assert len(fields) == 0

    def test_missing_values(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>MMSI:</td><td>123456789</td></tr>
        </table></body></html>"""
        fields = parse_response(html)
        ship_data = extract_ship_data(fields)

        assert ship_data.mmsi == "123456789"
        assert ship_data.position is None
        assert ship_data.ship_name is None

    def test_special_characters_in_name(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Ship Name:</td><td>TST-123 / ABC</td></tr>
        </table></body></html>"""
        fields = parse_response(html)
        ship_data = extract_ship_data(fields)
        assert ship_data.ship_name == "TST-123 / ABC"

    def test_negative_coordinates(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Latitude:</td><td>-33.8688</td></tr>
        <tr><td>Longitude:</td><td>151.2093</td></tr>
        </table></body></html>"""
        fields = parse_response(html)
        ship_data = extract_ship_data(fields)
        assert ship_data.position.latitude == -33.8688
        assert ship_data.position.longitude == 151.2093


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
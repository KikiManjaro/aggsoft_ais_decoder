"""
Tests for boundary values and edge cases in AIS message fields.
Tests verify correct handling of extreme values, N/A markers, and limits.
"""

import pytest
from aggsoft_ais_decoder.parser import parse_response, extract_ship_data


class TestLatitudeBoundaries:
    """Test latitude boundary values (-90 to +90 degrees)"""

    def test_latitude_positive_max(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Latitude:</td><td>90.0</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.position.latitude == 90.0

    def test_latitude_negative_max(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Latitude:</td><td>-90.0</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.position.latitude == -90.0

    def test_latitude_zero(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Latitude:</td><td>0.0</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.position.latitude == 0.0

    def test_latitude_equator_positive(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Latitude:</td><td>0.0001</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.position.latitude == 0.0001

    def test_latitude_equator_negative(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Latitude:</td><td>-0.0001</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.position.latitude == -0.0001

    def test_latitude_with_decimal_precision(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Latitude:</td><td>48.85661234</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.position.latitude == 48.85661234

    def test_latitude_with_degree_symbol(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Latitude:</td><td>48.8566°</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.position.latitude == 48.8566

    def test_latitude_with_nsew_suffix(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Latitude:</td><td>48.8566 N</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.position.latitude == 48.8566


class TestLongitudeBoundaries:
    """Test longitude boundary values (-180 to +180 degrees)"""

    def test_longitude_positive_max(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Longitude:</td><td>180.0</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.position.longitude == 180.0

    def test_longitude_negative_max(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Longitude:</td><td>-180.0</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.position.longitude == -180.0

    def test_longitude_zero(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Longitude:</td><td>0.0</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.position.longitude == 0.0

    def test_longitude_prime_meridian(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Longitude:</td><td>0.0001</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.position.longitude == 0.0001

    def test_longitude_date_line(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Longitude:</td><td>179.9999</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.position.longitude == 179.9999

    def test_longitude_with_ew_suffix(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Longitude:</td><td>2.3522 E</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.position.longitude == 2.3522


class TestSpeedBoundaries:
    """Test Speed Over Ground (SOG) boundary values"""

    def test_speed_zero(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Speed Over Ground:</td><td>0.0</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.speed_over_ground == 0.0

    def test_speed_max_valid(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Speed Over Ground:</td><td>102.2</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.speed_over_ground == 102.2

    def test_speed_na_value(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Speed Over Ground:</td><td>N/A</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.speed_over_ground is None

    def test_speed_with_knots_unit(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Speed Over Ground:</td><td>15.5 knots</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.speed_over_ground == 15.5

    def test_speed_integer_value(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Speed Over Ground:</td><td>10</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.speed_over_ground == 10.0


class TestCourseBoundaries:
    """Test Course Over Ground (COG) boundary values"""

    def test_course_zero(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Course Over Ground:</td><td>0.0</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.course_over_ground == 0.0

    def test_course_359_degrees(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Course Over Ground:</td><td>359.9</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.course_over_ground == 359.9

    def test_course_na_value(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Course Over Ground:</td><td>N/A</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.course_over_ground is None

    def test_course_with_degree_symbol(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Course Over Ground:</td><td>180.0°</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.course_over_ground == 180.0


class TestHeadingBoundaries:
    """Test True Heading boundary values"""

    def test_heading_zero(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>True Heading:</td><td>0</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.heading == 0

    def test_heading_359(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>True Heading:</td><td>359</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.heading == 359

    def test_heading_na_value(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>True Heading:</td><td>N/A</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.heading is None


class TestTurnRateBoundaries:
    """Test Rate of Turn boundary values"""

    def test_turn_rate_negative_max(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Rate of Turn:</td><td>-128</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.turn_rate == -128

    def test_turn_rate_positive_max(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Rate of Turn:</td><td>127</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.turn_rate == 127

    def test_turn_rate_zero(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Rate of Turn:</td><td>0</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.turn_rate == 0

    def test_turn_rate_na(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Rate of Turn:</td><td>N/A</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.turn_rate is None


class TestMMSIValidation:
    """Test MMSI field validation"""

    def test_mmsi_9_digits(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>MMSI:</td><td>123456789</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.mmsi == "123456789"

    def test_mmsi_mid_range(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>MMSI:</td><td>226666007</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.mmsi == "226666007"

    def test_mmsi_leading_zeros(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>MMSI:</td><td>000123456</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.mmsi == "000123456"


class TestDimensionBoundaries:
    """Test dimension field boundary values"""

    def test_dimension_zero(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Dimension to Bow:</td><td>0</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.dimensions.to_bow == 0

    def test_dimension_max(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Dimension to Bow:</td><td>511</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.dimensions.to_bow == 511

    def test_all_dimensions_zero(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Dimension to Bow:</td><td>0</td></tr>
        <tr><td>Dimension to Stern:</td><td>0</td></tr>
        <tr><td>Dimension to Port:</td><td>0</td></tr>
        <tr><td>Dimension to Starboard:</td><td>0</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.dimensions.to_bow == 0
        assert ship_data.dimensions.to_stern == 0
        assert ship_data.dimensions.to_port == 0
        assert ship_data.dimensions.to_starboard == 0


class TestDraughtBoundaries:
    """Test draught field boundary values"""

    def test_draught_zero(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Draught:</td><td>0.0</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.draught == 0.0

    def test_draught_max(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Draught:</td><td>25.5</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.draught == 25.5

    def test_draught_decimal(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Draught:</td><td>5.5</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.draught == 5.5


class TestAltitudeBoundaries:
    """Test altitude field for SAR aircraft (Msg 9)"""

    def test_altitude_zero(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Altitude:</td><td>0</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.altitude == 0

    def test_altitude_max(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Altitude:</td><td>4094</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.altitude == 4094

    def test_altitude_na(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Altitude:</td><td>4095</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.altitude == 4095


class TestTimestampBoundaries:
    """Test timestamp field boundary values"""

    def test_timestamp_zero(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Time Stamp:</td><td>0</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.timestamp == 0

    def test_timestamp_59(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Time Stamp:</td><td>59</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.timestamp == 59

    def test_timestamp_na(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Time Stamp:</td><td>60</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.timestamp == 60


class TestNavigationStatusValues:
    """Test all navigation status values"""

    @pytest.mark.parametrize("status_code,expected", [
        ("0", "Under way using engine"),
        ("1", "At anchor"),
        ("2", "Not under command"),
        ("3", "Restricted maneuverability"),
        ("4", "Constrained by her draught"),
        ("5", "Moored"),
        ("6", "Aground"),
        ("7", "Engaged in Fishing"),
        ("8", "Under way sailing"),
        ("15", "Undefined"),
    ])
    def test_navigation_status_values(self, status_code, expected):
        html = f"""<!DOCTYPE html><html><body><table>
        <tr><td>Navigation Status:</td><td>{status_code}</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.navigation_status == expected


class TestEPFDTypes:
    """Test Electronic Position Fixing Device types"""

    @pytest.mark.parametrize("epfd_code,expected", [
        ("0", "Undefined"),
        ("1", "GPS"),
        ("2", "GLONASS"),
        ("3", "GPS+GLONASS"),
        ("4", "Loran-C"),
        ("5", "Chayka"),
        ("6", "Integrated navigation system"),
        ("7", "Surveyed"),
    ])
    def test_epfd_types(self, epfd_code, expected):
        html = f"""<!DOCTYPE html><html><body><table>
        <tr><td>Type of EPFD:</td><td>{epfd_code}</td></tr>
        </table></body></html>"""
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.epfd_type == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
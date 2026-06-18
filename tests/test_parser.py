import pytest
from bs4 import BeautifulSoup
from aggsoft_ais_decoder.parser import parse_response, extract_ship_data, parse_aggsoft_response
from aggsoft_ais_decoder.models import AISShipData


class TestParseResponse:
    def test_parse_table_response(self, sample_html_response):
        fields = parse_response(sample_html_response)
        assert fields["mmsi"] == "226666007"
        assert fields["ship name"] == "TEST VESSEL"
        assert fields["callsign"] == "TST1234"

    def test_parse_minimal_response(self, sample_html_minimal):
        fields = parse_response(sample_html_minimal)
        assert fields["mmsi"] == "987654321"
        assert "latitude" in fields
        assert "longitude" in fields

    def test_parse_no_data(self, sample_html_no_data):
        fields = parse_response(sample_html_no_data)
        assert len(fields) == 0


class TestExtractShipData:
    def test_extract_full_data(self, sample_html_response, expected_ship_data):
        fields = parse_response(sample_html_response)
        ship_data = extract_ship_data(fields)

        assert ship_data.mmsi == expected_ship_data["mmsi"]
        assert ship_data.ship_name == expected_ship_data["ship_name"]
        assert ship_data.callsign == expected_ship_data["callsign"]
        assert ship_data.imo_number == expected_ship_data["imo_number"]
        assert ship_data.vessel_type == expected_ship_data["vessel_type"]
        assert ship_data.vessel_type_description == expected_ship_data["vessel_type_description"]
        assert ship_data.position.latitude == expected_ship_data["position"]["latitude"]
        assert ship_data.position.longitude == expected_ship_data["position"]["longitude"]
        assert ship_data.speed_over_ground == expected_ship_data["speed_over_ground"]
        assert ship_data.course_over_ground == expected_ship_data["course_over_ground"]
        assert ship_data.heading == expected_ship_data["heading"]
        assert ship_data.navigation_status == expected_ship_data["navigation_status"]

    def test_extract_minimal_data(self, sample_html_minimal):
        fields = parse_response(sample_html_minimal)
        ship_data = extract_ship_data(fields)

        assert ship_data.mmsi == "987654321"
        assert ship_data.position.latitude == 35.6762
        assert ship_data.position.longitude == 139.6503
        assert ship_data.ship_name is None

    def test_extract_with_dimensions(self, sample_html_response):
        fields = parse_response(sample_html_response)
        ship_data = extract_ship_data(fields)

        assert ship_data.dimensions is not None
        assert ship_data.dimensions.to_bow == 10
        assert ship_data.dimensions.to_stern == 10
        assert ship_data.dimensions.to_port == 3
        assert ship_data.dimensions.to_starboard == 3


class TestParseAggsoftResponse:
    def test_full_flow(self, sample_html_response, expected_ship_data):
        ship_data = parse_aggsoft_response(sample_html_response)

        assert isinstance(ship_data, AISShipData)
        assert ship_data.mmsi == expected_ship_data["mmsi"]
        assert ship_data.ship_name == expected_ship_data["ship_name"]

    def test_navigation_status_mapping(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Navigation Status:</td><td>0</td></tr>
        </table></body></html>"""
        ship_data = parse_aggsoft_response(html)
        assert ship_data.navigation_status == "Under way using engine"

    def test_vessel_type_mapping(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Vessel Type:</td><td>37</td></tr>
        </table></body></html>"""
        ship_data = parse_aggsoft_response(html)
        assert ship_data.vessel_type == "37"
        assert ship_data.vessel_type_description == "Pleasure craft"

    def test_speed_with_unit(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Speed Over Ground:</td><td>10.5 knots</td></tr>
        </table></body></html>"""
        ship_data = parse_aggsoft_response(html)
        assert ship_data.speed_over_ground == 10.5

    def test_coordinates_with_degrees_symbol(self):
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Latitude:</td><td>48.8566°</td></tr>
        <tr><td>Longitude:</td><td>2.3522°</td></tr>
        </table></body></html>"""
        ship_data = parse_aggsoft_response(html)
        assert ship_data.position.latitude == 48.8566
        assert ship_data.position.longitude == 2.3522


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
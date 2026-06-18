"""
Tests for multi-part NMEA AIS messages.
These tests verify correct handling of fragmented AIS messages.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aggsoft_ais_decoder.client import AISDecoderClient
from aggsoft_ais_decoder.parser import parse_response, extract_ship_data
from aggsoft_ais_decoder.models import AISDecodeResponse


MULTIPART_MSG5_SENTENCE1 = "!AIVDO,1,1,,A,703ltL0Q7D@GH0l0e0O,0*2F"
MULTIPART_MSG5_SENTENCE2 = "!AIVDO,1,1,,B,703ltL0Q7D@GH0l0e0Otp0<Ht0pP0P1Ht1@8P0l0@0l09Ht0P09Ht1@8Hq09Hq09Hp1@8Hq09Hq09Hq09Hq,0*2F"

MULTIPART_MSG24A_SENTENCE1 = "!AIVDO,1,1,,A,15R?0n08<:O85mSn4Q8a4@34b0,0*4D"
MULTIPART_MSG24A_SENTENCE2 = "!AIVDO,1,1,,B,15R?0n08<:O85mSn4Q8a4@34b0p0<8Hq09Hp1@8Hq09Hq09Hq09Hq09Hq09Hq09Hq09Hq09Hq,0*5A"

SINGLE_PART_MSG1 = "!AIVDM,1,1,,A,13u@ND0P01PJ=0lMH0nN20pl,0*7D"
SINGLE_PART_MSG18 = "!AIVDM,1,1,,A,91>Mn00FjLqGrqPoJ8n0v0p00<wS,0*4B"

MSG5_MULTIPART_HTML = """<!DOCTYPE html>
<html>
<body>
<table>
<tr><td>Message Type:</td><td>5</td></tr>
<tr><td>MMSI:</td><td>226666005</td></tr>
<tr><td>IMO Number:</td><td>0</td></tr>
<tr><td>Callsign:</td><td>TST1234</td></tr>
<tr><td>Ship Name:</td><td>TEST VESSEL</td></tr>
<tr><td>Ship Type:</td><td>37</td></tr>
<tr><td>Dimension to Bow:</td><td>10</td></tr>
<tr><td>Dimension to Stern:</td><td>10</td></tr>
<tr><td>Dimension to Port:</td><td>3</td></tr>
<tr><td>Dimension to Starboard:</td><td>3</td></tr>
<tr><td>Type of EPFD:</td><td>GPS</td></tr>
<tr><td>ETA Month:</td><td>12</td></tr>
<tr><td>ETA Day:</td><td>25</td></tr>
<tr><td>ETA Hour:</td><td>14</td></tr>
<tr><td>ETA Minute:</td><td>30</td></tr>
<tr><td>Draught:</td><td>5.5</td></tr>
<tr><td>Destination:</td><td>TEST DESTINATION</td></tr>
<tr><td>DTE:</td><td>No</td></tr>
</table>
</body>
</html>"""

MSG24_MULTIPART_HTML = """<!DOCTYPE html>
<html>
<body>
<table>
<tr><td>Message Type:</td><td>24</td></tr>
<tr><td>MMSI:</td><td>226666024</td></tr>
<tr><td>Part Number:</td><td>0</td></tr>
<tr><td>Ship Name:</td><td>CLASS B VESSEL NAME</td></tr>
</table>
</body>
</html>"""


class TestMultipartNMEAParsing:
    """Test parsing of multi-part NMEA messages"""

    def test_parse_multipart_msg5_html(self):
        fields = parse_response(MSG5_MULTIPART_HTML)
        ship_data = extract_ship_data(fields)

        assert ship_data.mmsi == "226666005"
        assert ship_data.ship_name == "TEST VESSEL"
        assert ship_data.callsign == "TST1234"
        assert ship_data.destination == "TEST DESTINATION"
        assert ship_data.vessel_type == "37"
        assert ship_data.draught == 5.5

    def test_parse_multipart_msg24_html(self):
        fields = parse_response(MSG24_MULTIPART_HTML)
        ship_data = extract_ship_data(fields)

        assert ship_data.mmsi == "226666024"
        assert ship_data.ship_name == "CLASS B VESSEL NAME"

    def test_single_part_msg1_parses_correctly(self):
        fields = parse_response("""<!DOCTYPE html>
<html><body><table>
<tr><td>MMSI:</td><td>123456789</td></tr>
<tr><td>Latitude:</td><td>48.8566</td></tr>
<tr><td>Longitude:</td><td>2.3522</td></tr>
</table></body></html>""")
        ship_data = extract_ship_data(fields)
        assert ship_data.mmsi == "123456789"

    def test_single_part_msg18_parses_correctly(self):
        fields = parse_response("""<!DOCTYPE html>
<html><body><table>
<tr><td>MMSI:</td><td>987654321</td></tr>
<tr><td>Speed Over Ground:</td><td>8.5</td></tr>
</table></body></html>""")
        ship_data = extract_ship_data(fields)
        assert ship_data.mmsi == "987654321"
        assert ship_data.speed_over_ground == 8.5


class TestMultipartClientBehavior:
    """Test AISDecoderClient behavior with multi-part messages"""

    @pytest.mark.asyncio
    async def test_decode_single_part_message(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """<!DOCTYPE html>
<html><body><table>
<tr><td>MMSI:</td><td>123456789</td></tr>
</table></body></html>"""

        mock_client = AsyncMock(spec=type(None))
        mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.is_closed = False
        mock_client.aclose = AsyncMock()

        client = AISDecoderClient()
        with patch.object(client, "_get_client", return_value=mock_client):
            result = await client.decode(SINGLE_PART_MSG1)

        assert result.success is True
        assert result.decoded.mmsi == "123456789"

    @pytest.mark.asyncio
    async def test_decode_multipart_msg5(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = MSG5_MULTIPART_HTML

        mock_client = AsyncMock(spec=type(None))
        mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.is_closed = False
        mock_client.aclose = AsyncMock()

        client = AISDecoderClient()
        with patch.object(client, "_get_client", return_value=mock_client):
            result = await client.decode(MULTIPART_MSG5_SENTENCE1)

        assert result.success is True
        assert result.decoded.ship_name == "TEST VESSEL"

    @pytest.mark.asyncio
    async def test_decode_batch_multiple_single_part(self):
        messages = [
            "!AIVDM,1,1,,A,13u@ND0P01PJ=0lMH0nN20pl,0*7D",
            "!AIVDO,1,1,,A,91>Mn00FjLqGrqPoJ8n0v0p00<wS,0*4B",
            "!AIVDM,1,1,,A,15MgK45P3@G?fl0E`JbR0OwT0@MS,0*4E",
        ]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """<!DOCTYPE html>
<html><body><table>
<tr><td>MMSI:</td><td>226666001</td></tr>
<tr><td>Latitude:</td><td>48.8566</td></tr>
<tr><td>Longitude:</td><td>2.3522</td></tr>
</table></body></html>"""

        mock_client = AsyncMock(spec=type(None))
        mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.is_closed = False
        mock_client.aclose = AsyncMock()

        client = AISDecoderClient()
        with patch.object(client, "_get_client", return_value=mock_client):
            result = await client.decode_batch(messages, delay=0.01)

        assert result.total == 3
        assert result.successful == 3
        assert result.failed == 0


class TestMultipartHTMLVariations:
    """Test parsing of different HTML formats from aggsoft for multi-part messages"""

    def test_msg5_with_two_parts_indicated(self):
        html = """<!DOCTYPE html>
<html><body>
<h2>Decoded Message (Part 1 of 2)</h2>
<table>
<tr><td>Message Type:</td><td>5</td></tr>
<tr><td>MMSI:</td><td>226666005</td></tr>
<tr><td>Ship Name:</td><td>PART1 DATA</td></tr>
</table>
</body></html>"""
        fields = parse_response(html)
        ship_data = extract_ship_data(fields)
        assert ship_data.mmsi == "226666005"
        assert ship_data.ship_name == "PART1 DATA"

    def test_msg24_part_a_format(self):
        html = """<!DOCTYPE html>
<html><body>
<table>
<tr><td>Message Type:</td><td>24</td></tr>
<tr><td>MMSI:</td><td>226666024</td></tr>
<tr><td>Part Number:</td><td>0</td></tr>
<tr><td>Ship Name:</td><td>NAME PART A</td></tr>
</table>
</body></html>"""
        fields = parse_response(html)
        ship_data = extract_ship_data(fields)
        assert ship_data.part_number == 0
        assert ship_data.ship_name == "NAME PART A"

    def test_msg24_part_b_format(self):
        html = """<!DOCTYPE html>
<html><body>
<table>
<tr><td>Message Type:</td><td>24</td></tr>
<tr><td>MMSI:</td><td>226666025</td></tr>
<tr><td>Part Number:</td><td>1</td></tr>
<tr><td>Ship Type:</td><td>37</td></tr>
<tr><td>Callsign:</td><td>CALL123</td></tr>
</table>
</body></html>"""
        fields = parse_response(html)
        ship_data = extract_ship_data(fields)
        assert ship_data.part_number == 1
        assert ship_data.vessel_type == "37"


class TestEdgeCasesMultipart:
    """Edge cases for multi-part messages"""

    def test_empty_multipart_response(self):
        fields = parse_response("<html><body></body></html>")
        ship_data = extract_ship_data(fields)
        assert ship_data.mmsi is None

    def test_multiline_ship_name(self):
        html = """<!DOCTYPE html>
<html><body><table>
<tr><td>Ship Name:</td><td>VERY LONG VESSEL
NAME SPLIT OVER
MULTIPLE LINES</td></tr>
</table></body></html>"""
        fields = parse_response(html)
        ship_data = extract_ship_data(fields)
        assert "\n" in ship_data.ship_name or "VERY LONG" in ship_data.ship_name

    def test_special_characters_in_destination(self):
        html = """<!DOCTYPE html>
<html><body><table>
<tr><td>Destination:</td><td>PORT-DE-BOUC, FRANCE (NORD)</td></tr>
</table></body></html>"""
        fields = parse_response(html)
        ship_data = extract_ship_data(fields)
        assert ship_data.destination == "PORT-DE-BOUC, FRANCE (NORD)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
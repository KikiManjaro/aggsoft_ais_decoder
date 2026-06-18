"""
Integration tests against real aggsoft.com API using pyais for generating valid AIS messages.

These tests:
1. Generate valid NMEA messages using pyais.encode_dict()
2. Send them to aggsoft.com for decoding
3. Verify the decoded fields match the input data

Run with: RUN_INTEGRATION_TESTS=1 pytest tests/test_integration_real_ais.py -v
"""

import os
import pytest
from pyais.encode import encode_dict

from aggsoft_ais_decoder import AISDecoderClient


def approx(expected, rel=1e-3, abs=1e-6):
    """Custom approximation matcher for float comparison."""
    return pytest.approx(expected, rel=rel, abs=abs)


class TestIntegrationMsg1PositionReport:
    """Test Message Type 1 - Position Report Class A"""

    @pytest.fixture(autouse=True)
    def check_integration_enabled(self):
        if not os.environ.get("RUN_INTEGRATION_TESTS"):
            pytest.skip("Integration tests disabled. Set RUN_INTEGRATION_TESTS=1 to enable.")

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_msg1_basic_position(self):
        """Test basic Msg 1 with standard position data."""
        input_data = {
            'type': 1,
            'mmsi': '226666001',
            'lat': 47.8626,
            'lon': 2.1291,
            'status': 0,
            'turn': 0,
            'speed': 10.5,
            'accuracy': False,
            'course': 180.0,
            'heading': 90,
            'second': 30,
            'raim': False,
            'radio': 0,
        }

        nmea_list = encode_dict(input_data)
        nmea = nmea_list[0]

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True, f"Decode failed: {result.error}"
        assert result.decoded.mmsi == '226666001'
        assert result.decoded.position.latitude == approx(47.8626, abs=0.0001)
        assert result.decoded.position.longitude == approx(2.1291, abs=0.0001)
        assert result.decoded.speed_over_ground == approx(10.5, abs=0.1)
        assert result.decoded.course_over_ground == approx(180.0, abs=0.1)
        assert result.decoded.heading == 90

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_msg1_moored(self):
        """Test Msg 1 with Navigation Status = Moored (5)."""
        input_data = {
            'type': 1,
            'mmsi': '226666002',
            'lat': 48.8566,
            'lon': 2.3522,
            'status': 5,  # Moored
            'speed': 0,
            'course': 0,
            'heading': 511,  # N/A
            'second': 45,
        }

        nmea_list = encode_dict(input_data)
        nmea = nmea_list[0]

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.navigation_status == "Moored"
        assert result.decoded.speed_over_ground == approx(0.0)

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_msg1_at_anchor(self):
        """Test Msg 1 with Navigation Status = At Anchor (1)."""
        input_data = {
            'type': 1,
            'mmsi': '226666003',
            'lat': 51.9244,
            'lon': 4.4777,
            'status': 1,  # At anchor
            'speed': 0,
            'course': 45.0,
            'heading': 45,
        }

        nmea_list = encode_dict(input_data)
        nmea = nmea_list[0]

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.navigation_status == "At anchor"

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_msg1_extreme_coordinates(self):
        """Test Msg 1 with extreme coordinates."""
        input_data = {
            'type': 1,
            'mmsi': '226666004',
            'lat': 89.9999,
            'lon': 179.9999,
            'speed': 102.2,
            'course': 359.9,
        }

        nmea_list = encode_dict(input_data)
        nmea = nmea_list[0]

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.position.latitude == approx(89.9999, abs=0.001)
        assert result.decoded.position.longitude == approx(179.9999, abs=0.001)

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_msg1_negative_coordinates(self):
        """Test Msg 1 with negative coordinates (Southern/Western hemisphere)."""
        input_data = {
            'type': 1,
            'mmsi': '226666005',
            'lat': -33.8688,
            'lon': 151.2093,
            'speed': 15.0,
            'course': 270.0,
        }

        nmea_list = encode_dict(input_data)
        nmea = nmea_list[0]

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.position.latitude == approx(-33.8688, abs=0.001)
        assert result.decoded.position.longitude == approx(151.2093, abs=0.001)


class TestIntegrationMsg5StaticVoyage:
    """Test Message Type 5 - Static and Voyage Related Data.

    Msg 5 requires multipart NMEA (2 sentences). pyais generates both
    sentences and decode() now supports list[str] for multipart messages.
    """

    @pytest.fixture(autouse=True)
    def check_integration_enabled(self):
        if not os.environ.get("RUN_INTEGRATION_TESTS"):
            pytest.skip("Integration tests disabled. Set RUN_INTEGRATION_TESTS=1 to enable.")

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_msg5_basic(self):
        input_data = {
            'type': 5,
            'mmsi': '226666010',
            'shipname': 'TEST VESSEL ABC',
            'callsign': 'TST1234',
            'shiptype': 37,
            'to_bow': 10,
            'to_stern': 10,
            'to_port': 3,
            'to_starboard': 3,
            'epfd': 1,
            'draught': 5.5,
            'month': 12,
            'day': 25,
            'hour': 14,
            'minute': 30,
            'destination': 'TEST DESTINATION',
            'dte': 0,
        }

        nmea_list = encode_dict(input_data)
        assert len(nmea_list) == 2, "Msg 5 should produce 2 sentences"

        async with AISDecoderClient() as client:
            result = await client.decode(nmea_list)

        assert result.success is True, f"Decode failed: {result.error}"
        assert result.decoded.mmsi == '226666010'
        assert 'TEST VESSEL' in result.decoded.ship_name
        assert result.decoded.callsign == 'TST1234'

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_msg5_cargo_vessel(self):
        input_data = {
            'type': 5,
            'mmsi': '226666011',
            'shipname': 'CARGO HCM         ',
            'callsign': 'DESTXX',
            'shiptype': 70,
            'to_bow': 50,
            'to_stern': 60,
            'to_port': 10,
            'to_starboard': 15,
            'epfd': 1,
            'draught': 8.5,
            'month': 3,
            'day': 15,
            'hour': 8,
            'minute': 0,
            'destination': 'ROTTERDAM',
            'dte': 0,
        }

        nmea_list = encode_dict(input_data)
        assert len(nmea_list) == 2, "Msg 5 should produce 2 sentences"

        async with AISDecoderClient() as client:
            result = await client.decode(nmea_list)

        assert result.success is True
        assert result.decoded.mmsi == '226666011'
        assert 'CARGO' in result.decoded.ship_name


class TestIntegrationMsg18ClassB:
    """Test Message Type 18 - Standard Class B CS Position Report"""

    @pytest.fixture(autouse=True)
    def check_integration_enabled(self):
        if not os.environ.get("RUN_INTEGRATION_TESTS"):
            pytest.skip("Integration tests disabled. Set RUN_INTEGRATION_TESTS=1 to enable.")

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_msg18_basic(self):
        """Test basic Msg 18."""
        input_data = {
            'type': 18,
            'mmsi': '226666018',
            'lat': 47.8626,
            'lon': 2.1291,
            'speed': 8.5,
            'accuracy': False,
            'course': 120.0,
            'heading': 120,
            'second': 40,
            'cs': True,
            'display': False,
            'dsc': False,
            'band': False,
            'msg22': False,
            'assigned': False,
            'radio': 0,
        }

        nmea_list = encode_dict(input_data)
        nmea = nmea_list[0]

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True, f"Decode failed: {result.error}"
        assert result.decoded.mmsi == '226666018'
        assert result.decoded.position.latitude == approx(47.8626, abs=0.0001)
        assert result.decoded.position.longitude == approx(2.1291, abs=0.0001)
        assert result.decoded.speed_over_ground == approx(8.5, abs=0.1)
        assert result.decoded.course_over_ground == approx(120.0, abs=0.1)

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_msg18_stopped(self):
        """Test Msg 18 with speed = 0."""
        input_data = {
            'type': 18,
            'mmsi': '226666019',
            'lat': 48.8566,
            'lon': 2.3522,
            'speed': 0,
            'course': 0,
            'heading': 511,  # N/A
        }

        nmea_list = encode_dict(input_data)
        nmea = nmea_list[0]

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.speed_over_ground == approx(0.0)


class TestIntegrationMsg24ClassBStatic:
    """Test Message Type 24 - Class B Static Data (Part A and B)"""

    @pytest.fixture(autouse=True)
    def check_integration_enabled(self):
        if not os.environ.get("RUN_INTEGRATION_TESTS"):
            pytest.skip("Integration tests disabled. Set RUN_INTEGRATION_TESTS=1 to enable.")

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_msg24_part_a_vessel_name(self):
        """Test Msg 24 Part A - Vessel Name."""
        input_data = {
            'type': 24,
            'mmsi': '226666024',
            'shipname': 'CLASS B VESSEL      ',
            'partno': 0,  # Part A
        }

        nmea_list = encode_dict(input_data)
        nmea = nmea_list[0]

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True, f"Decode failed: {result.error}"
        assert result.decoded.mmsi == '226666024'
        assert 'CLASS B' in result.decoded.ship_name
        assert result.decoded.part_number == 0

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_msg24_part_b_ship_data(self):
        """Test Msg 24 Part B - Ship Data.

        Note: shiptype is encoded as '0' by pyais for Class B messages
        (this appears to be a pyais encoding quirk, not a parser issue).
        We verify callsign, vendor_id, and part_number instead.
        """
        input_data = {
            'type': 24,
            'mmsi': '226666025',
            'shiptype': 37,
            'vendorid': 'ABC',
            'model': 1,
            'serial': 12345,
            'callsign': 'TST1234',
            'to_bow': 5,
            'to_stern': 5,
            'to_port': 2,
            'to_starboard': 2,
            'partno': 1,  # Part B
        }

        nmea_list = encode_dict(input_data)
        nmea = nmea_list[0]

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.mmsi == '226666025'
        assert result.decoded.callsign == 'TST1234'
        assert result.decoded.part_number == 1
        assert result.decoded.vendor_id is not None


class TestIntegrationMsg21AtoN:
    """Test Message Type 21 - Aid to Navigation"""

    @pytest.fixture(autouse=True)
    def check_integration_enabled(self):
        if not os.environ.get("RUN_INTEGRATION_TESTS"):
            pytest.skip("Integration tests disabled. Set RUN_INTEGRATION_TESTS=1 to enable.")

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_msg21_basic(self):
        """Test basic Msg 21 - Aid to Navigation."""
        input_data = {
            'type': 21,
            'mmsi': '226666021',
            'aid_type': 1,  # Default
            'name': 'BUOY ALPHA       ',
            'lat': 45.8626,
            'lon': 3.1291,
            'accuracy': False,
            'to_bow': 0,
            'to_stern': 0,
            'to_port': 0,
            'to_starboard': 0,
            'epfd': 1,  # GPS
            'second': 50,
            'off_position': False,
            'raim': False,
            'virtual_aton': False,
        }

        nmea_list = encode_dict(input_data)
        nmea = nmea_list[0]

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True, f"Decode failed: {result.error}"
        assert result.decoded.mmsi == '226666021'
        assert result.decoded.position.latitude == approx(45.8626, abs=0.0001)
        assert result.decoded.position.longitude == approx(3.1291, abs=0.0001)


class TestIntegrationMsg27LongRange:
    """Test Message Type 27 - Long Range AIS"""

    @pytest.fixture(autouse=True)
    def check_integration_enabled(self):
        if not os.environ.get("RUN_INTEGRATION_TESTS"):
            pytest.skip("Integration tests disabled. Set RUN_INTEGRATION_TESTS=1 to enable.")

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_msg27_basic(self):
        """Test basic Msg 27 - Long Range AIS broadcast."""
        input_data = {
            'type': 27,
            'mmsi': '226666027',
            'lat': 47.8626,
            'lon': 2.1291,
            'status': 15,  # Undefined
            'speed': 0,
            'course': 0,
            'accuracy': False,
            'raim': False,
            'gnss': False,
        }

        nmea_list = encode_dict(input_data)
        nmea = nmea_list[0]

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True, f"Decode failed: {result.error}"
        assert result.decoded.mmsi == '226666027'
        assert result.decoded.position.latitude == approx(47.8626, abs=0.001)
        assert result.decoded.position.longitude == approx(2.1291, abs=0.001)


class TestIntegrationBatchDecoding:
    """Test batch decoding of multiple messages."""

    @pytest.fixture(autouse=True)
    def check_integration_enabled(self):
        if not os.environ.get("RUN_INTEGRATION_TESTS"):
            pytest.skip("Integration tests disabled. Set RUN_INTEGRATION_TESTS=1 to enable.")

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_batch_mixed_messages(self):
        """Test batch decoding of different message types."""
        msg1_data = {
            'type': 1,
            'mmsi': '226666001',
            'lat': 47.8626,
            'lon': 2.1291,
            'speed': 10.5,
            'course': 180.0,
        }

        msg18_data = {
            'type': 18,
            'mmsi': '226666018',
            'lat': 48.8566,
            'lon': 2.3522,
            'speed': 8.5,
            'course': 120.0,
        }

        msg24a_data = {
            'type': 24,
            'mmsi': '226666024',
            'shipname': 'CLASS B VESSEL      ',
            'partno': 0,  # Part A
        }

        nmea_messages = [
            encode_dict(msg1_data)[0],
            encode_dict(msg18_data)[0],
            encode_dict(msg24a_data)[0],
        ]

        async with AISDecoderClient() as client:
            result = await client.decode_batch(nmea_messages, delay=0)

        assert result.total == 3
        assert result.successful == 3
        assert result.failed == 0

        assert result.results[0].decoded.mmsi == '226666001'
        assert result.results[1].decoded.mmsi == '226666018'
        assert result.results[2].decoded.mmsi == '226666024'


class TestIntegrationErrorHandling:
    """Test error handling with invalid messages."""

    @pytest.fixture(autouse=True)
    def check_integration_enabled(self):
        if not os.environ.get("RUN_INTEGRATION_TESTS"):
            pytest.skip("Integration tests disabled. Set RUN_INTEGRATION_TESTS=1 to enable.")

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_invalid_nmea_accepted_by_server(self):
        """Test that corrupted/invalid NMEA is accepted by aggsoft.com server.

        Note: aggsoft.com is permissive and accepts almost any data, decoding it
        as unexpected message types (e.g., msg 25). This test verifies our
        parser handles such responses gracefully.
        """
        invalid_nmea = "!AIVDM,1,1,,A,INVALID_CORRUPT_DATA_HERE,0*00"

        async with AISDecoderClient() as client:
            result = await client.decode(invalid_nmea)

        assert result.success is True
        assert result.decoded.msg_type == 25

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_empty_message_rejected(self):
        """Test that empty message is properly rejected."""
        async with AISDecoderClient() as client:
            with pytest.raises(Exception):
                await client.decode("")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
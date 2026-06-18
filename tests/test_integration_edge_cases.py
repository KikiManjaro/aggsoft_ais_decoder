"""
Comprehensive integration tests for AIS decoder edge cases, error handling,
and various NMEA formats.

Run with: RUN_INTEGRATION_TESTS=1 pytest tests/test_integration_edge_cases.py -v
"""

import os
import pytest
from pyais.encode import encode_dict

from aggsoft_ais_decoder import AISDecoderClient
from aggsoft_ais_decoder.exceptions import InvalidMessageError, NetworkError, ParseError


def approx(expected, rel=1e-3, abs=1e-6):
    return pytest.approx(expected, rel=rel, abs=abs)


@pytest.fixture
def integration_enabled():
    if not os.environ.get("RUN_INTEGRATION_TESTS"):
        pytest.skip("Integration tests disabled. Set RUN_INTEGRATION_TESTS=1 to enable.")


class TestNMEAFormatVariations:
    """Test various NMEA message format variations."""

    @pytest.fixture(autouse=True)
    def check_enabled(self, integration_enabled):
        pass

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_dollar_prefix_instead_of_exclamation(self):
        """Test that $AIVDM prefix is accepted (alternative NMEA format)."""
        input_data = {
            'type': 1,
            'mmsi': '226666001',
            'lat': 47.8626,
            'lon': 2.1291,
            'speed': 10.0,
            'course': 180.0,
        }
        nmea_list = encode_dict(input_data)
        nmea = nmea_list[0].replace('!', '$', 1)

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.mmsi == '226666001'

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_whitespace_before_message(self):
        """Test message with leading whitespace."""
        input_data = {
            'type': 1,
            'mmsi': '226666002',
            'lat': 47.8626,
            'lon': 2.1291,
            'speed': 10.0,
        }
        nmea = encode_dict(input_data)[0]
        nmea = '   ' + nmea

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.mmsi == '226666002'

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_whitespace_after_message(self):
        """Test message with trailing whitespace."""
        input_data = {
            'type': 1,
            'mmsi': '226666003',
            'lat': 47.8626,
            'lon': 2.1291,
            'speed': 10.0,
        }
        nmea = encode_dict(input_data)[0] + '   \n\n'

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.mmsi == '226666003'

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_multiple_newlines_between_messages_multipart(self):
        """Test multipart messages with multiple newlines between sentences."""
        input_data = {
            'type': 5,
            'mmsi': '226666010',
            'shipname': 'TEST VESSEL ABC',
            'callsign': 'TST1234',
            'shiptype': 37,
        }
        nmea_list = encode_dict(input_data)
        assert len(nmea_list) == 2
        nmea = f'{nmea_list[0]}\n\n\n{nmea_list[1]}'

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.mmsi == '226666010'

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_crlf_windows_line_endings(self):
        """Test multipart with CRLF (Windows) line endings."""
        input_data = {
            'type': 5,
            'mmsi': '226666011',
            'shipname': 'WINDOWS CRLF TEST',
            'callsign': 'WIN1234',
            'shiptype': 37,
        }
        nmea_list = encode_dict(input_data)
        nmea = f'{nmea_list[0]}\r\n{nmea_list[1]}'

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.mmsi == '226666011'

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_list_of_strings_format(self):
        """Test sending messages as list[str] directly."""
        input_data = {
            'type': 1,
            'mmsi': '226666004',
            'lat': 47.8626,
            'lon': 2.1291,
            'speed': 15.0,
            'course': 90.0,
        }
        nmea_list = encode_dict(input_data)

        async with AISDecoderClient() as client:
            result = await client.decode(nmea_list)

        assert result.success is True
        assert result.decoded.mmsi == '226666004'
        assert result.decoded.position.latitude == approx(47.8626, abs=0.0001)

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_single_element_list(self):
        """Test sending single message as list[str] with one element."""
        input_data = {
            'type': 18,
            'mmsi': '226666018',
            'lat': 48.0,
            'lon': 3.0,
            'speed': 5.0,
        }
        nmea_list = encode_dict(input_data)

        async with AISDecoderClient() as client:
            result = await client.decode([nmea_list[0]])

        assert result.success is True
        assert result.decoded.mmsi == '226666018'


class TestNavigationStatusValues:
    """Test all navigation status values for Msg 1."""

    @pytest.fixture(autouse=True)
    def check_enabled(self, integration_enabled):
        pass

    @pytest.mark.parametrize("status_code,expected_status", [
        (0, "Under way using engine"),
        (1, "At anchor"),
        (2, "Not under command"),
        (3, "Restricted maneuverability"),
        (4, "Constrained by her draught"),
        (5, "Moored"),
        (6, "Aground"),
        (7, "Engaged in Fishing"),
        (8, "Under way sailing"),
        (9, "Reserved for future amendment (HSC)"),
        (10, "Reserved for future amendment (WIG)"),
        (11, "Reserved for future use"),
        (12, "Reserved for future use"),
        (13, "Reserved for future use"),
        (14, "AIS-SART"),
        (15, "Undefined"),
    ])
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_all_navigation_statuses(self, status_code, expected_status):
        """Test all 16 navigation status values."""
        input_data = {
            'type': 1,
            'mmsi': f'2266660{status_code:02d}',
            'lat': 47.0 + status_code * 0.1,
            'lon': 2.0,
            'status': status_code,
            'speed': 5.0,
            'course': 0.0,
        }

        nmea_list = encode_dict(input_data)
        nmea = nmea_list[0]

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True, f"Failed for status {status_code}: {result.error}"
        assert result.decoded.navigation_status == expected_status


class TestCoordinateEdgeCases:
    """Test coordinate edge cases and special locations."""

    @pytest.fixture(autouse=True)
    def check_enabled(self, integration_enabled):
        pass

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_zero_coordinates_gulf_of_guinea(self):
        """Test at (0, 0) - Gulf of Guinea."""
        input_data = {
            'type': 1,
            'mmsi': '226666001',
            'lat': 0.0,
            'lon': 0.0,
            'speed': 0.0,
            'course': 0.0,
        }
        nmea = encode_dict(input_data)[0]

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.position.latitude == approx(0.0, abs=0.0001)
        assert result.decoded.position.longitude == approx(0.0, abs=0.0001)

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_dateline_east(self):
        """Test at date line east (lon=180)."""
        input_data = {
            'type': 1,
            'mmsi': '226666002',
            'lat': 0.0,
            'lon': 180.0,
            'speed': 10.0,
        }
        nmea = encode_dict(input_data)[0]

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.position.longitude == approx(180.0, abs=0.001)

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_dateline_west(self):
        """Test at date line west (lon=-180)."""
        input_data = {
            'type': 1,
            'mmsi': '226666003',
            'lat': 0.0,
            'lon': -180.0,
            'speed': 10.0,
        }
        nmea = encode_dict(input_data)[0]

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.position.longitude == approx(-180.0, abs=0.001)

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_south_pole_region(self):
        """Test near South Pole (very negative latitude)."""
        input_data = {
            'type': 1,
            'mmsi': '226666004',
            'lat': -89.9999,
            'lon': 0.0,
            'speed': 0.0,
        }
        nmea = encode_dict(input_data)[0]

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.position.latitude == approx(-89.9999, abs=0.001)

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_north_pole_region(self):
        """Test near North Pole (very positive latitude)."""
        input_data = {
            'type': 1,
            'mmsi': '226666005',
            'lat': 89.9999,
            'lon': 0.0,
            'speed': 0.0,
        }
        nmea = encode_dict(input_data)[0]

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.position.latitude == approx(89.9999, abs=0.001)

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_channel_tunnel_uk(self):
        """Test in English Channel (near UK/France border)."""
        input_data = {
            'type': 1,
            'mmsi': '226666006',
            'lat': 50.0,
            'lon': -0.5,
            'speed': 8.0,
            'course': 90.0,
        }
        nmea = encode_dict(input_data)[0]

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.position.latitude == approx(50.0, abs=0.001)
        assert result.decoded.position.longitude == approx(-0.5, abs=0.001)

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_pacific_ocean(self):
        """Test in middle of Pacific Ocean."""
        input_data = {
            'type': 1,
            'mmsi': '226666007',
            'lat': -25.0,
            'lon': -140.0,
            'speed': 12.0,
            'course': 45.0,
        }
        nmea = encode_dict(input_data)[0]

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.position.latitude == approx(-25.0, abs=0.001)
        assert result.decoded.position.longitude == approx(-140.0, abs=0.001)


class TestSpeedAndCourseEdgeCases:
    """Test speed and course edge cases."""

    @pytest.fixture(autouse=True)
    def check_enabled(self, integration_enabled):
        pass

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_max_speed(self):
        """Test with maximum speed (102.2 knots)."""
        input_data = {
            'type': 1,
            'mmsi': '226666001',
            'lat': 47.0,
            'lon': 2.0,
            'speed': 102.2,
        }
        nmea = encode_dict(input_data)[0]

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.speed_over_ground == approx(102.2, abs=0.1)

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_course_360(self):
        """Test with course exactly 360 degrees."""
        input_data = {
            'type': 1,
            'mmsi': '226666002',
            'lat': 47.0,
            'lon': 2.0,
            'course': 360.0,
        }
        nmea = encode_dict(input_data)[0]

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.course_over_ground == approx(360.0, abs=0.1)

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_speed_zero_stationary(self):
        """Test with speed = 0 (stationary vessel)."""
        input_data = {
            'type': 1,
            'mmsi': '226666003',
            'lat': 47.0,
            'lon': 2.0,
            'speed': 0.0,
            'course': 0.0,
        }
        nmea = encode_dict(input_data)[0]

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.speed_over_ground == approx(0.0, abs=0.1)

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_turn_rate_max_right(self):
        """Test with maximum turn rate right (+720 deg/min)."""
        input_data = {
            'type': 1,
            'mmsi': '226666004',
            'lat': 47.0,
            'lon': 2.0,
            'turn': 720,
        }
        nmea = encode_dict(input_data)[0]

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.turn_rate is not None

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_turn_rate_max_left(self):
        """Test with maximum turn rate left (-720 deg/min)."""
        input_data = {
            'type': 1,
            'mmsi': '226666005',
            'lat': 47.0,
            'lon': 2.0,
            'turn': -720,
        }
        nmea = encode_dict(input_data)[0]

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.turn_rate is not None

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_heading_not_available(self):
        """Test with heading N/A. Aggsoft returns empty string for heading when not available."""
        input_data = {
            'type': 1,
            'mmsi': '226666006',
            'lat': 47.0,
            'lon': 2.0,
            'heading': 511,
        }
        nmea = encode_dict(input_data)[0]

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.heading is None or result.decoded.heading == ""


class TestTimestampEdgeCases:
    """Test timestamp edge cases."""

    @pytest.fixture(autouse=True)
    def check_enabled(self, integration_enabled):
        pass

    @pytest.mark.parametrize("second", [0, 30, 59])
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_various_timestamps(self, second):
        """Test with various timestamp seconds."""
        input_data = {
            'type': 1,
            'mmsi': '226666001',
            'lat': 47.0,
            'lon': 2.0,
            'second': second,
        }
        nmea = encode_dict(input_data)[0]

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True


class TestMessageTypeVariations:
    """Test various message types beyond Msg 1/5/18/21/24/27."""

    @pytest.fixture(autouse=True)
    def check_enabled(self, integration_enabled):
        pass

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_msg2_similar_to_msg1(self):
        """Test Msg 2 (Position Report Class A, scheduled)."""
        input_data = {
            'type': 2,
            'mmsi': '226666002',
            'lat': 47.8626,
            'lon': 2.1291,
            'speed': 10.0,
            'course': 180.0,
        }
        nmea = encode_dict(input_data)[0]

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.mmsi == '226666002'

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_msg3_similar_to_msg1(self):
        """Test Msg 3 (Position Report Class A, response)."""
        input_data = {
            'type': 3,
            'mmsi': '226666003',
            'lat': 47.8626,
            'lon': 2.1291,
            'speed': 10.0,
            'course': 180.0,
        }
        nmea = encode_dict(input_data)[0]

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.mmsi == '226666003'

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_msg4_base_station(self):
        """Test Msg 4 (Base Station Report)."""
        input_data = {
            'type': 4,
            'mmsi': '226666004',
            'lat': 47.0,
            'lon': 2.0,
            'year': 2024,
            'month': 6,
            'day': 15,
            'hour': 12,
            'minute': 30,
            'second': 45,
        }
        nmea = encode_dict(input_data)[0]

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.mmsi == '226666004'

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_msg19_extended_classb(self):
        """Test Msg 19 (Extended Class B CS Position Report)."""
        input_data = {
            'type': 19,
            'mmsi': '226666019',
            'lat': 47.8626,
            'lon': 2.1291,
            'speed': 8.5,
            'course': 120.0,
            'heading': 120,
        }
        nmea = encode_dict(input_data)[0]

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.mmsi == '226666019'

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_msg9_sar_aircraft(self):
        """Test Msg 9 (Standard SAR Aircraft Position Report)."""
        input_data = {
            'type': 9,
            'mmsi': '226666009',
            'lat': 47.8626,
            'lon': 2.1291,
            'altitude': 1000,
            'speed': 250.0,
            'course': 180.0,
        }
        nmea = encode_dict(input_data)[0]

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.mmsi == '226666009'

    @pytest.mark.skip(reason="pyais encode_dict doesn't support Msg 10 properly")
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_msg10_utc_date(self):
        """Test Msg 10 (UTC and Date Report)."""
        pass


class TestBatchDecodingVariations:
    """Test batch decoding with various message combinations."""

    @pytest.fixture(autouse=True)
    def check_enabled(self, integration_enabled):
        pass

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_batch_empty_list(self):
        """Test batch with empty list."""
        async with AISDecoderClient() as client:
            result = await client.decode_batch([])

        assert result.total == 0
        assert result.successful == 0
        assert result.failed == 0

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_batch_single_message(self):
        """Test batch with single message."""
        input_data = {
            'type': 1,
            'mmsi': '226666001',
            'lat': 47.0,
            'lon': 2.0,
        }
        nmea = encode_dict(input_data)[0]

        async with AISDecoderClient() as client:
            result = await client.decode_batch([nmea])

        assert result.total == 1
        assert result.successful == 1
        assert result.failed == 0

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_batch_mixed_valid_invalid(self):
        """Test batch with mix of valid and invalid messages."""
        valid_data = {
            'type': 1,
            'mmsi': '226666001',
            'lat': 47.0,
            'lon': 2.0,
        }
        valid_nmea = encode_dict(valid_data)[0]

        async with AISDecoderClient() as client:
            result = await client.decode_batch([valid_nmea, '!AIVDM,1,1,,A,INVALID', valid_nmea])

        assert result.total == 3
        assert result.successful >= 1

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_batch_multiple_multipart(self):
        """Test batch with multiple multipart messages (each message must be sent as joined sentences)."""
        msg5_data1 = {
            'type': 5,
            'mmsi': '226666010',
            'shipname': 'VESSEL ONE      ',
            'callsign': 'ONE1234',
            'shiptype': 37,
        }
        msg5_data2 = {
            'type': 5,
            'mmsi': '226666011',
            'shipname': 'VESSEL TWO      ',
            'callsign': 'TWO1234',
            'shiptype': 70,
        }

        nmea_list1 = encode_dict(msg5_data1)
        nmea_list2 = encode_dict(msg5_data2)

        msg1 = '\n'.join(nmea_list1)
        msg2 = '\n'.join(nmea_list2)

        async with AISDecoderClient() as client:
            result = await client.decode_batch([msg1, msg2], delay=0)

        assert result.total == 2
        assert result.successful == 2

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_batch_large_10_messages(self):
        """Test batch with 10 different messages."""
        messages = []
        for i in range(10):
            input_data = {
                'type': 1,
                'mmsi': f'2266660{i:02d}',
                'lat': 47.0 + i * 0.1,
                'lon': 2.0 + i * 0.1,
                'speed': 5.0 + i,
            }
            nmea = encode_dict(input_data)[0]
            messages.append(nmea)

        async with AISDecoderClient() as client:
            result = await client.decode_batch(messages, delay=0)

        assert result.total == 10
        assert result.successful == 10


class TestErrorHandling:
    """Test error handling for various invalid inputs."""

    @pytest.fixture(autouse=True)
    def check_enabled(self, integration_enabled):
        pass

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_empty_string_raises_error(self):
        """Test that empty string raises InvalidMessageError."""
        async with AISDecoderClient() as client:
            with pytest.raises(InvalidMessageError):
                await client.decode("")

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_whitespace_only_raises_error(self):
        """Test that whitespace-only message raises InvalidMessageError."""
        async with AISDecoderClient() as client:
            with pytest.raises(InvalidMessageError):
                await client.decode("   \n\t  ")

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_invalid_prefix_raises_error(self):
        """Test that invalid NMEA prefix raises InvalidMessageError."""
        async with AISDecoderClient() as client:
            with pytest.raises(InvalidMessageError):
                await client.decode("GPGLL,fix data here")

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_random_text_raises_error(self):
        """Test that random text raises InvalidMessageError."""
        async with AISDecoderClient() as client:
            with pytest.raises(InvalidMessageError):
                await client.decode("This is not an AIS message at all!")

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_empty_list_raises_error(self):
        """Test that empty list raises InvalidMessageError."""
        async with AISDecoderClient() as client:
            with pytest.raises(InvalidMessageError):
                await client.decode([])

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_list_with_all_empty_strings_raises_error(self):
        """Test that list with only empty strings raises error."""
        async with AISDecoderClient() as client:
            with pytest.raises(InvalidMessageError):
                await client.decode(["", "  ", "\n"])


class TestSpecialDataHandling:
    """Test handling of special characters and edge case data."""

    @pytest.fixture(autouse=True)
    def check_enabled(self, integration_enabled):
        pass

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_special_shipname_characters(self):
        """Test Msg 5 with special characters in shipname."""
        input_data = {
            'type': 5,
            'mmsi': '226666010',
            'shipname': 'OCEAN EXPLORER   ',
            'callsign': 'EXP1234',
            'shiptype': 60,
            'to_bow': 20,
            'to_stern': 30,
            'to_port': 5,
            'to_starboard': 5,
            'epfd': 1,
        }
        nmea_list = encode_dict(input_data)

        async with AISDecoderClient() as client:
            result = await client.decode(nmea_list)

        assert result.success is True
        assert 'OCEAN' in result.decoded.ship_name

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_destination_with_special_chars(self):
        """Test Msg 5 with special characters in destination."""
        input_data = {
            'type': 5,
            'mmsi': '226666011',
            'shipname': 'TEST VESSEL      ',
            'callsign': 'TST1234',
            'shiptype': 37,
            'destination': 'PORT-DE-BOUCAUD',
            'epfd': 1,
        }
        nmea_list = encode_dict(input_data)

        async with AISDecoderClient() as client:
            result = await client.decode(nmea_list)

        assert result.success is True

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_callsign_with_numbers(self):
        """Test Msg 5 with callsign containing numbers."""
        input_data = {
            'type': 5,
            'mmsi': '226666012',
            'shipname': 'TEST VESSEL      ',
            'callsign': '5X1234',
            'shiptype': 37,
            'epfd': 1,
        }
        nmea_list = encode_dict(input_data)

        async with AISDecoderClient() as client:
            result = await client.decode(nmea_list)

        assert result.success is True
        assert result.decoded.callsign is not None


class TestConfigurationOptions:
    """Test various configuration options."""

    @pytest.fixture(autouse=True)
    def check_enabled(self, integration_enabled):
        pass

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_html_fallback_disabled_with_valid_json(self):
        """Test with enable_html_fallback=False and valid JSON response."""
        input_data = {
            'type': 1,
            'mmsi': '226666001',
            'lat': 47.0,
            'lon': 2.0,
            'speed': 10.0,
        }
        nmea = encode_dict(input_data)[0]

        async with AISDecoderClient(enable_html_fallback=False) as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.mmsi == '226666001'

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_html_fallback_enabled_explicit(self):
        """Test with enable_html_fallback=True explicitly set."""
        input_data = {
            'type': 1,
            'mmsi': '226666002',
            'lat': 47.0,
            'lon': 2.0,
            'speed': 10.0,
        }
        nmea = encode_dict(input_data)[0]

        async with AISDecoderClient(enable_html_fallback=True) as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.mmsi == '226666002'

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_custom_timeout(self):
        """Test with custom timeout value."""
        input_data = {
            'type': 1,
            'mmsi': '226666003',
            'lat': 47.0,
            'lon': 2.0,
            'speed': 10.0,
        }
        nmea = encode_dict(input_data)[0]

        async with AISDecoderClient(timeout=30.0) as client:
            result = await client.decode(nmea)

        assert result.success is True

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_multiple_clients_sequential(self):
        """Test creating multiple clients sequentially."""
        input_data = {
            'type': 1,
            'mmsi': '226666004',
            'lat': 47.0,
            'lon': 2.0,
        }

        async with AISDecoderClient() as client1:
            result1 = await client1.decode(encode_dict(input_data)[0])
            assert result1.success is True

        async with AISDecoderClient() as client2:
            result2 = await client2.decode(encode_dict(input_data)[0])
            assert result2.success is True


class TestRapidRequests:
    """Test rapid successive requests without delays."""

    @pytest.fixture(autouse=True)
    def check_enabled(self, integration_enabled):
        pass

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_rapid_5_requests_no_delay(self):
        """Test 5 rapid requests without any delay.

        Note: May hit rate limiting - we allow some failures due to 429 errors.
        """
        messages = []
        for i in range(5):
            input_data = {
                'type': 1,
                'mmsi': f'2266660{i:02d}',
                'lat': 47.0 + i,
                'lon': 2.0 + i,
                'speed': 10.0,
            }
            nmea = encode_dict(input_data)[0]
            messages.append(nmea)

        async with AISDecoderClient() as client:
            results = []
            for msg in messages:
                try:
                    result = await client.decode(msg)
                    results.append(result)
                except Exception:
                    results.append(None)

        successful = sum(1 for r in results if r and r.success)
        assert successful >= 3

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_rapid_10_requests_no_delay(self):
        """Test 10 rapid requests without any delay.

        Note: Will likely hit rate limiting - we allow partial success.
        """
        messages = []
        for i in range(10):
            input_data = {
                'type': 18,
                'mmsi': f'226666{i:02d}',
                'lat': 47.0 + i * 0.5,
                'lon': 2.0 + i * 0.5,
                'speed': 5.0 + i * 0.5,
            }
            nmea = encode_dict(input_data)[0]
            messages.append(nmea)

        async with AISDecoderClient() as client:
            results = []
            for msg in messages:
                try:
                    result = await client.decode(msg)
                    results.append(result)
                except Exception:
                    results.append(None)

        successful = sum(1 for r in results if r and r.success)
        assert successful >= 1


class TestModuleLevelFunctions:
    """Test module-level convenience functions."""

    @pytest.fixture(autouse=True)
    def check_enabled(self, integration_enabled):
        pass

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_module_decode_function(self):
        """Test the module-level decode() function."""
        import asyncio
        from aggsoft_ais_decoder import decode

        input_data = {
            'type': 1,
            'mmsi': '226666001',
            'lat': 47.0,
            'lon': 2.0,
            'speed': 10.0,
        }
        nmea = encode_dict(input_data)[0]

        await asyncio.sleep(1)
        result = await decode(nmea)

        assert result.success is True
        assert result.decoded.mmsi == '226666001'

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_module_decode_function_with_list(self):
        """Test the module-level decode() function with list[str]."""
        import asyncio
        from aggsoft_ais_decoder import decode

        input_data = {
            'type': 5,
            'mmsi': '226666010',
            'shipname': 'MODULE TEST     ',
            'callsign': 'MOD1234',
            'shiptype': 37,
        }
        nmea_list = encode_dict(input_data)

        await asyncio.sleep(1)
        result = await decode(nmea_list)

        assert result.success is True
        assert result.decoded.mmsi == '226666010'

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_module_decode_batch_function(self):
        """Test the module-level decode_batch() function."""
        import asyncio
        from aggsoft_ais_decoder import decode_batch

        await asyncio.sleep(1)
        messages = []
        for i in range(3):
            input_data = {
                'type': 1,
                'mmsi': f'2266660{i:02d}',
                'lat': 47.0,
                'lon': 2.0,
            }
            nmea = encode_dict(input_data)[0]
            messages.append(nmea)

        result = await decode_batch(messages, delay=0.5)

        assert result.total == 3
        assert result.successful >= 1


class TestResponseFieldExtraction:
    """Test that various fields are properly extracted from responses."""

    @pytest.fixture(autouse=True)
    def check_enabled(self, integration_enabled):
        pass

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_msg1_all_basic_fields(self):
        """Test Msg 1 extracts all basic fields correctly."""
        import asyncio
        input_data = {
            'type': 1,
            'mmsi': '226666001',
            'lat': 47.8626,
            'lon': 2.1291,
            'speed': 10.5,
            'course': 180.0,
            'heading': 90,
            'status': 0,
            'turn': 0,
            'second': 30,
            'raim': False,
        }
        nmea = encode_dict(input_data)[0]

        await asyncio.sleep(1)
        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.mmsi == '226666001'
        assert result.decoded.position.latitude == approx(47.8626, abs=0.0001)
        assert result.decoded.position.longitude == approx(2.1291, abs=0.0001)
        assert result.decoded.speed_over_ground == approx(10.5, abs=0.1)
        assert result.decoded.course_over_ground == approx(180.0, abs=0.1)
        assert result.decoded.heading == 90
        assert result.decoded.navigation_status == "Under way using engine"
        assert result.decoded.msg_type == 1

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_msg5_dimensions_extracted(self):
        """Test Msg 5 extracts dimension fields correctly."""
        input_data = {
            'type': 5,
            'mmsi': '226666010',
            'shipname': 'BIG CARGO         ',
            'callsign': 'CG1234',
            'shiptype': 70,
            'to_bow': 50,
            'to_stern': 60,
            'to_port': 10,
            'to_starboard': 15,
            'epfd': 1,
            'draught': 8.5,
        }
        nmea_list = encode_dict(input_data)

        async with AISDecoderClient() as client:
            result = await client.decode(nmea_list)

        assert result.success is True
        assert result.decoded.dimensions is not None
        assert result.decoded.dimensions.to_bow == 50
        assert result.decoded.dimensions.to_stern == 60
        assert result.decoded.draught == approx(8.5, abs=0.1)

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_msg21_aid_type_extracted(self):
        """Test Msg 21 extracts aid type correctly."""
        import asyncio
        input_data = {
            'type': 21,
            'mmsi': '226666021',
            'aid_type': 5,  # Light
            'name': 'LIGHTHOUSE       ',
            'lat': 45.0,
            'lon': 3.0,
        }
        nmea = encode_dict(input_data)[0]

        await asyncio.sleep(1)
        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.msg_type == 21

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_msg18_no_navigation_status(self):
        """Test Msg 18 doesn't have navigation_status (Class B doesn't report it)."""
        input_data = {
            'type': 18,
            'mmsi': '226666018',
            'lat': 47.0,
            'lon': 2.0,
            'speed': 10.0,
        }
        nmea = encode_dict(input_data)[0]

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.msg_type == 18
        assert result.decoded.navigation_status is None

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_msg24_part_number_extracted(self):
        """Test Msg 24 correctly extracts part number."""
        import asyncio
        input_data = {
            'type': 24,
            'mmsi': '226666024',
            'shipname': 'PART B TEST      ',
            'partno': 1,
            'callsign': 'PBT1234',
            'shiptype': 37,
        }
        nmea = encode_dict(input_data)[0]

        await asyncio.sleep(1)
        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.decoded.part_number == 1


class TestCorruptedAndInvalidData:
    """Test handling of corrupted or malformed data."""

    @pytest.fixture(autouse=True)
    def check_enabled(self, integration_enabled):
        pass

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_aggsoft_returns_error_for_corrupted_data(self):
        """Aggsoft is permissive and returns an Error response for corrupted data."""
        corrupted_nmea = "!AIVDM,1,1,,A,TOTALLY_INVALID_DATA_HERE,0*00"

        async with AISDecoderClient() as client:
            result = await client.decode(corrupted_nmea)

        assert result.success is True
        assert result.decoded.mmsi is None
        assert result.decoded.ship_name is None

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_very_short_nmea(self):
        """Test with very short but structurally valid NMEA - aggsoft returns success with no data."""
        short_nmea = "!AIVDM,1,1,,A,0*00"

        async with AISDecoderClient() as client:
            result = await client.decode(short_nmea)

        assert result.success is True
        assert result.decoded.mmsi is None

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_nmea_with_wrong_checksum(self):
        """Test that wrong checksum is still accepted (aggsoft doesn't validate)."""
        import asyncio
        input_data = {
            'type': 1,
            'mmsi': '226666001',
            'lat': 47.0,
            'lon': 2.0,
        }
        nmea = encode_dict(input_data)[0]
        nmea = nmea[:-2] + "FF"

        await asyncio.sleep(1)
        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_mixed_valid_invalid_in_list_raises_error(self):
        """Test decode() with list containing invalid message raises InvalidMessageError.

        Note: Validation happens before sending, so invalid messages in a list
        will cause the entire decode to fail. This is expected behavior.
        """
        input_data = {
            'type': 1,
            'mmsi': '226666001',
            'lat': 47.0,
            'lon': 2.0,
        }
        valid_nmea = encode_dict(input_data)[0]

        async with AISDecoderClient() as client:
            with pytest.raises(InvalidMessageError):
                await client.decode([valid_nmea, "INVALID", valid_nmea])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
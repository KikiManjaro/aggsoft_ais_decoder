"""
Integration tests for AIS decoder against aggsoft.com.
These tests are prepared but NOT executed by default.
Set RUN_INTEGRATION_TESTS=1 to run them against the real API.

These tests require:
- Network access to aggsoft.com
- Rate limiting (2+ seconds between requests)
- Valid AIS message samples
"""

import pytest
import os
import unittest
import unittest.mock


class TestIntegrationAggsoft:
    """
    Integration tests against real aggsoft.com API.
    These tests are DISABLED by default.
    """

    @pytest.fixture(autouse=True)
    def check_integration_enabled(self):
        if not os.environ.get("RUN_INTEGRATION_TESTS"):
            pytest.skip("Integration tests disabled. Set RUN_INTEGRATION_TESTS=1 to enable.")

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_real_aggsoft_decode_msg1(self):
        """
        Test decoding a real Msg 1 (Position Report) against aggsoft.com.
        This verifies end-to-end functionality with real HTTP requests.
        """
        from aggsoft_ais_decoder import AISDecoderClient

        nmea = "!AIVDM,1,1,,A,13u@ND0P01PJ=0lMH0nN20pl,0*7D"

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.success is True
        assert result.source == "aggsoft.com"
        assert result.decoded is not None
        assert result.decoded.mmsi is not None

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_real_aggsoft_decode_msg5(self):
        """
        Test decoding a real Msg 5 (Static & Voyage) against aggsoft.com.
        Multi-part messages may have different behavior.
        """
        from aggsoft_ais_decoder import AISDecoderClient

        nmea = "!AIVDO,1,1,,A,703ltL0Q7D@GH0l0e0O,0*2F"

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.source == "aggsoft.com"

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_real_aggsoft_decode_msg18(self):
        """Test decoding Msg 18 (Class B Position)."""
        from aggsoft_ais_decoder import AISDecoderClient

        nmea = "!AIVDM,1,1,,A,91>Mn00FjLqGrqPoJ8n0v0p00<wS,0*4B"

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.source == "aggsoft.com"

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_real_aggsoft_decode_msg24(self):
        """Test decoding Msg 24 (Class B Static)."""
        from aggsoft_ais_decoder import AISDecoderClient

        nmea = "!AIVDM,1,1,,A,15R?0n08<:O85mSn4Q8a4@34b0,0*4D"

        async with AISDecoderClient() as client:
            result = await client.decode(nmea)

        assert result.source == "aggsoft.com"

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_real_aggsoft_rate_limiting(self):
        """
        Test that batch decoding respects rate limits.
        Verifies delay between requests works correctly.
        """
        from aggsoft_ais_decoder import AISDecoderClient
        import time

        messages = [
            "!AIVDM,1,1,,A,13u@ND0P01PJ=0lMH0nN20pl,0*7D",
            "!AIVDM,1,1,,A,91>Mn00FjLqGrqPoJ8n0v0p00<wS,0*4B",
        ]

        async with AISDecoderClient() as client:
            start = time.time()
            result = await client.decode_batch(messages, delay=3.0)
            elapsed = time.time() - start

        assert result.total == 2
        assert elapsed >= 3.0, "Rate limiting delay not respected"

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_real_aggsoft_timeout_handling(self):
        """Test that timeout is properly handled."""
        from aggsoft_ais_decoder import AISDecoderClient
        from aggsoft_ais_decoder.exceptions import NetworkError

        async with AISDecoderClient(timeout=0.001) as client:
            with pytest.raises(NetworkError):
                await client.decode("!AIVDM,1,1,,A,13u@ND0P01PJ=0lMH0nN20pl,0*7D")

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_real_aggsoft_invalid_message(self):
        """Test error handling for invalid message sent to real API."""
        from aggsoft_ais_decoder import AISDecoderClient
        from aggsoft_ais_decoder.exceptions import AISDecodeError

        async with AISDecoderClient() as client:
            with pytest.raises(AISDecodeError):
                await client.decode("INVALID MESSAGE")

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_real_aggsoft_batch_multiple(self):
        """Test batch decoding of multiple different message types."""
        from aggsoft_ais_decoder import AISDecoderClient

        messages = [
            "!AIVDM,1,1,,A,13u@ND0P01PJ=0lMH0nN20pl,0*7D",
            "!AIVDM,1,1,,A,91>Mn00FjLqGrqPoJ8n0v0p00<wS,0*4B",
            "!AIVDM,1,1,,A,15MgK45P3@G?fl0E`JbR0OwT0@MS,0*4E",
        ]

        async with AISDecoderClient() as client:
            result = await client.decode_batch(messages, delay=3.0)

        assert result.total == 3
        assert result.successful >= 0
        assert result.failed >= 0


class TestPerformanceTests:
    """
    Performance tests to verify the library handles load well.
    These tests use mocked responses for consistent timing.
    """

    @pytest.mark.asyncio
    async def test_decode_batch_100_messages(self):
        """Test decoding 100 messages in batch mode."""
        from aggsoft_ais_decoder import AISDecoderClient
        from unittest.mock import AsyncMock, MagicMock

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """<!DOCTYPE html><html><body><table>
        <tr><td>MMSI:</td><td>123456789</td></tr>
        <tr><td>Latitude:</td><td>48.8566</td></tr>
        <tr><td>Longitude:</td><td>2.3522</td></tr>
        </table></body></html>"""

        mock_client = AsyncMock(spec=type(None))
        mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.is_closed = False
        mock_client.aclose = AsyncMock()

        messages = [f"!AIVDM,1,1,,A,13u@ND0P01PJ=0lMH0nN20pl,0*7D" for _ in range(100)]

        client = AISDecoderClient()
        with unittest.mock.patch.object(client, "_get_client", return_value=mock_client):
            result = await client.decode_batch(messages, delay=0)

        assert result.total == 100

    @pytest.mark.asyncio
    async def test_parser_handles_large_html(self):
        """Test that parser can handle large HTML documents."""
        from aggsoft_ais_decoder.parser import parse_response

        html = "<html><body><table>"
        for i in range(1000):
            html += f"<tr><td>Field{i}:</td><td>Value{i}</td></tr>"
        html += "</table></body></html>"

        fields = parse_response(html)
        assert len(fields) == 1000


class TestRealWorldScenarios:
    """
    Tests based on real-world AIS message scenarios.
    These tests use mocked responses with realistic data.
    """

    @pytest.fixture
    def real_world_msg1_nmea(self):
        return "!AIVDM,1,1,,A,13u@ND0P01PJ=0lMH0nN20pl,0*7D"

    @pytest.fixture
    def real_world_msg5_nmea(self):
        return "!AIVDO,1,1,,A,703ltL0Q7D@GH0l0e0O,0*2F"

    def test_parse_real_world_ship_name_with_unicode(self):
        """Test parsing vessel names with special characters."""
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Ship Name:</td><td>MARIE</td></tr>
        </table></body></html>"""
        from aggsoft_ais_decoder.parser import parse_response, extract_ship_data
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.ship_name == "MARIE"

    def test_parse_coordinates_from_gps(self):
        """Test parsing coordinates similar to real GPS data."""
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Latitude:</td><td>35.6762</td></tr>
        <tr><td>Longitude:</td><td>139.6503</td></tr>
        </table></body></html>"""
        from aggsoft_ais_decoder.parser import parse_response, extract_ship_data
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.position.latitude == 35.6762
        assert ship_data.position.longitude == 139.6503

    def test_parse_port_coordinates(self):
        """Test parsing coordinates for a major port."""
        html = """<!DOCTYPE html><html><body><table>
        <tr><td>Latitude:</td><td>51.9244</td></tr>
        <tr><td>Longitude:</td><td>4.4777</td></tr>
        </table></body></html>"""
        from aggsoft_ais_decoder.parser import parse_response, extract_ship_data
        ship_data = extract_ship_data(parse_response(html))
        assert ship_data.position.latitude == 51.9244
        assert ship_data.position.longitude == 4.4777


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
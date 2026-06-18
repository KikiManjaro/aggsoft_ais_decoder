"""
Tests for input validation and error handling.
Tests verify correct handling of invalid inputs, malformed messages, and edge cases.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aggsoft_ais_decoder.client import AISDecoderClient, decode
from aggsoft_ais_decoder.exceptions import InvalidMessageError, NetworkError, ParseError


class TestNMEAMessageValidation:
    """Test NMEA message format validation"""

    @pytest.mark.asyncio
    async def test_empty_message_raises_error(self):
        client = AISDecoderClient()
        with pytest.raises(InvalidMessageError, match="Empty message"):
            await client.decode("")

    @pytest.mark.asyncio
    async def test_whitespace_only_message_raises_error(self):
        client = AISDecoderClient()
        with pytest.raises(InvalidMessageError, match="Empty message"):
            await client.decode("   \n\t  ")

    @pytest.mark.asyncio
    async def test_invalid_prefix_raises_error(self):
        client = AISDecoderClient()
        with pytest.raises(InvalidMessageError, match="Invalid AIS message format"):
            await client.decode("GPGLL,fix data here")

    @pytest.mark.asyncio
    async def test_random_text_raises_error(self):
        client = AISDecoderClient()
        with pytest.raises(InvalidMessageError, match="Invalid AIS message format"):
            await client.decode("This is not an AIS message")

    @pytest.mark.asyncio
    async def test_too_short_message_rejected(self):
        client = AISDecoderClient()
        with pytest.raises(InvalidMessageError):
            await client.decode("")

    @pytest.mark.asyncio
    async def test_missing_checksum_still_sent_to_server(self):
        from unittest.mock import AsyncMock, MagicMock, patch

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        mock_client = AsyncMock(spec=type(None))
        mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.is_closed = False
        mock_client.aclose = AsyncMock()

        client = AISDecoderClient()
        with patch.object(client, "_get_client", return_value=mock_client):
            with pytest.raises(ParseError):
                await client.decode("!AIVDM,1,1,,A,")

    @pytest.mark.asyncio
    async def test_valid_aivdm_prefix(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """<!DOCTYPE html><html><body><table>
        <tr><td>MMSI:</td><td>123456789</td></tr>
        </table></body></html>"""

        mock_client = AsyncMock(spec=type(None))
        mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.is_closed = False
        mock_client.aclose = AsyncMock()

        client = AISDecoderClient()
        with patch.object(client, "_get_client", return_value=mock_client):
            result = await client.decode("!AIVDM,1,1,,A,13u@ND0P01PJ=0lMH0nN20pl,0*7D")
        assert result.success is True

    @pytest.mark.asyncio
    async def test_valid_aivdo_prefix(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """<!DOCTYPE html><html><body><table>
        <tr><td>MMSI:</td><td>987654321</td></tr>
        </table></body></html>"""

        mock_client = AsyncMock(spec=type(None))
        mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.is_closed = False
        mock_client.aclose = AsyncMock()

        client = AISDecoderClient()
        with patch.object(client, "_get_client", return_value=mock_client):
            result = await client.decode("!AIVDO,1,1,,A,91>Mn00FjLqGrqPoJ8n0v0p00<wS,0*4B")
        assert result.success is True

    @pytest.mark.asyncio
    async def test_valid_dollar_aivdm_prefix(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """<!DOCTYPE html><html><body><table>
        <tr><td>MMSI:</td><td>111222333</td></tr>
        </table></body></html>"""

        mock_client = AsyncMock(spec=type(None))
        mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.is_closed = False
        mock_client.aclose = AsyncMock()

        client = AISDecoderClient()
        with patch.object(client, "_get_client", return_value=mock_client):
            result = await client.decode("$AIVDM,1,1,,A,13u@ND0P01PJ=0lMH0nN20pl,0*7D")
        assert result.success is True


class TestCorruptedNMEAMessages:
    """Test handling of corrupted or malformed NMEA messages"""

    def test_nmea_validation_strips_whitespace(self):
        client = AISDecoderClient()
        try:
            client._validate_message("  !AIVDM,1,1,,A,13u@ND0P01PJ=0lMH0nN20pl,0*7D  ")
        except InvalidMessageError:
            pytest.fail("Whitespace-only prefix should be stripped before validation")

    def test_nmea_with_newlines(self):
        client = AISDecoderClient()
        try:
            client._validate_message("!AIVDM,1,1,,A,13u@ND0P01PJ=0lMH0nN20pl,0*7D\n")
        except InvalidMessageError:
            pytest.fail("Trailing newline should not cause validation failure")

    def test_nmea_with_carriage_return(self):
        client = AISDecoderClient()
        try:
            client._validate_message("!AIVDM,1,1,,A,13u@ND0P01PJ=0lMH0nN20pl,0*7D\r")
        except InvalidMessageError:
            pytest.fail("Trailing CR should not cause validation failure")


class TestNetworkErrors:
    """Test handling of network errors"""

    @pytest.mark.asyncio
    async def test_timeout_error(self):
        import httpx

        mock_client = AsyncMock(spec=type(None))
        mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
        mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("Connection timeout"))
        mock_client.is_closed = False
        mock_client.aclose = AsyncMock()

        client = AISDecoderClient()
        with patch.object(client, "_get_client", return_value=mock_client):
            with pytest.raises(NetworkError, match="Request timeout"):
                await client.decode("!AIVDM,1,1,,A,13u@ND0P01PJ=0lMH0nN20pl,0*7D")

    @pytest.mark.asyncio
    async def test_http_error(self):
        import httpx

        mock_client = AsyncMock(spec=type(None))
        mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
        mock_client.post = AsyncMock(side_effect=httpx.HTTPError("Server error"))
        mock_client.is_closed = False
        mock_client.aclose = AsyncMock()

        client = AISDecoderClient()
        with patch.object(client, "_get_client", return_value=mock_client):
            with pytest.raises(NetworkError, match="HTTP error"):
                await client.decode("!AIVDM,1,1,,A,13u@ND0P01PJ=0lMH0nN20pl,0*7D")

    @pytest.mark.asyncio
    async def test_connection_error(self):
        import httpx

        mock_client = AsyncMock(spec=type(None))
        mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
        mock_client.post = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))
        mock_client.is_closed = False
        mock_client.aclose = AsyncMock()

        client = AISDecoderClient()
        with patch.object(client, "_get_client", return_value=mock_client):
            with pytest.raises(NetworkError):
                await client.decode("!AIVDM,1,1,,A,13u@ND0P01PJ=0lMH0nN20pl,0*7D")


class TestParseErrors:
    """Test handling of parse errors"""

    @pytest.mark.asyncio
    async def test_empty_response_parsed(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = ""

        mock_client = AsyncMock(spec=type(None))
        mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.is_closed = False
        mock_client.aclose = AsyncMock()

        client = AISDecoderClient()
        with patch.object(client, "_get_client", return_value=mock_client):
            result = await client.decode("!AIVDM,1,1,,A,13u@ND0P01PJ=0lMH0nN20pl,0*7D")
            assert result.success is False

    @pytest.mark.asyncio
    async def test_html_without_table_parsed(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><p>No table here</p></body></html>"

        mock_client = AsyncMock(spec=type(None))
        mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.is_closed = False
        mock_client.aclose = AsyncMock()

        client = AISDecoderClient()
        with patch.object(client, "_get_client", return_value=mock_client):
            result = await client.decode("!AIVDM,1,1,,A,13u@ND0P01PJ=0lMH0nN20pl,0*7D")
            assert result.decoded is None
            assert result.success is False


class TestBatchErrorHandling:
    """Test error handling in batch operations"""

    @pytest.mark.asyncio
    async def test_batch_partial_failure(self):
        messages = [
            "!AIVDM,1,1,,A,13u@ND0P01PJ=0lMH0nN20pl,0*7D",
            "!AIVDM,1,1,,A,91>Mn00FjLqGrqPoJ8n0v0p00<wS,0*4B",
            "INVALID",
            "!AIVDM,1,1,,A,15MgK45P3@G?fl0E`JbR0OwT0@MS,0*4E",
        ]

        post_call_count = [0]
        def side_effect(*args, **kwargs):
            post_call_count[0] += 1
            if post_call_count[0] == 4:
                raise InvalidMessageError("Post processing error")
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = """<!DOCTYPE html><html><body><table>
            <tr><td>MMSI:</td><td>123456789</td></tr>
            </table></body></html>"""
            return mock_response

        mock_client = AsyncMock(spec=type(None))
        mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
        mock_client.post = AsyncMock(side_effect=side_effect)
        mock_client.is_closed = False
        mock_client.aclose = AsyncMock()

        client = AISDecoderClient()
        with patch.object(client, "_get_client", return_value=mock_client):
            result = await client.decode_batch(messages, delay=0.01)

        assert result.total == 4
        assert result.successful == 3
        assert result.failed == 1

    @pytest.mark.asyncio
    async def test_batch_all_failures(self):
        messages = ["INVALID1", "INVALID2", "INVALID3"]

        client = AISDecoderClient()
        result = await client.decode_batch(messages, delay=0.01)

        assert result.total == 3
        assert result.successful == 0
        assert result.failed == 3

    @pytest.mark.asyncio
    async def test_batch_empty_list(self):
        client = AISDecoderClient()
        result = await client.decode_batch([], delay=0.01)

        assert result.total == 0
        assert result.successful == 0
        assert result.failed == 0


class TestLargeHTMLParsing:
    """Test parsing of large HTML responses"""

    def test_large_html_with_many_fields(self):
        from aggsoft_ais_decoder.parser import parse_response
        html = "<html><body><table>"
        for i in range(100):
            html += f"<tr><td>Field {i}:</td><td>Value {i}</td></tr>"
        html += "</table></body></html>"

        fields = parse_response(html)
        assert len(fields) == 100

    def test_html_with_nested_tables(self):
        from aggsoft_ais_decoder.parser import parse_response
        html = """<!DOCTYPE html>
<html>
<body>
<table>
<tr><td>Outer Field:</td><td>Outer Value</td></tr>
</table>
<table>
<tr><td>Inner Field:</td><td>Inner Value</td></tr>
</table>
</body>
</html>"""
        fields = parse_response(html)
        assert "outer field" in fields
        assert "inner field" in fields


class TestModuleLevelFunctions:
    """Test module-level convenience functions"""

    @pytest.mark.asyncio
    async def test_decode_function_success(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """<!DOCTYPE html><html><body><table>
        <tr><td>MMSI:</td><td>123456789</td></tr>
        </table></body></html>"""

        mock_client = AsyncMock(spec=type(None))
        mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.is_closed = False
        mock_client.aclose = AsyncMock()

        with patch("aggsoft_ais_decoder.client.httpx.AsyncClient", return_value=mock_client):
            result = await decode("!AIVDM,1,1,,A,13u@ND0P01PJ=0lMH0nN20pl,0*7D")
        assert result.success is True

    @pytest.mark.asyncio
    async def test_decode_function_invalid_message(self):
        with pytest.raises(InvalidMessageError):
            await decode("INVALID")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
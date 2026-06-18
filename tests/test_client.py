import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
from aggsoft_ais_decoder.client import AISDecoderClient, decode, decode_batch
from aggsoft_ais_decoder.exceptions import InvalidMessageError, NetworkError
from aggsoft_ais_decoder.models import AISDecodeResponse


class TestAISDecoderClient:
    @pytest.fixture
    def client(self):
        return AISDecoderClient()

    def test_validate_message_valid(self, client):
        valid_messages = [
            "!AIVDM,1,1,,A,13u@ND0P01PJ=0lMH0nN20pl,0*7D",
            "!AIVDO,1,1,,A,703ltL0Q7D@GH0l0e0O,0*2F",
            "$AIVDM,1,1,,A,15MgK45P3@G?fl0E`JbR0OwT0@MS,0*4E",
            "$AIVDO,1,1,,A,15MgK45P3@G?fl0E`JbR0OwT0@MS,0*4E",
        ]
        for msg in valid_messages:
            client._validate_message(msg)

    def test_validate_message_invalid_empty(self, client):
        with pytest.raises(InvalidMessageError, match="Empty message"):
            client._validate_message("")

    def test_validate_message_invalid_empty_whitespace(self, client):
        with pytest.raises(InvalidMessageError, match="Empty message"):
            client._validate_message("   \n\t  ")

    def test_validate_message_invalid_format(self, client):
        with pytest.raises(InvalidMessageError, match="Invalid AIS message format"):
            client._validate_message("GPGLL,fix data")

    @pytest.mark.asyncio
    async def test_decode_success(self, client, sample_html_response):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = sample_html_response

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.is_closed = False
        mock_client.aclose = AsyncMock()

        with patch.object(client, "_get_client", return_value=mock_client):
            result = await client.decode("!AIVDM,1,1,,A,13u@ND0P01PJ=0lMH0nN20pl,0*7D")

        assert isinstance(result, AISDecodeResponse)
        assert result.success is True
        assert result.source == "aggsoft.com"
        assert result.decoded is not None
        assert result.decoded.mmsi == "226666007"
        assert result.decoded.ship_name == "TEST VESSEL"

    @pytest.mark.asyncio
    async def test_decode_http_error(self, client):
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
        mock_client.post = AsyncMock(side_effect=httpx.HTTPError("Connection failed"))
        mock_client.is_closed = False
        mock_client.aclose = AsyncMock()

        with patch.object(client, "_get_client", return_value=mock_client):
            with pytest.raises(NetworkError, match="HTTP error"):
                await client.decode("!AIVDM,1,1,,A,13u@ND0P01PJ=0lMH0nN20pl,0*7D")

    @pytest.mark.asyncio
    async def test_decode_timeout(self, client):
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
        mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))
        mock_client.is_closed = False
        mock_client.aclose = AsyncMock()

        with patch.object(client, "_get_client", return_value=mock_client):
            with pytest.raises(NetworkError, match="Request timeout"):
                await client.decode("!AIVDM,1,1,,A,13u@ND0P01PJ=0lMH0nN20pl,0*7D")

    @pytest.mark.asyncio
    async def test_decode_invalid_message(self, client):
        with pytest.raises(InvalidMessageError):
            await client.decode("INVALID MESSAGE")

    @pytest.mark.asyncio
    async def test_decode_batch_with_delay(self, client, sample_html_response):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = sample_html_response

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.is_closed = False
        mock_client.aclose = AsyncMock()

        messages = [
            "!AIVDM,1,1,,A,13u@ND0P01PJ=0lMH0nN20pl,0*7D",
            "!AIVDO,1,1,,A,703ltL0Q7D@GH0l0e0O,0*2F",
        ]

        with patch.object(client, "_get_client", return_value=mock_client):
            result = await client.decode_batch(messages, delay=0.01)

        assert result.total == 2
        assert result.successful == 2
        assert result.failed == 0

    @pytest.mark.asyncio
    async def test_context_manager(self, sample_html_response):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = sample_html_response

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.is_closed = False
        mock_client.aclose = AsyncMock()

        with patch("aggsoft_ais_decoder.client.httpx.AsyncClient", return_value=mock_client):
            async with AISDecoderClient() as client:
                await client.decode("!AIVDM,1,1,,A,13u@ND0P01PJ=0lMH0nN20pl,0*7D")
                assert client._client is not None


class TestModuleLevelFunctions:
    @pytest.mark.asyncio
    async def test_decode_function(self, sample_html_response):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = sample_html_response

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.get = AsyncMock(return_value=MagicMock(status_code=200))
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.is_closed = False
        mock_client.aclose = AsyncMock()

        with patch("aggsoft_ais_decoder.client.httpx.AsyncClient", return_value=mock_client):
            result = await decode("!AIVDM,1,1,,A,13u@ND0P01PJ=0lMH0nN20pl,0*7D")

        assert result.success is True
        assert result.decoded.mmsi == "226666007"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
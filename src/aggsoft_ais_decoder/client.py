import asyncio
import json
from typing import Optional, Union
import httpx
from .constants import AIS_MESSAGE_PREFIXES, DEFAULT_BASE_URL, DEFAULT_TIMEOUT, DEFAULT_BATCH_DELAY
from .exceptions import InvalidMessageError, NetworkError, ParseError
from .models import AISDecodeResponse, AISShipData, BatchDecodeResponse
from .parser import parse_json_response


class AISDecoderClient:
    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        enable_html_fallback: bool = True,
    ):
        self.base_url = base_url
        self.timeout = timeout
        self.enable_html_fallback = enable_html_fallback
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout, follow_redirects=True)
        return self._client

    async def close(self) -> None:
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    def _validate_message(self, nmea_message: str) -> None:
        if not nmea_message.strip():
            raise InvalidMessageError("Empty message")

        lines = nmea_message.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if not any(line.startswith(prefix) for prefix in AIS_MESSAGE_PREFIXES):
                raise InvalidMessageError(
                    f"Invalid AIS message format. Expected one of {AIS_MESSAGE_PREFIXES}, got: {line[:20]}..."
                )

    async def decode(self, nmea_message: Union[str, list[str]]) -> AISDecodeResponse:
        if isinstance(nmea_message, list):
            nmea_message = '\n'.join(msg.strip() for msg in nmea_message if msg.strip())

        if not nmea_message.strip():
            raise InvalidMessageError("Empty message")

        self._validate_message(nmea_message)
        cleaned = nmea_message.strip()

        try:
            client = await self._get_client()

            form_data = {"src_message": cleaned}

            response = await client.post(self.base_url, data=form_data)

            if response.status_code != 200:
                raise NetworkError(f"HTTP error: {response.status_code}")

            ship_data = parse_json_response(response.text, enable_html_fallback=self.enable_html_fallback)

            raw = ship_data.raw_data or ""
            if not ship_data.mmsi and not ship_data.ship_name and not raw:
                return AISDecodeResponse(
                    success=False,
                    raw_message=cleaned,
                    error="Failed to decode message - no data extracted",
                )

            return AISDecodeResponse(
                success=True,
                source="aggsoft.com",
                raw_message=cleaned,
                decoded=ship_data,
            )

        except InvalidMessageError:
            raise
        except httpx.TimeoutException as e:
            raise NetworkError(f"Request timeout: {e}") from e
        except httpx.HTTPError as e:
            raise NetworkError(f"HTTP error: {e}") from e
        except Exception as e:
            if isinstance(e, (ParseError, InvalidMessageError)):
                raise
            raise ParseError(f"Failed to parse response: {e}") from e

    async def decode_batch(
        self,
        messages: list[str],
        delay: float = DEFAULT_BATCH_DELAY,
    ) -> BatchDecodeResponse:
        results: list[AISDecodeResponse] = []
        successful = 0
        failed = 0

        for msg in messages:
            try:
                result = await self.decode(msg)
                results.append(result)
                if result.success:
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                results.append(
                    AISDecodeResponse(
                        success=False,
                        raw_message=msg,
                        error=str(e),
                    )
                )
                failed += 1

            if delay > 0 and msg != messages[-1]:
                await asyncio.sleep(delay)

        return BatchDecodeResponse(
            total=len(messages),
            successful=successful,
            failed=failed,
            results=results,
        )

    async def __aenter__(self) -> "AISDecoderClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()


async def decode(nmea_message: Union[str, list[str]]) -> AISDecodeResponse:
    async with AISDecoderClient() as client:
        return await client.decode(nmea_message)


async def decode_batch(messages: list[str], delay: float = DEFAULT_BATCH_DELAY) -> BatchDecodeResponse:
    async with AISDecoderClient() as client:
        return await client.decode_batch(messages, delay)
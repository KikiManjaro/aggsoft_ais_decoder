# aggsoft-ais-decoder

[![PyPI version](https://img.shields.io/pypi/v/aggsoft-ais-decoder)](https://pypi.org/project/aggsoft-ais-decoder/)
[![Python versions](https://img.shields.io/pypi/pyversions/aggsoft-ais-decoder)](https://pypi.org/project/aggsoft-ais-decoder/)
[![License](https://img.shields.io/pypi/l/aggsoft-ais-decoder)](https://github.com/KikiManjaro/aggsoft_ais_decoder/blob/main/LICENSE)

**Unofficial** Python wrapper for decoding AIS (Automatic Identification System) messages via [aggsoft.com](https://www.aggsoft.com/).

> **Note**: This library is not affiliated with, endorsed by, or connected to aggsoft.com. The service is provided by a third party.

## Features

- Decode AIS messages types 1-27
- Support for single and multipart NMEA sentences
- Async/await API with httpx
- Configurable HTML fallback parser
- Comprehensive error handling

## Requirements

> **Internet connection required** - This library relies on the aggsoft.com online service to decode AIS messages. The messages are sent to a third-party server for processing.

## User Responsibility

- **Do not spam the service** with excessive requests. Use appropriate delays between requests (see `decode_batch` delay parameter).
- **Verify compliance** with aggsoft.com's terms of service before using this library.
- **You are responsible** for ensuring your usage of the service is appropriate.

## Installation

```bash
pip install aggsoft-ais-decoder
```

Or install from source:

```bash
pip install -e .
```

## Quick Start

```python
from aggsoft_ais_decoder import AISDecoderClient, decode

async def main():
    # Using client
    async with AISDecoderClient() as client:
        result = await client.decode("!AIVDM,1,1,,A,13u@ND0P01PJ=0lMH0nN20pl,0*7D")
        if result.success:
            print(f"Ship: {result.decoded.ship_name}")
            print(f"Position: {result.decoded.position}")

    # Or module-level function
    result = await decode("!AIVDM,1,1,,A,13u@ND0P01PJ=0lMH0nN20pl,0*7D")
```

## Configuration

```python
from aggsoft_ais_decoder import AISDecoderClient

# Enable HTML fallback if JSON parsing fails (default: False)
client = AISDecoderClient(enable_html_fallback=True)

# Customize timeout (default: 30 seconds)
client = AISDecoderClient(timeout=60.0)
```

## API Reference

### AISDecoderClient

```python
client = AISDecoderClient(
    enable_html_fallback=False,  # Use HTML parser if JSON fails
    timeout=30.0                  # Request timeout in seconds
)
```

**Methods:**
- `decode(message: str | list[str])` - Decode single or multipart message
- `decode_batch(messages: list[str], delay=0.5)` - Decode multiple messages

**Returns:** `AISDecodeResponse` with:
- `success: bool`
- `decoded: AISShipData | None`
- `error: str | None`

### Module Functions

```python
from aggsoft_ais_decoder import decode, decode_batch

# Single message
result = await decode("!AIVDM,1,1,,A,13u@ND0P01PJ=0lMH0nN20pl,0*7D")

# Multipart message (list)
result = await decode(["!AIVDM,2,1,,A,13u@ND0P01Pj00000000000000", "!AIVDM,2,2,,A,0000000000000000000000000"])

# Batch
results = await decode_batch(["!AIVDM,1,1,,A,13u@ND0P01PJ=0lMH0nN20pl,0*7D"])
```

## Dependencies

- httpx >= 0.27.0
- pydantic >= 2.0.0
- beautifulsoup4 >= 4.12.0

## Development

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/
```

## Links

- [PyPI Package](https://pypi.org/project/aggsoft-ais-decoder/)
- [GitHub Repository](https://github.com/KikiManjaro/aggsoft_ais_decoder)
- [Issue Tracker](https://github.com/KikiManjaro/aggsoft_ais_decoder/issues)

## Legal

**Copyright (c) 2026 KikiManjaro**

This library is provided under the MIT License.

aggsoft.com is a third-party service. All rights reserved by their respective owners.
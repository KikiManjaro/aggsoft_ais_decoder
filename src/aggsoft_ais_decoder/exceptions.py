class AISDecodeError(Exception):
    pass


class InvalidMessageError(AISDecodeError):
    pass


class NetworkError(AISDecodeError):
    pass


class ParseError(AISDecodeError):
    pass
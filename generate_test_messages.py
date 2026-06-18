"""
Script to generate AIS test messages for all types 1-26 using pyais
and verify against aggsoft.com decoder.
"""

import asyncio

from pyais.encode import encode_dict
from aggsoft_ais_decoder import AISDecoderClient


MMSI_BASE = 226666000


def generate_msg1():
    return encode_dict({
        'type': 1,
        'mmsi': str(MMSI_BASE + 1),
        'lat': 48.8566,
        'lon': 2.3522,
        'status': 0,
        'turn': -128,
        'speed': 10.5,
        'accuracy': False,
        'course': 180.0,
        'heading': 90,
        'second': 30,
        'maneuver': 0,
        'raim': False,
        'radio': 0,
    })[0]


def generate_msg2():
    return encode_dict({
        'type': 2,
        'mmsi': str(MMSI_BASE + 2),
        'lat': 48.8566,
        'lon': 2.3522,
        'status': 0,
        'turn': -128,
        'speed': 10.5,
        'accuracy': False,
        'course': 180.0,
        'heading': 90,
        'second': 30,
    })[0]


def generate_msg3():
    return encode_dict({
        'type': 3,
        'mmsi': str(MMSI_BASE + 3),
        'lat': 48.8566,
        'lon': 2.3522,
        'status': 0,
        'turn': 127,
        'speed': 15.0,
        'accuracy': False,
        'course': 90.0,
        'heading': 45,
        'second': 45,
    })[0]


def generate_msg4():
    return encode_dict({
        'type': 4,
        'mmsi': str(MMSI_BASE + 4),
        'lat': 48.8566,
        'lon': 2.3522,
        'year': 2024,
        'month': 6,
        'day': 18,
        'hour': 12,
        'minute': 30,
        'second': 0,
        'accuracy': True,
        'epfd': 1,
        'raim': False,
        'radio': 0,
    })[0]


def generate_msg5():
    return encode_dict({
        'type': 5,
        'mmsi': str(MMSI_BASE + 5),
        'shipname': 'TEST VESSEL ABC',
        'callsign': 'TST1234',
        'destination': 'PARIS FRANCE',
        'shiptype': 37,
        'to_bow': 10,
        'to_stern': 10,
        'to_port': 3,
        'to_starboard': 3,
        'epfd': 1,
        'draught': 2.0,
        'month': 6,
        'day': 18,
        'hour': 12,
        'minute': 30,
        'dte': 0,
    })[0]


def generate_msg6():
    return encode_dict({
        'type': 6,
        'mmsi': str(MMSI_BASE + 6),
        'dest_mmsi': str(MMSI_BASE + 7),
        'seqno': 0,
        'retransmit': False,
        'dac': 1,
        'fi': 1,
        'data': b'\x01\x02\x03',
    })[0]


def generate_msg7():
    return encode_dict({
        'type': 7,
        'mmsi': str(MMSI_BASE + 7),
        'dest_mmsi': str(MMSI_BASE + 8),
        'seqno': 0,
    })[0]


def generate_msg8():
    return encode_dict({
        'type': 8,
        'mmsi': str(MMSI_BASE + 8),
        'dac': 1,
        'fi': 1,
        'data': b'\x01\x02\x03\x04',
    })[0]


def generate_msg9():
    return encode_dict({
        'type': 9,
        'mmsi': str(MMSI_BASE + 9),
        'lat': 48.8566,
        'lon': 2.3522,
        'alt': 1000,
        'speed': 250,
        'accuracy': False,
        'course': 180.0,
        'second': 30,
        'dte': False,
        'raim': False,
        'assigned': False,
    })[0]


def generate_msg10():
    return encode_dict({
        'type': 10,
        'mmsi': str(MMSI_BASE + 10),
        'dest_mmsi': str(MMSI_BASE + 11),
    })[0]


def generate_msg11():
    return encode_dict({
        'type': 11,
        'mmsi': str(MMSI_BASE + 11),
        'lat': 48.8566,
        'lon': 2.3522,
        'year': 2024,
        'month': 6,
        'day': 18,
        'hour': 12,
        'minute': 30,
        'second': 0,
        'accuracy': True,
        'epfd': 1,
        'raim': False,
    })[0]


def generate_msg12():
    return encode_dict({
        'type': 12,
        'mmsi': str(MMSI_BASE + 12),
        'dest_mmsi': str(MMSI_BASE + 13),
        'seqno': 0,
        'retransmit': False,
        'text': 'SAFETY TEST MESSAGE',
    })[0]


def generate_msg13():
    return encode_dict({
        'type': 13,
        'mmsi': str(MMSI_BASE + 13),
        'dest_mmsi': str(MMSI_BASE + 14),
        'seqno': 0,
    })[0]


def generate_msg14():
    return encode_dict({
        'type': 14,
        'mmsi': str(MMSI_BASE + 14),
        'text': 'SAFETY BROADCAST MESSAGE',
    })[0]


def generate_msg15():
    return encode_dict({
        'type': 15,
        'mmsi': str(MMSI_BASE + 15),
        'dest_mmsi': str(MMSI_BASE + 16),
        'msg_type': 1,
        'slot_offset': 100,
    })[0]


def generate_msg16():
    return encode_dict({
        'type': 16,
        'mmsi': str(MMSI_BASE + 16),
        'dest_mmsi': str(MMSI_BASE + 17),
        'offset': 100,
        'increment': 500,
    })[0]


def generate_msg17():
    return encode_dict({
        'type': 17,
        'mmsi': str(MMSI_BASE + 17),
        'lat': 48.8566,
        'lon': 2.3522,
        'data': b'\x01\x02',
    })[0]


def generate_msg18():
    return encode_dict({
        'type': 18,
        'mmsi': str(MMSI_BASE + 18),
        'lat': 48.8566,
        'lon': 2.3522,
        'speed': 10.5,
        'accuracy': False,
        'course': 180.0,
        'heading': 90,
        'second': 30,
        'raim': False,
        'cs': True,
        'display': False,
        'dsc': False,
        'band': False,
        'msg22': False,
        'assigned': False,
        'radio': 0,
    })[0]


def generate_msg19():
    return encode_dict({
        'type': 19,
        'mmsi': str(MMSI_BASE + 19),
        'lat': 48.8566,
        'lon': 2.3522,
        'speed': 10.5,
        'accuracy': False,
        'course': 180.0,
        'heading': 90,
        'second': 30,
        'raim': False,
        'cs': True,
        'display': False,
        'dsc': False,
        'band': False,
        'msg22': False,
        'assigned': False,
        'vendorid': 'ABC',
        'model': 1,
        'serial': 12345,
        'to_bow': 5,
        'to_stern': 5,
        'to_port': 2,
        'to_starboard': 2,
    })[0]


def generate_msg20():
    return encode_dict({
        'type': 20,
        'mmsi': str(MMSI_BASE + 20),
        'offset': 100,
        'slots': 3,
        'timeout': 2,
        'increment': 750,
    })[0]


def generate_msg21():
    return encode_dict({
        'type': 21,
        'mmsi': str(MMSI_BASE + 21),
        'lat': 48.8566,
        'lon': 2.3522,
        'aid_type': 5,
        'name': 'BUOY MARKER ONE  ',
        'accuracy': False,
        'to_bow': 2,
        'to_stern': 2,
        'to_port': 1,
        'to_starboard': 1,
        'epfd': 1,
        'second': 30,
        'off_position': False,
        'raim': False,
        'virtual_aid': False,
        'assigned': False,
    })[0]


def generate_msg22():
    return encode_dict({
        'type': 22,
        'mmsi': str(MMSI_BASE + 22),
        'channel_a': 2087,
        'channel_b': 2088,
        'txrx': 0,
        'power': False,
        'addressed': False,
        'ne_lon': 2.5,
        'ne_lat': 49.0,
        'sw_lon': 2.0,
        'sw_lat': 48.5,
    })[0]


def generate_msg23():
    return encode_dict({
        'type': 23,
        'mmsi': str(MMSI_BASE + 23),
        'ne_lon': 2.5,
        'ne_lat': 49.0,
        'sw_lon': 2.0,
        'sw_lat': 48.5,
        'station_type': 0,
        'txrx': 0,
        'interval': 60,
        'quiet': 0,
    })[0]


def generate_msg24a():
    return encode_dict({
        'type': 24,
        'mmsi': str(MMSI_BASE + 24),
        'shipname': 'CLASS B VESSEL ABC',
        'partno': 0,
    })[0]


def generate_msg24b():
    return encode_dict({
        'type': 24,
        'mmsi': str(MMSI_BASE + 25),
        'shiptype': 37,
        'vendorid': 'ABC',
        'model': 1,
        'serial': 12345,
        'callsign': 'TST1234',
        'to_bow': 5,
        'to_stern': 5,
        'to_port': 2,
        'to_starboard': 2,
        'partno': 1,
    })[0]


def generate_msg25():
    return encode_dict({
        'type': 25,
        'mmsi': str(MMSI_BASE + 26),
        'data': b'\x01\x02\x03',
        'addressed': False,
        'structured': False,
    })[0]


def generate_msg26():
    return encode_dict({
        'type': 26,
        'mmsi': str(MMSI_BASE + 27),
        'data': b'\x01\x02\x03\x04',
        'addressed': False,
        'structured': False,
    })[0]


def generate_msg27():
    return encode_dict({
        'type': 27,
        'mmsi': str(MMSI_BASE + 28),
        'accuracy': False,
        'raim': False,
        'status': 15,
        'lon': 2.3522,
        'lat': 48.8566,
        'speed': 10,
        'course': 180,
    })[0]


MESSAGE_GENERATORS = {
    1: generate_msg1,
    2: generate_msg2,
    3: generate_msg3,
    4: generate_msg4,
    5: generate_msg5,
    6: generate_msg6,
    7: generate_msg7,
    8: generate_msg8,
    9: generate_msg9,
    10: generate_msg10,
    11: generate_msg11,
    12: generate_msg12,
    13: generate_msg13,
    14: generate_msg14,
    15: generate_msg15,
    16: generate_msg16,
    17: generate_msg17,
    18: generate_msg18,
    19: generate_msg19,
    20: generate_msg20,
    21: generate_msg21,
    22: generate_msg22,
    23: generate_msg23,
    24: generate_msg24a,
    24.1: generate_msg24b,
    25: generate_msg25,
    26: generate_msg26,
    27: generate_msg27,
}


async def test_aggsoft_all_types():
    client = AISDecoderClient()

    results = {}

    for msg_id, generator in MESSAGE_GENERATORS.items():
        try:
            nmea = generator()
            print(f"\n--- Message Type {msg_id} ---")
            print(f"NMEA: {nmea}")

            result = await client.decode(nmea)
            results[msg_id] = result

            if result.success and result.decoded:
                print(f"Decoded MMSI: {result.decoded.mmsi}")
                print(f"Decoded Name: {result.decoded.ship_name}")
                print(f"Decoded Position: {result.decoded.position}")
                print(f"Decoded Speed: {result.decoded.speed_over_ground}")
                print(f"Decoded Course: {result.decoded.course_over_ground}")
            else:
                print(f"Failed: {result.error}")

        except Exception as e:
            print(f"Error for msg type {msg_id}: {e}")
            results[msg_id] = None

        await asyncio.sleep(1.5)

    await client.close()
    return results


if __name__ == "__main__":
    print("Testing all AIS message types against aggsoft.com...")
    asyncio.run(test_aggsoft_all_types())
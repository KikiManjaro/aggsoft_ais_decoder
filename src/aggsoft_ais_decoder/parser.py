import json
import re
from typing import Optional
from bs4 import BeautifulSoup
from .models import AISShipData, Position, Dimensions
from .constants import NAV_STATUS_MAP, VESSEL_TYPES
from .exceptions import ParseError


EPFD_TYPES = {
    "0": "Undefined",
    "1": "GPS",
    "2": "GLONASS",
    "3": "GPS+GLONASS",
    "4": "Loran-C",
    "5": "Chayka",
    "6": "Integrated navigation system",
    "7": "Surveyed",
}

MANEUVER_INDICATORS = {
    "0": "No special maneuver",
    "1": "No special maneuver",
    "2": "Special maneuver (group 1)",
    "3": "Special maneuver (group 2)",
}

POSITION_ACCURACY = {
    "0": "Low",
    "1": "High",
    "high": "High",
    "low": "Low",
}


def parse_response(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    fields: dict[str, str] = {}

    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cells = row.find_all(["td", "th"])
            if len(cells) >= 2:
                label = cells[0].get_text(strip=True).lower()
                value = cells[1].get_text(strip=True)
                if ":" in label:
                    label = label.split(":")[0].strip()
                if label and value:
                    fields[label] = value

    for tag in soup.find_all(["span", "div", "p"]):
        text = tag.get_text()
        if ":" in text:
            parts = text.split(":", 1)
            key = parts[0].strip().lower()
            val = parts[1].strip() if len(parts) > 1 else ""
            if key and val:
                fields[key] = val

    pre_tags = soup.find_all("pre")
    for pre in pre_tags:
        pre_text = pre.get_text()
        for line in pre_text.split("\n"):
            if ":" in line:
                key, _, value = line.partition(":")
                key = key.strip().lower()
                value = value.strip()
                if key and value:
                    fields[key] = value

    return fields


def extract_ship_data(fields: dict) -> AISShipData:
    ship_data = AISShipData()

    for key, value in fields.items():
        key_lower = key.lower()
        value_clean = value.strip() if isinstance(value, str) else value

        if "message type" in key_lower or key_lower == "type":
            try:
                ship_data.msg_type = int(re.sub(r"[^\d]", "", value_clean))
            except (ValueError, AttributeError):
                pass

        elif "repeat indicator" in key_lower:
            try:
                ship_data.repeat_indicator = int(re.sub(r"[^\d]", "", value_clean))
            except (ValueError, AttributeError):
                pass

        elif "mmsi" in key_lower or key_lower in ("source id", "id"):
            ship_data.mmsi = value_clean

        elif ("name" in key_lower and "ship" in key_lower) or key_lower in ("ship name", "shipname", "name") or key_lower == "aid to navigation name":
            ship_data.ship_name = value_clean

        elif "call" in key_lower:
            ship_data.callsign = value_clean

        elif "imo" in key_lower:
            ship_data.imo_number = re.sub(r"[^\d]", "", value_clean) if value_clean else None

        elif key_lower in ("vessel type", "vesseltype") or ("type" in key_lower and "ship" in key_lower):
            ship_data.vessel_type = re.sub(r"[^\d]", "", value_clean) if value_clean else None
            if ship_data.vessel_type and ship_data.vessel_type in VESSEL_TYPES:
                ship_data.vessel_type_description = VESSEL_TYPES[ship_data.vessel_type]

        elif key_lower == "aid type":
            try:
                ship_data.aid_type = int(re.sub(r"[^\d]", "", value_clean))
            except (ValueError, AttributeError):
                pass

        elif "lat" in key_lower and "lon" not in key_lower and "long" not in key_lower:
            try:
                lat_val = float(re.sub(r"[^\d.\-]", "", value_clean))
                if ship_data.position is None:
                    ship_data.position = Position()
                ship_data.position.latitude = lat_val
            except (ValueError, AttributeError):
                pass

        elif "lon" in key_lower or "long" in key_lower:
            try:
                lon_val = float(re.sub(r"[^\d.\-]", "", value_clean))
                if ship_data.position is None:
                    ship_data.position = Position()
                ship_data.position.longitude = lon_val
            except (ValueError, AttributeError):
                pass

        elif "speed" in key_lower or "sog" in key_lower:
            try:
                ship_data.speed_over_ground = float(re.sub(r"[^\d.]", "", value_clean))
            except (ValueError, AttributeError):
                pass

        elif "course" in key_lower or "cog" in key_lower:
            try:
                ship_data.course_over_ground = float(re.sub(r"[^\d.]", "", value_clean))
            except (ValueError, AttributeError):
                pass

        elif "heading" in key_lower or "hdg" in key_lower:
            try:
                ship_data.heading = int(re.sub(r"[^\d]", "", value_clean))
            except (ValueError, AttributeError):
                pass

        elif "status" in key_lower or "nav" in key_lower:
            status_val = re.sub(r"[^\d]", "", value_clean) if value_clean else None
            if status_val and status_val in NAV_STATUS_MAP:
                ship_data.navigation_status = NAV_STATUS_MAP[status_val]
            else:
                ship_data.navigation_status = value_clean

        elif "turn" in key_lower or "rot" in key_lower:
            try:
                ship_data.turn_rate = float(re.sub(r"[^\d.\-]", "", value_clean))
            except (ValueError, AttributeError):
                pass

        elif "accuracy" in key_lower:
            if "high" in value_clean.lower():
                ship_data.position_accuracy = "High"
            else:
                ship_data.position_accuracy = "Low"

        elif "altitude" in key_lower:
            try:
                ship_data.altitude = int(re.sub(r"[^\d]", "", value_clean))
            except (ValueError, AttributeError):
                pass

        elif "timestamp" in key_lower or "time stamp" in key_lower:
            if "year" in key_lower:
                try:
                    ship_data.year = int(re.sub(r"[^\d]", "", value_clean))
                except (ValueError, AttributeError):
                    pass
            elif "month" in key_lower:
                try:
                    ship_data.month = int(re.sub(r"[^\d]", "", value_clean))
                except (ValueError, AttributeError):
                    pass
            elif "day" in key_lower:
                try:
                    ship_data.day = int(re.sub(r"[^\d]", "", value_clean))
                except (ValueError, AttributeError):
                    pass
            elif "hour" in key_lower:
                try:
                    ship_data.hour = int(re.sub(r"[^\d]", "", value_clean))
                except (ValueError, AttributeError):
                    pass
            elif "minute" in key_lower:
                try:
                    ship_data.minute = int(re.sub(r"[^\d]", "", value_clean))
                except (ValueError, AttributeError):
                    pass
            elif "second" in key_lower:
                try:
                    ship_data.second = int(re.sub(r"[^\d]", "", value_clean))
                except (ValueError, AttributeError):
                    pass
            else:
                try:
                    ship_data.timestamp = int(re.sub(r"[^\d]", "", value_clean))
                except (ValueError, AttributeError):
                    pass

        elif "maneuver" in key_lower:
            ship_data.maneuver_indicator = value_clean

        elif "raim" in key_lower:
            ship_data.raim_flag = "yes" in value_clean.lower() or "true" in value_clean.lower()

        elif "dest" in key_lower or "destination" in key_lower:
            ship_data.destination = value_clean

        elif "eta" in key_lower:
            ship_data.eta = value_clean

        elif "draught" in key_lower:
            try:
                ship_data.draught = float(re.sub(r"[^\d.]", "", value_clean))
            except (ValueError, AttributeError):
                pass

        elif "bow" in key_lower and "to" in key_lower or key_lower == "dimension reference for position a":
            if ship_data.dimensions is None:
                ship_data.dimensions = Dimensions()
            try:
                ship_data.dimensions.to_bow = int(re.sub(r"[^\d]", "", value_clean))
            except ValueError:
                pass

        elif "stern" in key_lower and "to" in key_lower or key_lower == "dimension reference for position b":
            if ship_data.dimensions is None:
                ship_data.dimensions = Dimensions()
            try:
                ship_data.dimensions.to_stern = int(re.sub(r"[^\d]", "", value_clean))
            except ValueError:
                pass

        elif ("port" in key_lower and "to" in key_lower) or key_lower == "dimension reference for position c":
            if ship_data.dimensions is None:
                ship_data.dimensions = Dimensions()
            try:
                ship_data.dimensions.to_port = int(re.sub(r"[^\d]", "", value_clean))
            except ValueError:
                pass

        elif "starboard" in key_lower and "to" in key_lower or key_lower == "dimension reference for position d":
            if ship_data.dimensions is None:
                ship_data.dimensions = Dimensions()
            try:
                ship_data.dimensions.to_starboard = int(re.sub(r"[^\d]", "", value_clean))
            except ValueError:
                pass

        elif "epfd" in key_lower or "position fixing" in key_lower:
            epfd_val = re.sub(r"[^\d]", "", value_clean) if value_clean else None
            if epfd_val and epfd_val in EPFD_TYPES:
                ship_data.epfd_type = EPFD_TYPES[epfd_val]
            else:
                ship_data.epfd_type = value_clean

        elif "vendor id" in key_lower or "vendorid" in key_lower:
            ship_data.vendor_id = value_clean

        elif "model" in key_lower:
            try:
                ship_data.model = int(re.sub(r"[^\d]", "", value_clean))
            except (ValueError, AttributeError):
                pass

        elif "serial" in key_lower:
            try:
                ship_data.serial = int(re.sub(r"[^\d]", "", value_clean))
            except (ValueError, AttributeError):
                pass

        elif "part number" in key_lower or "partno" in key_lower:
            try:
                ship_data.part_number = int(re.sub(r"[^\d]", "", value_clean))
            except (ValueError, AttributeError):
                pass

        elif "off position" in key_lower:
            ship_data.off_position = "yes" in value_clean.lower() or "true" in value_clean.lower()

        elif "virtual" in key_lower:
            ship_data.virtual_aton = "yes" in value_clean.lower() or "true" in value_clean.lower()

        elif "comm" in key_lower and "state" in key_lower:
            try:
                ship_data.comm_state = int(re.sub(r"[^\d]", "", value_clean))
            except (ValueError, AttributeError):
                pass

    return ship_data


def parse_aggsoft_response(html: str) -> AISShipData:
    fields = parse_response(html)
    return extract_ship_data(fields)


JSON_FIELD_MAPPING = {
    "source id": "mmsi",
    "message type": "msg_type",
    "packet type": "packet_type",
    "radio channel": "radio_channel",
    "repeat indicator": "repeat_indicator",
    "navigation status": "navigation_status",
    "rate of turn (rot)": "turn_rate",
    "speed over ground (sog)": "speed_over_ground",
    "position accuracy": "position_accuracy",
    "longitude": "longitude",
    "latitude": "latitude",
    "course over ground (cog)": "course_over_ground",
    "true heading (hdg)": "heading",
    "second of utc timestamp": "timestamp",
    "reserved for regional": "reserved_regional",
    "raim flag": "raim_flag",
    "communication state": "comm_state",
    "communication sync state": "comm_sync_state",
    "communication slot timeout": "comm_slot_timeout",
    "communication sub message": "comm_sub_message",
    "communication slot number": "comm_slot_number",
    "imo number": "imo_number",
    "callsign": "callsign",
    "ship name": "ship_name",
    "vessel type": "vessel_type",
    "dimension to bow": "dimension_bow",
    "dimension to stern": "dimension_stern",
    "dimension to port": "dimension_port",
    "dimension to starboard": "dimension_starboard",
    "type of epfd": "epfd_type",
    "eta month": "eta_month",
    "eta day": "eta_day",
    "eta hour": "eta_hour",
    "eta minute": "eta_minute",
    "draught": "draught",
    "destination": "destination",
    "dte": "dte",
    "assigned mode": "assigned_mode",
    "gnss type": "gnss_type",
    "spare": "spare",
    "altitude": "altitude",
    "aid type": "aid_type",
    "off position": "off_position",
    "virtual aton": "virtual_aton",
    "assigned mode flag": "assigned_mode_flag",
    "name": "ship_name",
    "vendor id": "vendor_id",
    "model": "model",
    "serial": "serial",
    "part number": "part_number",
}


def parse_json_response(response_text: str, enable_html_fallback: bool = True) -> AISShipData:
    try:
        data = json.loads(response_text)
    except (json.JSONDecodeError, ValueError):
        if enable_html_fallback:
            return parse_aggsoft_response(response_text)
        from .exceptions import ParseError
        raise ParseError(f"Failed to parse JSON response: {response_text[:200]}")

    aa_data = data.get("aaData", [])
    fields: dict[str, str] = {}

    for row in aa_data:
        if len(row) >= 2:
            key = re.sub(r'<[^>]+>', '', row[0]).lower().strip() if row[0] else ""
            value = row[1].strip() if row[1] else ""
            if key and value:
                fields[key] = value

    ship_data = extract_ship_data(fields)
    ship_data.raw_data = response_text

    return ship_data
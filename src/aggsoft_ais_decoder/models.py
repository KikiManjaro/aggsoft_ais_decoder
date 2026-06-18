from typing import Optional
from pydantic import BaseModel, Field


class Position(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class Dimensions(BaseModel):
    to_bow: Optional[int] = None
    to_stern: Optional[int] = None
    to_port: Optional[int] = None
    to_starboard: Optional[int] = None


class AISShipData(BaseModel):
    mmsi: Optional[str] = None
    ship_name: Optional[str] = None
    callsign: Optional[str] = None
    imo_number: Optional[str] = None
    vessel_type: Optional[str] = None
    vessel_type_description: Optional[str] = None
    dimensions: Optional[Dimensions] = None
    position: Optional[Position] = None
    navigation_status: Optional[str] = None
    speed_over_ground: Optional[float] = Field(None, description="Speed in knots")
    course_over_ground: Optional[float] = Field(None, description="Course in degrees")
    heading: Optional[int] = None
    destination: Optional[str] = None
    eta: Optional[str] = None
    raw_data: Optional[str] = None

    repeat_indicator: Optional[int] = None
    turn_rate: Optional[float] = Field(None, description="Rate of Turn")
    position_accuracy: Optional[str] = None
    altitude: Optional[int] = Field(None, description="Altitude for SAR aircraft")
    timestamp: Optional[int] = Field(None, description="Time stamp (seconds)")
    maneuver_indicator: Optional[str] = None
    raim_flag: Optional[bool] = None
    comm_state: Optional[int] = None

    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    hour: Optional[int] = None
    minute: Optional[int] = None
    second: Optional[int] = None

    epfd_type: Optional[str] = None
    draught: Optional[float] = None

    vendor_id: Optional[str] = None
    model: Optional[int] = None
    serial: Optional[int] = None

    aid_type: Optional[int] = Field(None, description="Aid-to-Navigation type")
    off_position: Optional[bool] = None
    virtual_aton: Optional[bool] = None

    part_number: Optional[int] = None

    msg_type: Optional[int] = None


class AISDecodeRequest(BaseModel):
    message: str = Field(..., description="NMEA AIS message (e.g., !AIVDM,1,1,,A,13u@ND0P01PJ=0lMH0nN20pl,0*7D)")


class AISDecodeResponse(BaseModel):
    success: bool
    source: str = "aggsoft.com"
    raw_message: str
    decoded: Optional[AISShipData] = None
    error: Optional[str] = None


class BatchDecodeResponse(BaseModel):
    total: int
    successful: int
    failed: int
    results: list[AISDecodeResponse]
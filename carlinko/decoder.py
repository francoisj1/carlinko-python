"""
carlinko/decoder.py

Decode CarLinko realtime telemetry packets.

The websocket sends packets similar to:

{
    "action": 6,
    "data": "7E01020304..."
}

where "data" is a hexadecimal string.

This module converts that into useful telemetry.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# ---------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------

@dataclass
class BatteryTelemetry:
    soc: Optional[int] = None
    range_km: Optional[int] = None
    voltage: Optional[float] = None
    current: Optional[float] = None
    power_kw: Optional[float] = None
    temperature: Optional[float] = None
    charging: Optional[bool] = None


@dataclass
class TyreTelemetry:
    fl_pressure: Optional[float] = None
    fr_pressure: Optional[float] = None
    rl_pressure: Optional[float] = None
    rr_pressure: Optional[float] = None

    fl_temperature: Optional[int] = None
    fr_temperature: Optional[int] = None
    rl_temperature: Optional[int] = None
    rr_temperature: Optional[int] = None


@dataclass
class VehicleTelemetry:
    speed: Optional[int] = None
    odometer: Optional[int] = None
    gear: Optional[str] = None
    ready: Optional[bool] = None
    ignition: Optional[bool] = None


@dataclass
class GPSTelemetry:
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    heading: Optional[int] = None
    altitude: Optional[int] = None


@dataclass
class Telemetry:

    battery: BatteryTelemetry
    tyres: TyreTelemetry
    vehicle: VehicleTelemetry
    gps: GPSTelemetry

    raw: bytes


# ---------------------------------------------------------
# Decoder
# ---------------------------------------------------------

class CarLinkoDecoder:

    def decode(self, hex_data: str) -> Telemetry:

        packet = bytes.fromhex(hex_data)

        battery = BatteryTelemetry()
        tyres = TyreTelemetry()
        vehicle = VehicleTelemetry()
        gps = GPSTelemetry()

        #
        # -----------------------------------------------------
        # Known offsets from the original dashboard project
        # -----------------------------------------------------
        #

        #
        # Battery %
        #
        try:
            battery.soc = packet[17]
        except Exception:
            pass

        #
        # Remaining range
        #
        try:
            battery.range_km = (
                (packet[18] << 8)
                | packet[19]
            )
        except Exception:
            pass

        #
        # Tyre pressures
        #
        try:
            tyres.fl_pressure = packet[40] / 10.0
            tyres.fr_pressure = packet[41] / 10.0
            tyres.rl_pressure = packet[42] / 10.0
            tyres.rr_pressure = packet[43] / 10.0
        except Exception:
            pass

        #
        # Tyre temperatures
        #
        try:
            tyres.fl_temperature = packet[44] - 40
            tyres.fr_temperature = packet[45] - 40
            tyres.rl_temperature = packet[46] - 40
            tyres.rr_temperature = packet[47] - 40
        except Exception:
            pass

        #
        # -----------------------------------------------------
        # Unknown fields
        #
        # These will be populated as we reverse engineer
        # additional telemetry packets.
        # -----------------------------------------------------
        #

        return Telemetry(
            battery=battery,
            tyres=tyres,
            vehicle=vehicle,
            gps=gps,
            raw=packet,
        )

    # -----------------------------------------------------

    @staticmethod
    def dump(packet: bytes):

        print("\nPacket Length:", len(packet))

        print("\nOffset  Hex")

        for i, b in enumerate(packet):

            print(
                f"{i:03d}    {b:02X} ({b})"
            )

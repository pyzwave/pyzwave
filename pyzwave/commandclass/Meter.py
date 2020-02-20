from enum import IntEnum

from pyzwave.const.ZW_classcmd import (
    COMMAND_CLASS_METER,
    METER_GET,
    METER_REPORT,
    METER_RESET_V2,
    METER_SUPPORTED_GET_V2,
    METER_SUPPORTED_REPORT_V2,
)
from pyzwave.message import Message
from pyzwave.types import (
    bits_t,
    bytes_t,
    enum_t,
    flag_t,
    float_t,
    reserved_t,
    uint7_t,
    uint8_t,
    uint16_t,
)
from . import ZWaveMessage, ZWaveCommandClass
from .CommandClass import CommandClass


class MeterType(IntEnum):
    """Enum for Meter types"""

    ELECTRIC_METER = 0x01
    GAS_METER = 0x02
    WATER_METER = 0x03
    HEATING_METER = 0x04
    COOLING_METER = 0x05


MeterType_t = enum_t(MeterType, bits_t(5))  # pylint: disable=invalid-name


class ElectricMeterScale(IntEnum):
    """Enum for the scales for electric meter"""

    KWH = 0x00
    KVAH = 0x01
    W = 0x02
    PULSE_COUNT = 0x03
    V = 0x04
    A = 0x05
    POWER_FACTOR = 0x06
    MST = 0x07


class RateType(IntEnum):
    """Enum for rate types"""

    UNSPECIFIED = 0x00
    IMPORT = 0x01
    EXPORT = 0x02
    BOTH_IMPORT_AND_EXPORT = 0x03


RateType_t = enum_t(RateType, bits_t(2))  # pylint: disable=invalid-name


@ZWaveMessage(COMMAND_CLASS_METER, METER_GET)
class Get(Message):
    """Command Class message COMMAND_CLASS_METER METER_GET"""

    NAME = "GET"

    attributes = (
        ("rateType", RateType_t),
        ("scale", bits_t(3)),
        ("-", reserved_t(3)),
        ("scale2", uint8_t),
    )


@ZWaveMessage(COMMAND_CLASS_METER, METER_REPORT)
class Report(Message):
    """Command Class message COMMAND_CLASS_METER METER_REPORT"""

    NAME = "REPORT"

    attributes = (
        ("scale2", flag_t),
        ("rateType", RateType_t),
        ("meterType", MeterType_t),
        ("meterValue", float_t),
        ("deltaTime", uint16_t),
    )

    @property
    def scale(self) -> int:
        """Return the scale for this value"""
        scale = self.meterValue.scale
        if self.scale2:
            scale |= 0x04
        if self.meterType == MeterType.ELECTRIC_METER:
            return ElectricMeterScale(scale)
        return scale


@ZWaveMessage(COMMAND_CLASS_METER, METER_RESET_V2)
class Reset(Message):
    """Command Class message COMMAND_CLASS_METER METER_RESET"""

    NAME = "RESET"


@ZWaveMessage(COMMAND_CLASS_METER, METER_SUPPORTED_GET_V2)
class SupportedGet(Message):
    """Command Class message COMMAND_CLASS_METER METER_SUPPORTED_GET"""

    NAME = "SUPPORTED_GET"


@ZWaveMessage(COMMAND_CLASS_METER, METER_SUPPORTED_REPORT_V2)
class SupportedReport(Message):
    """Command Class message COMMAND_CLASS_METER METER_SUPPORTED_REPORT"""

    NAME = "SUPPORTED_REPORT"

    attributes = (
        ("meterReset", flag_t),
        ("rateType", RateType_t),
        ("meterType", MeterType_t),
        ("moreScaleTypes", flag_t),
        ("scaleSupported", uint7_t),
        ("nbrScaleSupportedBytesToFollow", uint8_t),
        ("scaleSupportedByteN", bytes_t),
    )


# pylint: disable=attribute-defined-outside-init
@ZWaveCommandClass(COMMAND_CLASS_METER)
class Meter(CommandClass):
    """Command Class METER"""

    NAME = "METER"

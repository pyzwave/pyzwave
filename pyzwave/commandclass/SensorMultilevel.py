from enum import IntEnum

from pyzwave.const.ZW_classcmd import (
    COMMAND_CLASS_SENSOR_MULTILEVEL,
    SENSOR_MULTILEVEL_GET,
    SENSOR_MULTILEVEL_REPORT,
    SENSOR_MULTILEVEL_SUPPORTED_GET_SCALE_V5,
    SENSOR_MULTILEVEL_SUPPORTED_GET_SENSOR_V5,
    SENSOR_MULTILEVEL_SUPPORTED_SCALE_REPORT_V5,
    SENSOR_MULTILEVEL_SUPPORTED_SENSOR_REPORT_V5,
)
from pyzwave.message import Message

from pyzwave.types import (
    BitStreamReader,
    bits_t,
    enum_t,
    float_t,
    reserved_t,
    uint8_t,
)
from . import ZWaveMessage, ZWaveMessageHandler, ZWaveCommandClass
from .CommandClass import CommandClass, VarDictAttribute


class SensorType(IntEnum):
    """Enum for sensor types"""

    TEMPERATURE = 1
    GENERAL_PURPOSE = 0x02
    LUMINANCE = 0x03
    POWER = 0x04
    HUMIDITY = 0x05
    VELOCITY = 0x06
    BAROMETRIC_PRESSURE = 0x09
    DEW_POINT = 0x0B
    RAIN_RATE = 0x0C
    WEIGHT = 0x0E
    VOLTAGE = 0x0F
    CO2 = 0x11
    VOLUME = 0x13  # tank capacity
    UV = 0x1B
    LOUDNESS = 0x1E
    MOISTURE = 0x1F
    PM25 = 0x23
    CO = 0x28


SensorType_t = enum_t(SensorType, uint8_t)  # pylint: disable=invalid-name


class SensorSupported(set):
    """Deserializer for sensor types returned in SUPPORTED_SENSOR_REPORT"""

    @classmethod
    def deserialize(cls, stream: BitStreamReader):
        """Deserialize types from stream"""
        supported = cls()
        value = int.from_bytes(stream.remaining(), byteorder="big", signed=False)
        i = 1
        while value > 0:
            if value & 1 == 1:
                supported.add(SensorType(i))
            value >>= 1
            i += 1
        return supported


@ZWaveMessage(COMMAND_CLASS_SENSOR_MULTILEVEL, SENSOR_MULTILEVEL_GET)
class Get(Message):
    """Command Class message COMMAND_CLASS_SENSOR_MULTILEVEL SENSOR_MULTILEVEL_GET"""

    NAME = "GET"

    attributes = (
        ("sensorType", SensorType_t),
        ("-", reserved_t(3)),
        ("scale", bits_t(2)),
        ("-", reserved_t(3)),
    )


@ZWaveMessage(COMMAND_CLASS_SENSOR_MULTILEVEL, SENSOR_MULTILEVEL_REPORT)
class Report(Message):
    """Command Class message COMMAND_CLASS_SENSOR_MULTILEVEL SENSOR_MULTILEVEL_REPORT"""

    NAME = "REPORT"

    attributes = (
        ("sensorType", SensorType_t),
        ("sensorValue", float_t),
    )


@ZWaveMessage(COMMAND_CLASS_SENSOR_MULTILEVEL, SENSOR_MULTILEVEL_SUPPORTED_GET_SCALE_V5)
class SupportedGetScale(Message):
    """
    Command Class message
    COMMAND_CLASS_SENSOR_MULTILEVEL
    SENSOR_MULTILEVEL_SUPPORTED_GET_SCALE
    """

    NAME = "SUPPORTED_GET_SCALE"
    attributes = (("sensorType", SensorType_t),)


@ZWaveMessage(
    COMMAND_CLASS_SENSOR_MULTILEVEL, SENSOR_MULTILEVEL_SUPPORTED_GET_SENSOR_V5
)
class SupportedGetSensor(Message):
    """
    Command Class message
    COMMAND_CLASS_SENSOR_MULTILEVEL
    SENSOR_MULTILEVEL_SUPPORTED_GET_SENSOR_V5
    """

    NAME = "SUPPORTED_GET_SENSOR"


@ZWaveMessage(
    COMMAND_CLASS_SENSOR_MULTILEVEL, SENSOR_MULTILEVEL_SUPPORTED_SCALE_REPORT_V5
)
class SupportedScaleReport(Message):
    """
    Command Class message
    COMMAND_CLASS_SENSOR_MULTILEVEL
    SENSOR_MULTILEVEL_SUPPORTED_SCALE_REPORT
    """

    NAME = "SUPPORTED_SCALE_REPORT"
    attributes = (
        ("sensorType", SensorType_t),
        ("-", reserved_t(4)),
        ("scaleBitMask", bits_t(4)),
    )


@ZWaveMessage(
    COMMAND_CLASS_SENSOR_MULTILEVEL, SENSOR_MULTILEVEL_SUPPORTED_SENSOR_REPORT_V5
)
class SupportedSensorReport(Message):
    """
    Command Class message
    COMMAND_CLASS_SENSOR_MULTILEVEL
    SENSOR_MULTILEVEL_SUPPORTED_SENSOR_REPORT_V5
    """

    NAME = "SUPPORTED_SENSOR_REPORT"
    attributes = (("bitMask", SensorSupported),)


# pylint: disable=attribute-defined-outside-init
@ZWaveCommandClass(COMMAND_CLASS_SENSOR_MULTILEVEL)
class SensorMultilevel(CommandClass):
    """Command Class SENSOR_MULTILEVEL"""

    NAME = "SENSOR_MULTILEVEL"
    attributes = (("supportedTypes", VarDictAttribute(int, uint8_t)),)

    @ZWaveMessageHandler(Report)
    async def __report__(self, report: Report, _flags):
        # Match report against supported types and filter out if we get any non supported
        if self.version < 5:
            # We do not know whats supported
            return False
        supportedScales = self.supportedTypes.get(report.sensorType)
        if not supportedScales:
            # Type is not supported, suppress further processing
            return True
        scaleMask = 1 << report.sensorValue.scale
        if supportedScales & scaleMask == 0:
            # Scale is not supported, suppress message
            return True

    async def interview(self):
        if self.version < 5:
            # Does not support report whats supported
            return
        report: Message = await self.sendAndReceive(
            SupportedGetSensor(), SupportedSensorReport
        )
        for sensor in report.bitMask:
            scaleReport = await self.sendAndReceive(
                SupportedGetScale(sensorType=sensor), SupportedScaleReport
            )
            self.supportedTypes[int(sensor)] = scaleReport.scaleBitMask

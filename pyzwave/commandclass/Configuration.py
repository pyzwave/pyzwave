from enum import IntEnum
import logging

from pyzwave.const.ZW_classcmd import (
    COMMAND_CLASS_CONFIGURATION,
    CONFIGURATION_BULK_GET_V2,
    CONFIGURATION_BULK_REPORT_V2,
    CONFIGURATION_GET,
    CONFIGURATION_REPORT,
    CONFIGURATION_SET,
)
from pyzwave.message import Message
from pyzwave.types import (
    BitStreamReader,
    BitStreamWriter,
    bytes_t,
    enum_t,
    flag_t,
    reserved_t,
    uint3_t,
    uint8_t,
    uint16_t,
)
from . import ZWaveCommandClass, ZWaveMessage, ZWaveMessageHandler
from .CommandClass import CommandClass, DictAttribute, VarDictAttribute

_LOGGER = logging.getLogger(__name__)


class Size(IntEnum):
    """Size enum for configurations"""

    SIZE_8_BIT = 1
    SIZE_16_BIT = 2
    SIZE_32_BIT = 4


Size_t = enum_t(Size, uint3_t)  # pylint: disable=invalid-name


@ZWaveMessage(COMMAND_CLASS_CONFIGURATION, CONFIGURATION_BULK_GET_V2)
class BulkGet(Message):
    """Command Class message COMMAND_CLASS_CONFIGURATION CONFIGURATION_BULK_GET_V2"""

    NAME = "BULK_GET"
    attributes = (("parameterOffset", uint16_t), ("numberOfParameters", uint8_t))


@ZWaveMessage(COMMAND_CLASS_CONFIGURATION, CONFIGURATION_BULK_REPORT_V2)
class BulkReport(Message):
    """Command Class message COMMAND_CLASS_CONFIGURATION CONFIGURATION_BULK_REPORT_V2"""

    NAME = "BULK_REPORT"
    attributes = (
        ("parameterOffset", uint16_t),
        ("numberOfParameters", uint8_t),
        ("reportsToFollow", uint8_t),
        ("default", flag_t),
        ("handshake", flag_t),
        ("-", reserved_t(3)),
        ("size", Size_t),
        ("parameter", bytes_t),
    )


@ZWaveMessage(COMMAND_CLASS_CONFIGURATION, CONFIGURATION_GET)
class Get(Message):
    """Command Class message COMMAND_CLASS_CONFIGURATION CONFIGURATION_GET"""

    NAME = "GET"
    attributes = (("parameterNumber", uint8_t),)


@ZWaveMessage(COMMAND_CLASS_CONFIGURATION, CONFIGURATION_REPORT)
class Report(Message):
    """Command Class message COMMAND_CLASS_CONFIGURATION CONFIGURATION_REPORT"""

    NAME = "REPORT"

    attributes = (
        ("parameterNumber", uint8_t),
        ("-", reserved_t(5)),
        ("size", Size_t),
        ("value", int),
    )

    def parse_value(self, stream: BitStreamReader):  # pylint: disable=invalid-name
        """Decode the value from the report"""
        return int.from_bytes(stream.value(self.size), "big", signed=False)


@ZWaveMessage(COMMAND_CLASS_CONFIGURATION, CONFIGURATION_SET)
class Set(Message):
    """Command Class message COMMAND_CLASS_CONFIGURATION CONFIGURATION_SET"""

    NAME = "SET"

    attributes = (
        ("parameterNumber", uint8_t),
        ("default", flag_t),
        ("-", reserved_t(4)),
        ("size", Size_t),
        ("value", int),
    )

    def compose_value(self, stream: BitStreamWriter):  # pylint: disable=invalid-name
        """Write the value to the bitstream. The value is variable size"""
        stream.addBytes(self.value, self.size, False)


class ConfigurationValue(DictAttribute):
    """Helper class for holding one configuration value"""

    attributes = (("value", int), ("size", int))


# pylint: disable=attribute-defined-outside-init
@ZWaveCommandClass(COMMAND_CLASS_CONFIGURATION)
class Configuration(CommandClass):
    """Command Class COMMAND_CLASS_CONFIGURATION"""

    NAME = "CONFIGURATION"
    attributes = (("parameters", VarDictAttribute(int, ConfigurationValue)),)

    @ZWaveMessageHandler(Report)
    async def __report__(self, report: Report, _flags):
        number = int(report.parameterNumber)
        parameter = self.parameters.setdefault(number, ConfigurationValue())
        parameter.value = report.value
        parameter.size = int(report.size)
        self.speak("commandClassUpdated")
        return True

    async def get(self, number: int, cached: bool = True) -> int:
        """Request configuration value from node. Return the cached value if it is already known."""
        if cached and number in self.parameters:
            return self.parameters[number].value
        report: Report = await self.sendAndReceive(Get(parameterNumber=number), Report)
        return report.value

    async def set(self, parameterNumber: int, size: Size, value: int) -> bool:
        """Set a configuration value in the node"""
        return await self.send(
            Set(parameterNumber=parameterNumber, default=False, size=size, value=value,)
        )

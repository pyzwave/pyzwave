from enum import IntEnum
import logging

from pyzwave.const.ZW_classcmd import (
    COMMAND_CLASS_CONFIGURATION,
    CONFIGURATION_GET,
    CONFIGURATION_REPORT,
    CONFIGURATION_SET,
)
from pyzwave.message import Message
from pyzwave.types import (
    BitStreamWriter,
    enum_t,
    flag_t,
    reserved_t,
    uint3_t,
    uint8_t,
)
from . import ZWaveCommandClass, ZWaveMessage
from .CommandClass import CommandClass

_LOGGER = logging.getLogger(__name__)


class Size(IntEnum):
    """Size enum for configurations"""

    SIZE_8_BIT = 1
    SIZE_16_BIT = 2
    SIZE_32_BIT = 4


Size_t = enum_t(Size, uint3_t)  # pylint: disable=invalid-name


@ZWaveMessage(COMMAND_CLASS_CONFIGURATION, CONFIGURATION_GET)
class Get(Message):
    """Command Class message COMMAND_CLASS_CONFIGURATION CONFIGURATION_GET"""

    NAME = "GET"
    attributes = ("parameterNumber", uint8_t)


@ZWaveMessage(COMMAND_CLASS_CONFIGURATION, CONFIGURATION_REPORT)
class Report(Message):
    """Command Class message COMMAND_CLASS_CONFIGURATION CONFIGURATION_REPORT"""

    NAME = "REPORT"

    # attributes = (("batteryLevel", uint8_t),)


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


# pylint: disable=attribute-defined-outside-init
@ZWaveCommandClass(COMMAND_CLASS_CONFIGURATION)
class Configuration(CommandClass):
    """Command Class COMMAND_CLASS_CONFIGURATION"""

    NAME = "CONFIGURATION"

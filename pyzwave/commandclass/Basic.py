from pyzwave.const.ZW_classcmd import (
    COMMAND_CLASS_BASIC,
    BASIC_GET,
    BASIC_REPORT,
    BASIC_SET,
)
from pyzwave.message import Message
from pyzwave.types import uint8_t
from . import ZWaveMessage, registerCmdClass

registerCmdClass(COMMAND_CLASS_BASIC, "BASIC")


@ZWaveMessage(COMMAND_CLASS_BASIC, BASIC_GET)
class Get(Message):
    """Command Class message COMMAND_CLASS_BASIC BASIC_GET"""

    NAME = "GET"


@ZWaveMessage(COMMAND_CLASS_BASIC, BASIC_REPORT)
class Report(Message):
    """Command Class message COMMAND_CLASS_BASIC BASIC_REPORT"""

    NAME = "REPORT"

    attributes = (("value", uint8_t),)


@ZWaveMessage(COMMAND_CLASS_BASIC, BASIC_SET)
class Set(Message):
    """Command Class message COMMAND_CLASS_BASIC BASIC_SET"""

    NAME = "SET"

    attributes = (("value", uint8_t),)

from pyzwave.const.ZW_classcmd import (
    COMMAND_CLASS_SWITCH_BINARY,
    SWITCH_BINARY_GET,
    SWITCH_BINARY_REPORT,
    SWITCH_BINARY_SET,
)
from pyzwave.message import Message
from pyzwave.types import uint8_t
from . import ZWaveMessage, registerCmdClass

registerCmdClass(COMMAND_CLASS_SWITCH_BINARY, "SWITCH_BINARY")


@ZWaveMessage(COMMAND_CLASS_SWITCH_BINARY, SWITCH_BINARY_GET)
class Get(Message):
    """Command Class message COMMAND_CLASS_SWITCH_BINARY SWITCH_BINARY_GET"""

    NAME = "GET"


@ZWaveMessage(COMMAND_CLASS_SWITCH_BINARY, SWITCH_BINARY_REPORT)
class Report(Message):
    """Command Class message COMMAND_CLASS_SWITCH_BINARY SWITCH_BINARY_REPORT"""

    NAME = "REPORT"

    attributes = (("value", uint8_t),)


@ZWaveMessage(COMMAND_CLASS_SWITCH_BINARY, SWITCH_BINARY_SET)
class Set(Message):
    """Command Class message COMMAND_CLASS_SWITCH_BINARY SWITCH_BINARY_SET"""

    NAME = "SET"

    attributes = (("value", uint8_t),)

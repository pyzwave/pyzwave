import struct

from pyzwave.const.ZW_classcmd import (
    COMMAND_CLASS_BASIC,
    BASIC_GET,
    BASIC_REPORT,
)
from pyzwave.message import Message
from . import ZWaveMessage, registerCmdClass

registerCmdClass(COMMAND_CLASS_BASIC, "BASIC")


@ZWaveMessage(COMMAND_CLASS_BASIC, BASIC_GET)
class Get(Message):
    NAME = "GET"


@ZWaveMessage(COMMAND_CLASS_BASIC, BASIC_REPORT)
class Report(Message):
    NAME = "REPORT"

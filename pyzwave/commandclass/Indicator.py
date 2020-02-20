from pyzwave.const.ZW_classcmd import (
    COMMAND_CLASS_INDICATOR,
    INDICATOR_GET,
    INDICATOR_REPORT,
    INDICATOR_SET,
)
from pyzwave.message import Message
from pyzwave.types import uint8_t
from . import ZWaveCommandClass, ZWaveMessage
from .CommandClass import CommandClass


@ZWaveMessage(COMMAND_CLASS_INDICATOR, INDICATOR_GET)
class Get(Message):
    """Command Class message COMMAND_CLASS_INDICATOR INDICATOR_GET"""

    NAME = "GET"


@ZWaveMessage(COMMAND_CLASS_INDICATOR, INDICATOR_REPORT)
class Report(Message):
    """Command Class message COMMAND_CLASS_INDICATOR INDICATOR_REPORT"""

    NAME = "REPORT"

    attributes = (("value", uint8_t),)


@ZWaveMessage(COMMAND_CLASS_INDICATOR, INDICATOR_SET)
class Set(Message):
    """Command Class message COMMAND_CLASS_INDICATOR INDICATOR_SET"""

    NAME = "SET"

    attributes = (("value", uint8_t),)


# pylint: disable=attribute-defined-outside-init
@ZWaveCommandClass(COMMAND_CLASS_INDICATOR)
class Basic(CommandClass):
    """Command Class COMMAND_CLASS_INDICATOR"""

    NAME = "INDICATOR"

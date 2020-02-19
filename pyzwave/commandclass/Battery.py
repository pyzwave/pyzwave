from pyzwave.const.ZW_classcmd import (
    COMMAND_CLASS_BATTERY,
    BATTERY_GET,
    BATTERY_REPORT,
)
from pyzwave.message import Message
from pyzwave.types import uint8_t
from . import ZWaveCommandClass, ZWaveMessage
from .CommandClass import CommandClass


@ZWaveMessage(COMMAND_CLASS_BATTERY, BATTERY_GET)
class Get(Message):
    """Command Class message COMMAND_CLASS_BATTERY BATTERY_GET"""

    NAME = "GET"


@ZWaveMessage(COMMAND_CLASS_BATTERY, BATTERY_REPORT)
class Report(Message):
    """Command Class message COMMAND_CLASS_BATTERY BATTERY_REPORT"""

    NAME = "REPORT"

    attributes = (("batteryLevel", uint8_t),)


# pylint: disable=attribute-defined-outside-init
@ZWaveCommandClass(COMMAND_CLASS_BATTERY)
class Basic(CommandClass):
    """Command Class COMMAND_CLASS_BATTERY"""

    NAME = "BATTERY"

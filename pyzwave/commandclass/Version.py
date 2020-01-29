from pyzwave.const.ZW_classcmd import (
    COMMAND_CLASS_VERSION,
    VERSION_COMMAND_CLASS_GET,
    VERSION_COMMAND_CLASS_REPORT,
)

from pyzwave.message import Message
from pyzwave.types import uint8_t
from . import CommandClass, ZWaveMessage, ZWaveCommandClass


@ZWaveCommandClass(COMMAND_CLASS_VERSION)
class Version(CommandClass):
    """Command Class COMMAND_CLASS_VERSION"""

    NAME = "COMMAND_CLASS_VERSION"


@ZWaveMessage(COMMAND_CLASS_VERSION, VERSION_COMMAND_CLASS_GET)
class VersionCommandClassGet(Message):
    """Command Class message COMMAND_CLASS_VERSION VERSION_COMMAND_CLASS_GET"""

    NAME = "VERSION_COMMAND_CLASS_GET"
    attributes = (("requestedCommandClass", uint8_t),)


@ZWaveMessage(COMMAND_CLASS_VERSION, VERSION_COMMAND_CLASS_REPORT)
class VersionCommandClassReport(Message):
    """Command Class message COMMAND_CLASS_VERSION VERSION_COMMAND_CLASS_REPORT"""

    NAME = "VERSION_COMMAND_CLASS_REPORT"

    attributes = (
        ("requestedCommandClass", uint8_t),
        ("commandClassVersion", uint8_t),
    )

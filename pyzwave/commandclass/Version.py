from pyzwave.const.ZW_classcmd import (
    COMMAND_CLASS_VERSION,
    VERSION_COMMAND_CLASS_GET,
    VERSION_COMMAND_CLASS_REPORT,
    VERSION_GET,
    VERSION_REPORT,
)

from pyzwave.message import Message
from pyzwave.types import uint8_t
from . import ZWaveMessage, ZWaveCommandClass
from .CommandClass import CommandClass

# pylint: disable=attribute-defined-outside-init
@ZWaveCommandClass(COMMAND_CLASS_VERSION)
class Version(CommandClass):
    """Command Class COMMAND_CLASS_VERSION"""

    NAME = "VERSION"
    attributes = (
        ("zwaveLibraryType", uint8_t),
        ("zwaveProtocolVersion", uint8_t),
        ("zwaveProtocolSubVersion", uint8_t),
        ("applicationVersion", uint8_t),
        ("applicationSubVersion", uint8_t),
    )

    async def interview(self):
        report = await self.sendAndReceive(VersionGet(), VersionReport)
        self.zwaveLibraryType = report.zwaveLibraryType
        self.zwaveProtocolVersion = report.zwaveProtocolVersion
        self.zwaveProtocolSubVersion = report.zwaveProtocolSubVersion
        self.applicationVersion = report.applicationVersion
        self.applicationSubVersion = report.applicationSubVersion


@ZWaveMessage(COMMAND_CLASS_VERSION, VERSION_GET)
class VersionGet(Message):
    """Command Class message COMMAND_CLASS_VERSION VERSION_GET"""

    NAME = "VERSION_GET"


@ZWaveMessage(COMMAND_CLASS_VERSION, VERSION_REPORT)
class VersionReport(Message):
    """Command Class message COMMAND_CLASS_VERSION VERSION_REPORT"""

    NAME = "VERSION_REPORT"

    attributes = (
        ("zwaveLibraryType", uint8_t),
        ("zwaveProtocolVersion", uint8_t),
        ("zwaveProtocolSubVersion", uint8_t),
        ("applicationVersion", uint8_t),
        ("applicationSubVersion", uint8_t),
    )


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

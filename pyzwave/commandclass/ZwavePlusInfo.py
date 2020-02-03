from pyzwave.const.ZW_classcmd import (
    COMMAND_CLASS_ZWAVEPLUS_INFO,
    ZWAVEPLUS_INFO_GET,
    ZWAVEPLUS_INFO_REPORT,
)
from pyzwave.message import Message
from pyzwave.types import uint16_t, uint8_t
from . import ZWaveMessage, ZWaveCommandClass
from .CommandClass import CommandClass

# pylint: disable=attribute-defined-outside-init
@ZWaveCommandClass(COMMAND_CLASS_ZWAVEPLUS_INFO)
class ZwavePlusInfo(CommandClass):
    """Command Class COMMAND_CLASS_ZWAVEPLUS_INFO"""

    NAME = "ZWAVEPLUS_INFO"
    attributes = (
        ("zwavePlusVersion", uint8_t),
        ("roleType", uint8_t),
        ("nodeType", uint8_t),
        ("installerIconType", uint16_t),
        ("userIconType", uint16_t),
    )

    async def interview(self):
        report = await self.sendAndReceive(Get(), Report)
        self.zwavePlusVersion = report.zwavePlusVersion
        self.roleType = report.roleType
        self.nodeType = report.nodeType
        self.installerIconType = report.installerIconType
        self.userIconType = report.userIconType


@ZWaveMessage(COMMAND_CLASS_ZWAVEPLUS_INFO, ZWAVEPLUS_INFO_GET)
class Get(Message):
    """Command Class message COMMAND_CLASS_ZWAVEPLUS_INFO ZWAVEPLUS_INFO_GET"""

    NAME = "GET"


@ZWaveMessage(COMMAND_CLASS_ZWAVEPLUS_INFO, ZWAVEPLUS_INFO_REPORT)
class Report(Message):
    """Command Class message COMMAND_CLASS_ZWAVEPLUS_INFO ZWAVEPLUS_INFO_REPORT"""

    NAME = "REPORT"

    attributes = (
        ("zwavePlusVersion", uint8_t),
        ("roleType", uint8_t),
        ("nodeType", uint8_t),
        ("installerIconType", uint16_t),
        ("userIconType", uint16_t),
    )

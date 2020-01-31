from pyzwave.const.ZW_classcmd import (
    COMMAND_CLASS_MANUFACTURER_SPECIFIC,
    MANUFACTURER_SPECIFIC_GET,
    MANUFACTURER_SPECIFIC_REPORT,
)
from pyzwave.message import Message
from pyzwave.types import uint16_t
from . import ZWaveMessage, ZWaveCommandClass
from .CommandClass import CommandClass

# pylint: disable=attribute-defined-outside-init
@ZWaveCommandClass(COMMAND_CLASS_MANUFACTURER_SPECIFIC)
class ManufacturerSpecific(CommandClass):
    """Command Class MANUFACTURER_SPECIFIC"""

    NAME = "MANUFACTURER_SPECIFIC"
    attributes = (
        ("manufacturerID", uint16_t),
        ("productTypeID", uint16_t),
        ("productID", uint16_t),
    )

    async def interview(self):
        report = await self.sendAndReceive(Get(), Report)
        self.manufacturerID = report.manufacturerID
        self.productTypeID = report.productTypeID
        self.productID = report.productID


@ZWaveMessage(COMMAND_CLASS_MANUFACTURER_SPECIFIC, MANUFACTURER_SPECIFIC_GET)
class Get(Message):
    """Command Class message COMMAND_CLASS_MANUFACTURER_SPECIFIC MANUFACTURER_SPECIFIC_GET"""

    NAME = "GET"


@ZWaveMessage(COMMAND_CLASS_MANUFACTURER_SPECIFIC, MANUFACTURER_SPECIFIC_REPORT)
class Report(Message):
    """Command Class message COMMAND_CLASS_MANUFACTURER_SPECIFIC MANUFACTURER_SPECIFIC_REPORT"""

    NAME = "REPORT"

    attributes = (
        ("manufacturerID", uint16_t),
        ("productTypeID", uint16_t),
        ("productID", uint16_t),
    )

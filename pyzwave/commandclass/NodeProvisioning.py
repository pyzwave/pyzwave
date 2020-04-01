from enum import IntEnum
from pyzwave.message import Message
from pyzwave.types import BitStreamReader, bytes_t, dsk_t, reserved_t, uint5_t, uint8_t
from . import ZWaveMessage, registerCmdClass
from .CommandClass import VarDictAttribute


COMMAND_CLASS_NODE_PROVISIONING = 0x78
COMMAND_NODE_PROVISIONING_SET = 0x01
COMMAND_NODE_PROVISIONING_LIST_ITERATION_GET = 0x03
COMMAND_NODE_PROVISIONING_LIST_ITERATION_REPORT = 0x04

registerCmdClass(COMMAND_CLASS_NODE_PROVISIONING, "NODE_PROVISIONING")


class MetadataExtensionType(IntEnum):
    """Metadata extension type enum"""

    PRODUCT_TYPE = 0x00
    PRODUCT_ID = 0x01
    MAX_INCLUSION_REQUEST_INTERVAL = 0x02
    UUID16 = 0x03
    NAME = 0x32
    LOCATION = 0x33
    SMART_START_INCLUSION_SETTING = 0x34
    ADVANCED_JOINING = 0x35
    BOOTSTRAPPING_MODE = 0x36
    NETWORK_STATUS = 0x37


class MetadataExtension(VarDictAttribute(MetadataExtensionType, bytes)):
    """Metadata extension type"""

    @classmethod
    def deserialize(cls, stream: BitStreamReader):
        """Deserialize metadata extension"""
        retval = {}
        while stream.bytesLeft():
            metadataType = stream.bits(7)
            _critical = stream.bit()
            length = stream.byte()
            retval[metadataType] = stream.value(length)
        return retval


@ZWaveMessage(COMMAND_CLASS_NODE_PROVISIONING, COMMAND_NODE_PROVISIONING_SET)
class Set(Message):
    """Command Class message COMMAND_CLASS_NODE_PROVISIONING NODE_PROVISIONING_SET"""

    NAME = "NODE_PROVISIONING_SET"

    attributes = (("seqNo", uint8_t), ("dsk", dsk_t), ("metaDataExtension", bytes_t))


@ZWaveMessage(
    COMMAND_CLASS_NODE_PROVISIONING, COMMAND_NODE_PROVISIONING_LIST_ITERATION_GET
)
class ListIterationGet(Message):
    """
    Command Class message
    COMMAND_CLASS_NODE_PROVISIONING
    COMMAND_NODE_PROVISIONING_LIST_ITERATION_GET
    """

    NAME = "LIST_ITERATION_GET"

    attributes = (("seqNo", uint8_t), ("remainingCounter", uint8_t))


@ZWaveMessage(
    COMMAND_CLASS_NODE_PROVISIONING, COMMAND_NODE_PROVISIONING_LIST_ITERATION_REPORT
)
class ListIterationReport(Message):
    """
    Command Class message
    COMMAND_CLASS_NODE_PROVISIONING
    COMMAND_NODE_PROVISIONING_LIST_ITERATION_REPORT
    """

    NAME = "LIST_ITERATION_REPORT"

    attributes = (
        ("seqNo", uint8_t),
        ("remainingCount", uint8_t),
        ("-", reserved_t(3)),
        ("dskLengthN", uint5_t),
        ("dsk", dsk_t),
        ("metaDataExtension", MetadataExtension),
    )

    def parse_dsk(self, stream: BitStreamReader):  # pylint: disable=invalid-name
        """Parse attribute dsk"""
        return dsk_t.deserializeN(stream, self.dskLengthN)

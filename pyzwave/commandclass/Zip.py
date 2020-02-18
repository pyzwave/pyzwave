from pyzwave.const.ZW_classcmd import (
    COMMAND_CLASS_ZIP,
    COMMAND_ZIP_PACKET,
    COMMAND_ZIP_KEEP_ALIVE,
)
from pyzwave.message import Message
from pyzwave.types import (
    BitStreamReader,
    BitStreamWriter,
    flag_t,
    reserved_t,
    uint7_t,
    uint8_t,
)
from . import ZWaveMessage, registerCmdClass

registerCmdClass(COMMAND_CLASS_ZIP, "ZIP")


class HeaderExtension(dict):
    """
    Decoder type for header extensions in Command Class message ZIP_PACKET
    """

    default = {}

    def serialize(self, stream: BitStreamWriter):
        """Serialize header extension into stream"""

    @classmethod
    def deserialize(cls, stream: BitStreamReader):
        """Deserialize header extension from stream"""
        retval = {}
        extLength = stream.byte() - 1
        val = stream.value(extLength)
        for _optionType, _optionValue in cls.tlvIterator(val):
            pass
        return retval

    @staticmethod
    def tlvIterator(pkt):
        """Parse tlv from bytearray"""
        i = 0
        while i < len(pkt):
            tlvType = pkt[i]
            length = pkt[i + 1]
            tlvValue = pkt[i + 2 : i + 2 + length]
            i = i + 2 + length
            yield (tlvType, tlvValue)
        if i != len(pkt):
            raise ValueError("BAD TLV")


@ZWaveMessage(COMMAND_CLASS_ZIP, COMMAND_ZIP_KEEP_ALIVE)
class ZipKeepAlive(Message):
    """
    Command Class message COMMAND_CLASS_ZIP COMMAND_ZIP_KEEP_ALIVE
    """

    NAME = "ZIP_KEEP_ALIVE"

    attributes = (
        ("ackRequest", flag_t),
        ("ackResponse", flag_t),
        ("_", reserved_t(6)),
    )


@ZWaveMessage(COMMAND_CLASS_ZIP, COMMAND_ZIP_PACKET)
class ZipPacket(Message):
    """
    Command Class message COMMAND_CLASS_ZIP COMMAND_ZIP_PACKET
    """

    NAME = "ZIP_PACKET"

    attributes = (
        # flags 0, byte 0
        ("ackRequest", flag_t),
        ("ackResponse", flag_t),
        ("nackResponse", flag_t),
        ("nackWaiting", flag_t),
        ("nackQueueFull", flag_t),
        ("nackOptionError", flag_t),
        ("_", reserved_t(2)),
        # flags 1, byte 1
        ("headerExtIncluded", flag_t),
        ("zwCmdIncluded", flag_t),
        ("moreInformation", flag_t),
        ("secureOrigin", flag_t),
        ("_", reserved_t(4)),
        ("seqNo", uint8_t),
        ("-", reserved_t(1)),
        ("sourceEP", uint7_t),
        ("-", reserved_t(1)),
        ("destEP", uint7_t),
        ("headerExtension", HeaderExtension),
        ("command", Message),
    )

    ZIP_OPTION_EXPECTED_DELAY = 1
    ZIP_OPTION_MAINTENANCE_GET = 2
    ZIP_OPTION_MAINTENANCE_REPORT = 3

    def parse_headerExtension(
        self, stream: BitStreamReader
    ):  # pylint: disable=invalid-name
        """Parse header extension if supplied"""
        if not self.headerExtIncluded:
            return {}
        return HeaderExtension.deserialize(stream)

    def response(
        self,
        success: bool,
        nackWaiting: bool = False,
        nackQueueFull: bool = False,
        nackOptionError: bool = False,
    ) -> Message:
        """Generate an ackResponse for this messsage. Use if ackRequest is set"""
        return ZipPacket(
            ackRequest=False,
            ackResponse=success,
            nackResponse=not success,
            nackWaiting=nackWaiting,
            nackQueueFull=nackQueueFull,
            nackOptionError=nackOptionError,
            headerExtIncluded=False,
            zwCmdIncluded=False,
            moreInformation=False,
            secureOrigin=self.secureOrigin,
            seqNo=self.seqNo,
            sourceEP=self.destEP,
            destEP=self.sourceEP,
            command=None,
        )

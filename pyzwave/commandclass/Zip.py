from enum import IntEnum
from pyzwave.const.ZW_classcmd import (
    COMMAND_CLASS_ZIP,
    COMMAND_ZIP_PACKET,
    COMMAND_ZIP_KEEP_ALIVE,
)
from pyzwave.message import Message
from pyzwave.types import (
    BitStreamReader,
    BitStreamWriter,
    bits_t,
    bytes_t,
    enum_t,
    flag_t,
    int24_t,
    reserved_t,
    uint7_t,
    uint8_t,
    uint16_t,
)
from pyzwave.util import AttributesMixin
from . import ZWaveMessage, registerCmdClass
from .CommandClass import VarDictAttribute

registerCmdClass(COMMAND_CLASS_ZIP, "ZIP")


class ZIPPacketOptionData:
    """ZIP Packet Option Data"""


class IMEType(IntEnum):
    """IME Type"""

    ROUTE_CHANGED = 0x00
    TRANSMISION_TIME = 0x01
    LAST_WORKING_ROUTE = 0x02
    RSSI = 0x03
    ACK_CHANNEL = 0x04
    TRANSMIT_CHANNEL = 0x05
    ROUTING_SCHEME = 0x06
    ROUTING_ATTEMPTS = 0x07
    LAST_FAILED_LINK = 0x08


class IMEValue:
    """Default base type for IME values"""

    @classmethod
    def load(cls, value):
        """Load IME value"""
        return cls(cls.deserialize(value))  # pylint: disable=no-member


class IMEAckChannel(IMEValue, uint8_t):
    """Ack channel"""


class IMELastWorkingRoute(IMEValue, AttributesMixin):
    """Last working route"""

    class Speed(IntEnum):
        """Communication speed"""

        SPEED_9_6_KBIT_S = 0x01
        SPEED_40_KBIT_S = 0x02
        SPEED_100_KBIT_S = 0x03

    attributes = (
        ("repeater1", uint8_t),
        ("repeater2", uint8_t),
        ("repeater3", uint8_t),
        ("repeater4", uint8_t),
        ("speed", enum_t(Speed, uint8_t)),
    )

    @classmethod
    def load(cls, value):
        lastWorkingRoute = cls()
        lastWorkingRoute.parseAttributes(value)
        return lastWorkingRoute


class IMERouteChanged(IMEValue, uint8_t):
    """Route changed"""


class IMETransmitChannel(IMEValue, uint8_t):
    """Transmit channel"""


class IMETransmissionTime(IMEValue, uint16_t):
    """Transmission time"""


class IMEUnknownValue(IMEValue, bytes_t):
    """Type not yet implemented"""


IME_MAPPING = {
    IMEType.ROUTE_CHANGED: IMERouteChanged,
    IMEType.TRANSMISION_TIME: IMETransmissionTime,
    IMEType.LAST_WORKING_ROUTE: IMELastWorkingRoute,
    IMEType.ACK_CHANNEL: IMEAckChannel,
    IMEType.TRANSMIT_CHANNEL: IMETransmitChannel,
}


class ZIPPacketOptionMaintenanceReport(
    ZIPPacketOptionData, VarDictAttribute(IMEType, IMEValue)
):
    """Maintenance report"""

    @classmethod
    def deserialize(cls, stream: BitStreamReader):
        """Deserialize ZIP Maintenance Report"""
        retval = {}
        while stream.bytesLeft():
            imeType = IMEType(stream.byte())
            length = stream.byte()
            imeVal = stream.value(length)
            typeCls = IME_MAPPING.get(imeType, IMEUnknownValue)
            retval[imeType] = typeCls.load(BitStreamReader(imeVal))
        return retval


class ZIPPacketOptionEncapsulationFormatInfo(ZIPPacketOptionData, AttributesMixin):
    """Zip packet option encapsulation format info"""

    attributes = (
        ("security2SecurityClass", bits_t(8)),
        ("-", reserved_t(7)),
        ("crc16", flag_t),
    )


class ZIPPacketOptionExpectedDelay(ZIPPacketOptionData, int24_t):
    """Zip Packet option expexted delay"""


class ZIPPacketOptionType(IntEnum):
    """ZIP Packet option type"""

    EXPECTED_DELAY = 1
    MAINTENANCE_GET = 2
    MAINTENANCE_REPORT = 3
    ENCAPSULATION_FORMAT_INFORMATION = 4
    ZWAVE_MULTICAST_ADDRESSING = 5


class ZIPPacketOption(AttributesMixin):
    """ZIP Packet option"""

    attributes = (
        ("critical", flag_t),
        ("optionType", enum_t(ZIPPacketOptionType, uint7_t)),
        ("optionData", ZIPPacketOptionData),
    )

    def parse_optionData(self, stream: BitStreamReader):  # pylint: disable=invalid-name
        """Parse attribute optionData"""
        clsType = ZIPPacketOptionData
        length = stream.byte()
        data = stream.value(length)
        if self.optionType == ZIPPacketOptionType.MAINTENANCE_REPORT:
            clsType = ZIPPacketOptionMaintenanceReport
        elif self.optionType == ZIPPacketOptionType.ENCAPSULATION_FORMAT_INFORMATION:
            clsType = ZIPPacketOptionEncapsulationFormatInfo
        elif self.optionType == ZIPPacketOptionType.EXPECTED_DELAY:
            clsType = ZIPPacketOptionExpectedDelay
        cls = clsType()
        if hasattr(cls, "parseAttributes"):
            cls.parseAttributes(BitStreamReader(data))
        elif hasattr(cls, "__setstate__"):
            data = clsType.deserialize(BitStreamReader(data))
            cls.__setstate__(data)
        else:
            value = clsType.deserialize(BitStreamReader(data))
            return clsType(value)
        return cls


class HeaderExtension(VarDictAttribute(ZIPPacketOptionType, ZIPPacketOptionData)):
    """
    Decoder type for header extensions in Command Class message ZIP_PACKET
    """

    default = {}

    @property
    def expectedDelay(self) -> int:
        """Returns the expected delay for sleeping nodes"""
        return self.get(ZIPPacketOptionType.EXPECTED_DELAY, 0)

    def serialize(self, stream: BitStreamWriter):
        """Serialize header extension into stream"""

    @classmethod
    def deserialize(cls, stream: BitStreamReader):
        """Deserialize header extension from stream"""
        retval = {}
        extLength = stream.byte() - 1
        reader = BitStreamReader(stream.value(extLength))
        while reader.bytesLeft() > 0:
            option = ZIPPacketOption()
            option.parseAttributes(reader)
            retval[option.optionType] = option.optionData
        return retval


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

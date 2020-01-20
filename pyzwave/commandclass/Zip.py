import struct

from pyzwave.const.ZW_classcmd import COMMAND_CLASS_ZIP, COMMAND_ZIP_PACKET
from pyzwave.message import Message
from pyzwave.types import (
    BitStreamReader,
    BitStreamWriter,
    bits_t,
    flag_t,
    reserved_t,
    uint8_t,
)
from . import ZWaveMessage, registerCmdClass

registerCmdClass(COMMAND_CLASS_ZIP, "ZIP")


@ZWaveMessage(COMMAND_CLASS_ZIP, COMMAND_ZIP_PACKET)
class ZipPacket(Message):
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
        ("sourceEP", uint8_t),  # TODO, actually only 7 bits
        ("destEP", uint8_t),  # TODO, 7 bits + bit address
        ("command", Message),
    )

    ZIP_OPTION_EXPECTED_DELAY = 1
    ZIP_OPTION_MAINTENANCE_GET = 2
    ZIP_OPTION_MAINTENANCE_REPORT = 3

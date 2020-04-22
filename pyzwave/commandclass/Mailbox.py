from enum import IntEnum, IntFlag

from pyzwave.message import Message

from pyzwave.types import (
    BitStreamReader,
    bits_t,
    bytes_t,
    enum_t,
    flag_t,
    IPv6,
    reserved_t,
    uint3_t,
    uint8_t,
    uint16_t,
)
from . import ZWaveMessage, ZWaveCommandClass
from .CommandClass import CommandClass

COMMAND_CLASS_MAILBOX = 0x69
MAILBOX_CONFIGURATION_GET = 0x01
MAILBOX_CONFIGURATION_SET = 0x02
MAILBOX_CONFIGURATION_REPORT = 0x03
MAILBOX_QUEUE = 0x04
MAILBOX_WAKEUP_NOTIFICATION = 0x05
MAILBOX_NODE_FAILING = 0x06
MAILBOX_QUEUE_FLUSH = 0x07


class Mode(IntFlag):
    """Mailbox mode enum"""

    DISABLE_MAILBOX = 0x00
    ENABLE_MAILBOX_SERVICE = 0x01
    ENABLE_MAILBOX_PROXY_FORWARDING = 0x02


Mode_t = enum_t(Mode, uint3_t)  # pylint: disable=invalid-name


@ZWaveMessage(COMMAND_CLASS_MAILBOX, MAILBOX_CONFIGURATION_GET)
class ConfigurationGet(Message):
    """Command Class message COMMAND_CLASS_MAILBOX MAILBOX_CONFIGURATION_GET"""

    NAME = "CONFIGURATION_GET"


@ZWaveMessage(COMMAND_CLASS_MAILBOX, MAILBOX_CONFIGURATION_REPORT)
class ConfigurationReport(Message):
    """Command Class message COMMAND_CLASS_MAILBOX MAILBOX_CONFIGURATION_REPORT"""

    NAME = "CONFIGURATION_REPORT"
    attributes = (
        ("-", reserved_t(3)),
        ("supportedModes", bits_t(2)),
        ("mode", Mode_t),
        ("mailboxCapacity", uint16_t),
        ("forwardingDestinationIPv6Address", IPv6),
        ("udpPortNumber", uint16_t),
    )


@ZWaveMessage(COMMAND_CLASS_MAILBOX, MAILBOX_NODE_FAILING)
class NodeFailing(Message):
    """Command Class message COMMAND_CLASS_MAILBOX MAILBOX_NODE_FAILING"""

    NAME = "NODE_FAILING"
    attributes = (("queueHandle", uint8_t),)

    @staticmethod
    def parse_queueHandle(stream: BitStreamReader):  # pylint: disable=invalid-name
        """Parse queueHandle from raw bitstream"""
        # According to the docs queueHandle should be an uint8_t value
        # just like the other similar messages. But for unknown reason zipgateway
        # sends this like an ipv6 address (at least version 7.11.01)
        print("Node failing", stream.remaining(advance=False))
        if stream.bytesLeft() == 16:
            stream.advance(8 * 15)
        return stream.byte()


@ZWaveMessage(COMMAND_CLASS_MAILBOX, MAILBOX_QUEUE)
class Queue(Message):
    """Command Class message COMMAND_CLASS_MAILBOX MAILBOX_QUEUE"""

    class Operation(IntEnum):
        """Mailbox Queue Operation enum"""

        PUSH = 0x00
        POP = 0x01
        WAITING = 0x02
        PING = 0x03
        ACK = 0x04
        NACK = 0x05
        QUEUE_FULL = 0x06

    NAME = "QUEUE"
    attributes = (
        ("-", reserved_t(4)),
        ("last", flag_t),
        ("operation", enum_t(Operation, uint3_t)),
        ("queueHandle", uint8_t),
        ("mailboxEntry", bytes_t),
    )


@ZWaveMessage(COMMAND_CLASS_MAILBOX, MAILBOX_QUEUE_FLUSH)
class QueueFlush(Message):
    """Command Class message COMMAND_CLASS_MAILBOX MAILBOX_QUEUE_FLUSH"""

    NAME = "QUEUE_FLUSH"
    attributes = (("queueHandle", uint8_t),)


@ZWaveMessage(COMMAND_CLASS_MAILBOX, MAILBOX_CONFIGURATION_SET)
class ConfigurationSet(Message):
    """Command Class message COMMAND_CLASS_MAILBOX MAILBOX_CONFIGURATION_SET"""

    NAME = "CONFIGURATION_SET"
    attributes = (
        ("-", reserved_t(5)),
        ("mode", Mode_t),
        ("forwardingDestinationIPv6Address", IPv6),
        ("udpPortNumber", uint16_t),
    )


@ZWaveMessage(COMMAND_CLASS_MAILBOX, MAILBOX_WAKEUP_NOTIFICATION)
class WakeupNotification(Message):
    """Command Class message COMMAND_CLASS_MAILBOX MAILBOX_WAKEUP_NOTIFICATION"""

    NAME = "WAKEUP_NOTIFICATION"
    attributes = (("queueHandle", uint8_t),)


# pylint: disable=attribute-defined-outside-init
@ZWaveCommandClass(COMMAND_CLASS_MAILBOX)
class Mailbox(CommandClass):
    """Command Class MAILBOX"""

    NAME = "MAILBOX"

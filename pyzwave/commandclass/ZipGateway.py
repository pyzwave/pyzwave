from pyzwave.const.ZW_classcmd import (
    COMMAND_APPLICATION_NODE_INFO_SET,
    COMMAND_CLASS_ZIP_GATEWAY,
    GATEWAY_MODE_GET,
    GATEWAY_MODE_REPORT,
    GATEWAY_MODE_SET,
    GATEWAY_PEER_SET,
    UNSOLICITED_DESTINATION_SET,
)
from pyzwave.message import Message
from pyzwave.types import (
    bits_t,
    bytes_t,
    IPv6,
    reserved_t,
    uint16_t,
    uint8_t,
)
from . import ZWaveMessage, registerCmdClass

registerCmdClass(COMMAND_CLASS_ZIP_GATEWAY, "ZIP_GATEWAY")


@ZWaveMessage(COMMAND_CLASS_ZIP_GATEWAY, COMMAND_APPLICATION_NODE_INFO_SET)
class ApplicationNodeInfoSet(Message):
    """
    Command Class Message COMMAND_CLASS_ZIP_GATEWAY COMMAND_APPLICATION_NODE_INFO_SET
    """

    NAME = "COMMAND_APPLICATION_NODE_INFO_SET"
    attributes = (("commandClasses", bytes_t),)


@ZWaveMessage(COMMAND_CLASS_ZIP_GATEWAY, GATEWAY_MODE_GET)
class GatewayModeGet(Message):
    """
    Command Class Message COMMAND_CLASS_ZIP_GATEWAY GATEWAY_MODE_GET
    """

    NAME = "GATEWAY_MODE_GET"


@ZWaveMessage(COMMAND_CLASS_ZIP_GATEWAY, GATEWAY_MODE_REPORT)
class GatewayModeReport(Message):
    """
    Command Class Message COMMAND_CLASS_ZIP_GATEWAY GATEWAY_MODE_REPORT
    """

    NAME = "GATEWAY_MODE_REPORT"
    attributes = (("mode", uint8_t),)


@ZWaveMessage(COMMAND_CLASS_ZIP_GATEWAY, GATEWAY_MODE_SET)
class GatewayModeSet(Message):
    """
    Command Class Message COMMAND_CLASS_ZIP_GATEWAY GATEWAY_MODE_SET
    """

    NAME = "GATEWAY_MODE_SET"
    attributes = (("mode", uint8_t),)


@ZWaveMessage(COMMAND_CLASS_ZIP_GATEWAY, GATEWAY_PEER_SET)
class GatewayPeerSet(Message):
    """
    Command Class Message COMMAND_CLASS_ZIP_GATEWAY GATEWAY_PEER_SET
    """

    NAME = "GATEWAY_PEER_SET"
    attributes = (
        ("peerProfile", uint8_t),
        ("ipv6", IPv6),
        ("port", uint16_t),
        ("-", reserved_t(2)),
        ("peerNameLength", bits_t(6)),
    )


@ZWaveMessage(COMMAND_CLASS_ZIP_GATEWAY, UNSOLICITED_DESTINATION_SET)
class UnsolicitedDestinationSet(Message):
    """
    Command Class Message COMMAND_CLASS_ZIP_GATEWAY UNSOLICITED_DESTINATION_SET
    """

    NAME = "UNSOLICITED_DESTINATION_SET"
    attributes = (
        ("unsolicitedIPv6Destination", IPv6),
        ("port", uint16_t),
    )
